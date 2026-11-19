import os, glob, time, itertools, numpy as np, pandas as pd, torch, torch.nn as nn
from transformers import AutoTokenizer, AutoModel

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
W = f"{R}/indel-benchmark-1119"
os.makedirs(f"{W}/out", exist_ok=True); os.makedirs(f"{W}/data", exist_ok=True)
SKIP = {"CAPSD_AAV2S_Sinai_2021_designed_indels"}      # 226k variants; excluded for runtime
LAYERS = (20, 30, 33); WIN = 4; device = "cuda"
MODELS = ["Embeddings_ESM1v_indels_predictions",
          "Embeddings_MSA_Transformer_indels_predictions",
          "Embeddings_Tranception_indels_predictions"]
torch.set_grad_enabled(False)

# ---------- stage 1: features ----------
LOCAL_MODEL_CANDIDATES = [
    f"{R}/cytolex-aakg-s-1030-v1/models/esm2_t33_650M_v2",
    f"{R}/cytolex-aakg-s-1030-v1/models/esm2_t33_650M_UR50D",
]

def load_model():
    """Try each staged copy; a truncated safetensors file raises on load, so fall through."""
    last = None
    for c in LOCAL_MODEL_CANDIDATES + ["facebook/esm2_t33_650M_UR50D"]:
        try:
            tok = AutoTokenizer.from_pretrained(c)
            m = AutoModel.from_pretrained(c, torch_dtype=torch.float16)
            print("LOADED:", c, flush=True)
            return tok, m.to(device).eval()
        except Exception as e:
            print(f"cannot load {c}: {str(e)[:160]}", flush=True)
            last = e
    raise last

def extract():
    tok, model = load_model()
    def embed_into(seqs, fill, wt, wt_h, batch=16):
        """Batch through the encoder and write features straight into `fill`.

        Holding every hidden state for an assay in RAM costs ~20GB on the larger libraries, which is what
        killed the previous run; this streams instead.
        """
        order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
        for k in range(0, len(order), batch):
            idx = order[k:k+batch]
            enc = tok([seqs[i] for i in idx], return_tensors="pt", padding=True,
                      truncation=True, max_length=1024)
            enc = {k2: v.to(device) for k2, v in enc.items()}
            hs = model(**enc, output_hidden_states=True).hidden_states
            mask = enc["attention_mask"].bool().cpu()
            for j, i in enumerate(idx):
                L = int(mask[j].sum()) - 2
                h = {ly: hs[ly][j, 1:1+L].float().cpu().numpy() for ly in LAYERS}
                fill[i] = feats(wt_h, h, *edit_region(wt, seqs[i]))
            del hs
            torch.cuda.empty_cache()

    def embed_one(seq):
        enc = tok([seq], return_tensors="pt", truncation=True, max_length=1024)
        enc = {k2: v.to(device) for k2, v in enc.items()}
        hs = model(**enc, output_hidden_states=True).hidden_states
        L = int(enc["attention_mask"].sum()) - 2
        return {ly: hs[ly][0, 1:1+L].float().cpu().numpy() for ly in LAYERS}

    def edit_region(wt, mut):
        n, m = len(wt), len(mut); p = 0
        while p < n and p < m and wt[p] == mut[p]: p += 1
        s = 0
        while s < n-p and s < m-p and wt[n-1-s] == mut[m-1-s]: s += 1
        return p, n-s, p, m-s
    def feats(wt_h, mut_h, a, b, c, e):
        f = []
        for ly in LAYERS:
            Wt, M = wt_h[ly], mut_h[ly]
            wlo, whi = max(0, a-WIN), min(len(Wt), b+WIN)
            mlo, mhi = max(0, c-WIN), min(len(M), e+WIN)
            w_win = Wt[wlo:whi].mean(0) if whi > wlo else Wt.mean(0)
            m_win = M[mlo:mhi].mean(0) if mhi > mlo else M.mean(0)
            f += [w_win, m_win, m_win - w_win]
        return np.concatenate(f).astype(np.float32)
    ref = pd.read_csv(f"{W}/data/DMS_indels_ref.csv").set_index("DMS_id")
    t0 = time.time()
    for f in sorted(glob.glob(f"{W}/data/DMS_ProteinGym_indels/*.csv")):
        aid = os.path.basename(f)[:-4]
        if aid in SKIP: continue
        outp = f"{W}/out/{aid}.npz"
        if os.path.exists(outp): continue
        d = pd.read_csv(f)
        src = pd.read_csv(f"{W}/data/DMS_supervised_indels_scores/fold_random_5/{aid}.csv")
        if len(src) != len(d): print("SKIP mismatch", aid); continue
        wt = ref.loc[aid, "target_seq"]; wt_h = embed_one(wt)
        muts = d.mutated_sequence.tolist()
        X = np.empty((len(muts), 9*1280), dtype=np.float32)
        embed_into(muts, X, wt, wt_h)
        rng = np.random.default_rng(1)
        fold = np.zeros(len(d), dtype=np.int8); fold[rng.permutation(len(d))] = np.arange(len(d)) % 5
        np.savez_compressed(outp, X=X, y=d.DMS_score.to_numpy(np.float32), fold=fold,
                            P=src[MODELS].to_numpy(np.float32))
        print(f"feat {aid:50s} n={len(d):6d} {time.time()-t0:7.0f}s", flush=True)

