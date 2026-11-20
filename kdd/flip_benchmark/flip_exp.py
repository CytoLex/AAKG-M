"""Third, independent source: does the differential representation travel to FLIP2?

FLIP2 publishes 16 predefined splits over 7 datasets. Only the fixed-length substitution libraries admit a
wild-type, and of those only the ones with a train set large enough to fit a head are used here:
amylase (4 splits), ired (1), trpb (2 of its 3; one_to_many has 304 training rows).

The wild type is inferred as the per-position modal residue, which the reconnaissance showed to be reliable
(modal support 0.99, median distance to it 2-4 residues).

Each split trains three models on the released train set, selects nothing on test, and reports Spearman:
  A  ridge on mean-pooled ESM-2 embeddings of the mutant sequence  (a standard FLIP-style baseline)
  B  ridge on the differential features                            (features without the neural head)
  C  our MLP encoder on the differential features                  (the paper's model)
"""
import os, glob, gzip, collections, itertools, json
import numpy as np, pandas as pd, torch, torch.nn as nn
from scipy.stats import spearmanr
from transformers import AutoTokenizer, AutoModel

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
D = f"{R}/aakg-flip2-1120"
OUT = f"{D}/feats"; os.makedirs(OUT, exist_ok=True)
LAYERS = (20, 30, 33); WIN = 4; device = "cuda"
SPLITS = [("amylase", s) for s in ("one_to_many","close_to_far","far_to_close","by_mutation")] + \
         [("ired","two_to_many"), ("trpb","two_to_many"), ("trpb","by_position")]
torch.set_grad_enabled(False)

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a - a.mean()) / (a.std() + 1e-12)
def sp(a, b): return spearmanr(a, b).correlation

LOCAL = [f"{R}/cytolex-aakg-s-1030-v1/models/esm2_t33_650M_v2",
         f"{R}/cytolex-aakg-s-1030-v1/models/esm2_t33_650M_UR50D"]
def load_model():
    last = None
    for c in LOCAL + ["facebook/esm2_t33_650M_UR50D"]:
        try:
            tok = AutoTokenizer.from_pretrained(c)
            m = AutoModel.from_pretrained(c, torch_dtype=torch.float16)
            print("LOADED:", c, flush=True); return tok, m.to(device).eval()
        except Exception as e:
            print("cannot load", c, str(e)[:100], flush=True); last = e
    raise last

tok, model = load_model()

def infer_wt(seqs):
    L = len(seqs[0])
    return "".join(collections.Counter(s[i] for s in seqs).most_common(1)[0][0] for i in range(L))

def features_for(seqs, wt, path):
    """Differential features plus the mean-pooled baseline vector, streamed to disk."""
    L = len(wt)
    diff = np.zeros((len(seqs), 9*1280), dtype=np.float32)
    mean = np.zeros((len(seqs), 1280), dtype=np.float32)
    # embed the wild type once
    enc = tok([wt], return_tensors="pt", truncation=True, max_length=1024)
    enc = {k: v.to(device) for k, v in enc.items()}
    hs = model(**enc, output_hidden_states=True).hidden_states
    wt_h = {ly: hs[ly][0, 1:1+L].float().cpu().numpy() for ly in LAYERS}
    del hs; torch.cuda.empty_cache()
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    B = 16
    for k in range(0, len(order), B):
        idx = order[k:k+B]
        enc = tok([seqs[i] for i in idx], return_tensors="pt", padding=True,
                  truncation=True, max_length=1024)
        enc = {k2: v.to(device) for k2, v in enc.items()}
        hs = model(**enc, output_hidden_states=True).hidden_states
        mask = enc["attention_mask"].bool().cpu()
        for j, i in enumerate(idx):
            Ln = int(mask[j].sum()) - 2
            mh = {ly: hs[ly][j, 1:1+Ln].float().cpu().numpy() for ly in LAYERS}
            mut_pos = [p for p in range(min(L, Ln)) if seqs[i][p] != wt[p]]
            f = []
            for ly in LAYERS:
                Wt, M = wt_h[ly], mh[ly]
                if mut_pos:
                    w_win = np.mean([Wt[max(0,p-WIN):min(len(Wt),p+WIN+1)].mean(0) for p in mut_pos], axis=0)
                    m_win = np.mean([M[max(0,p-WIN):min(len(M),p+WIN+1)].mean(0) for p in mut_pos], axis=0)
                else:
                    w_win = Wt.mean(0); m_win = M.mean(0)
                f += [w_win, m_win, m_win - w_win]
            diff[i] = np.concatenate(f)
            mean[i] = mh[30].mean(0)
        del hs; torch.cuda.empty_cache()
    np.savez_compressed(path, diff=diff, mean=mean)
    return path