# ---------- stage 2: student + fusion ----------
class Head(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(), nn.Dropout(0.1),
                                 nn.Linear(256, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x): return self.net(x).squeeze(-1)

def train_student(X, y, teacher, fold, seeds=2, alpha=0.9, epochs=300):
    torch.set_grad_enabled(True)          # the module-level switch disables autograd for extraction
    n = len(y); oof = np.zeros(n)
    for k in range(5):
        tr = fold != k; te = fold == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        Xtr = torch.tensor((X[tr]-mu)/sd, dtype=torch.float32, device=device)
        Xte = torch.tensor((X[te]-mu)/sd, dtype=torch.float32, device=device)
        ytr = torch.tensor(y[tr], dtype=torch.float32, device=device)
        ttr = torch.tensor(teacher[tr], dtype=torch.float32, device=device)
        ymu, ysd = ytr.mean(), ytr.std() + 1e-8
        ytr_n = (ytr - ymu) / ysd; ttr_n = (ttr - ttr.mean()) / (ttr.std() + 1e-8)
        pred = torch.zeros(int(te.sum()), device=device)
        for s in range(seeds):
            torch.manual_seed(s)
            m = Head(X.shape[1]).to(device)
            opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-4)
            lossf = nn.MSELoss()
            idx = torch.tensor(tr.nonzero()[0], device=device)
            for ep in range(epochs):
                opt.zero_grad()
                out = m(Xtr)
                loss = (1-alpha)*lossf(out, ytr_n) + alpha*lossf(out, ttr_n)
                loss.backward(); opt.step()
            pred += m(Xte).detach()
        oof[te] = (pred/seeds).cpu().numpy()
    torch.set_grad_enabled(False)
    return oof

def z(a):
    a = np.asarray(a, dtype=np.float64)
    return (a - a.mean()) / (a.std() + 1e-12)

def main():
    from scipy.stats import spearmanr
    files = sorted(glob.glob(f"{W}/out/*.npz"))
    data = []
    for f in files:
        z0 = np.load(f, allow_pickle=True)
        X, y, fold, P = z0["X"], z0["y"], z0["fold"], z0["P"]
        ok = np.isfinite(y)
        X, y, fold, P = X[ok], y[ok], fold[ok], P[ok]
        if len(y) < 60:
            continue
        teacher = np.mean([z(P[:, j]) for j in range(3)], axis=0)
        oof = train_student(X, y, teacher, fold)
        data.append({"assay": os.path.basename(f)[:-4], "y": y, "P": P, "oof": oof})
        print("student", data[-1]["assay"], flush=True)

    def sp(a, b):
        return spearmanr(a, b).correlation
    n = len(data)
    base = np.array([[sp(d["P"][:, j], d["y"]) for j in range(3)] for d in data])
    stud = np.array([sp(d["oof"], d["y"]) for d in data])
    print(f"\nassays: {n}")
    print(f"published experts : {base.mean(0).round(4)}")
    print(f"our indel encoder : {stud.mean():.4f}")

    cols4 = [[z(d["P"][:, j]) for j in range(3)] + [z(d["oof"])] for d in data]
    cols3 = [[z(d["P"][:, j]) for j in range(3)] for d in data]

    def score_matrix(G, cols):
        """S[g, i] = Spearman of blend g on assay i. Computed once; the nested rule is then a row-mean."""
        S = np.empty((len(G), n))
        for gi, w in enumerate(G):
            for i in range(n):
                S[gi, i] = sp(sum(wi * c for wi, c in zip(w, cols[i])), data[i]["y"])
        return S

    out = {}
    for tag, cols in (("3-expert", cols3), ("4-expert", cols4)):
        k = len(cols[0])
        G = np.array([w for w in itertools.product(np.linspace(0, 1, 11), repeat=k)
                      if abs(sum(w) - 1) < 1e-9])
        S = score_matrix(G, cols)
        oracle = S.max(axis=0).mean()
        nested = np.empty(n)
        for i in range(n):
            others = (S.sum(axis=1) - S[:, i]) / (n - 1)
            nested[i] = S[int(np.argmax(others)), i]
        print(f"{tag}: grid {len(G):4d} | nested constant {nested.mean():.4f} "
              f"| oracle {oracle:.4f} | headroom {oracle - nested.mean():+.4f}")
        out[tag] = {"nested": float(nested.mean()), "oracle": float(oracle),
                    "headroom": float(oracle - nested.mean())}
    out["base"] = base.mean(0).tolist()
    out["student"] = float(stud.mean())
    json.dump(out, open(f"{W}/out/result.json", "w"), indent=2)
    print("\nDONE")

extract()
main()