def ridge(Xtr, ytr, Xte, lam=1.0):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-8
    Xtr = (Xtr-mu)/sd; Xte = (Xte-mu)/sd
    ym = ytr.mean(); ys = ytr.std() + 1e-8
    A = Xtr.T @ Xtr + lam*np.eye(Xtr.shape[1])
    w = np.linalg.solve(A, Xtr.T @ ((ytr-ym)/ys))
    return (Xte @ w)*ys + ym

class Head(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d,256), nn.ReLU(), nn.Dropout(0.1),
                                 nn.Linear(256,64), nn.ReLU(), nn.Linear(64,1))
    def forward(self,x): return self.net(x).squeeze(-1)

def train_mlp(Xtr, ytr, Xte, seeds=3, epochs=250):
    torch.set_grad_enabled(True)
    mu, sd = Xtr.mean(0), Xtr.std(0)+1e-8
    Xt = torch.tensor((Xtr-mu)/sd, dtype=torch.float32, device=device)
    Xe = torch.tensor((Xte-mu)/sd, dtype=torch.float32, device=device)
    yt = torch.tensor(ytr, dtype=torch.float32, device=device)
    yt = (yt-yt.mean())/(yt.std()+1e-8)
    acc = torch.zeros(len(Xte), device=device)
    for s in range(seeds):
        torch.manual_seed(s)
        m = Head(Xtr.shape[1]).to(device)
        opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-4)
        lf = nn.MSELoss()
        for _ in range(epochs):
            opt.zero_grad(); lf(m(Xt), yt).backward(); opt.step()
        acc += m(Xe).detach()
    torch.set_grad_enabled(False)
    return (acc/seeds).cpu().numpy()

results = {}
for ds, nm in SPLITS:
    d = pd.read_csv(f"{D}/{ds}__{nm}.csv.gz")
    val = d["validation"].astype(str).str.lower().eq("true")
    tr = d.loc[d["set"].eq("train") & ~val]
    te = d.loc[d["set"].eq("test") & ~val]
    if len(tr) < 1000 or len(te) < 200:
        print(f"skip {ds}/{nm}: train {len(tr)} test {len(te)}", flush=True); continue
    seqs, idx = [], {}
    allseq = pd.concat([tr, te]).sequence.tolist()
    uniq = {s: i for i, s in enumerate(dict.fromkeys(allseq))}
    ulist = list(uniq)
    path = f"{OUT}/{ds}__{nm}.npz"
    if not os.path.exists(path):
        wt = infer_wt(allseq)
        features_for(ulist, wt, path)
    z0 = np.load(path)
    di, me = z0["diff"], z0["mean"]
    tri = np.array([uniq[s] for s in tr.sequence]); tei = np.array([uniq[s] for s in te.sequence])
    ytr, yte = tr.target.to_numpy(), te.target.to_numpy()
    rA = sp(ridge(me[tri], ytr, me[tei]), yte)
    rB = sp(ridge(di[tri], ytr, di[tei]), yte)
    rC = sp(train_mlp(di[tri], ytr, di[tei]), yte)
    results[f"{ds}/{nm}"] = {"n_train": int(len(tr)), "n_test": int(len(te)),
                             "ridge_meanpool": float(rA), "ridge_diff": float(rB), "mlp_diff": float(rC)}
    print(f"{ds}/{nm:14s} train {len(tr):6d} test {len(te):6d} | meanpool {rA:+.4f} | "
          f"diff-ridge {rB:+.4f} | diff-MLP {rC:+.4f}", flush=True)

json.dump(results, open(f"{D}/flip_results.json", "w"), indent=2)
if results:
    import statistics as st
    for k in ("ridge_meanpool","ridge_diff","mlp_diff"):
        vals = [v[k] for v in results.values()]
        print(f"mean {k:14s} {np.mean(vals):+.4f} (sd {np.std(vals):.4f})", flush=True)
print("FLIP DONE", flush=True)
