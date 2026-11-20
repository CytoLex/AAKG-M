"""One protocol for the whole second-benchmark section, with stability estimates.

Unification: every indel number uses the 65 assays with a complete released-fold join (the 226k-variant AAV
library excluded), and the reference constant is fitted nested on the other assays rather than on the whole
panel. Stability: the split-half analysis is repeated over independent random half-splits, and the encoder
is trained with more seeds, so both arrive with a spread rather than a point.
"""
import os, glob, json, itertools, numpy as np, pandas as pd, torch, torch.nn as nn
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
W = f"{R}/indel-benchmark-1119"
device = "cuda"
torch.set_grad_enabled(False)
SEEDS = 5
SPLITS = 10

def z(a):
    a = np.asarray(a, dtype=np.float64)
    return (a - a.mean()) / (a.std() + 1e-12)

def sp(a, b):
    return spearmanr(a, b).correlation

class Head(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(), nn.Dropout(0.1),
                                 nn.Linear(256, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x): return self.net(x).squeeze(-1)

def train_student(X, y, teacher, fold, alpha, seeds, epochs=250):
    torch.set_grad_enabled(True)
    oof = np.zeros(len(y))
    for k in range(5):
        tr, te = fold != k, fold == k
        if te.sum() < 5: continue
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        Xtr = torch.tensor((X[tr]-mu)/sd, dtype=torch.float32, device=device)
        Xte = torch.tensor((X[te]-mu)/sd, dtype=torch.float32, device=device)
        ytr = torch.tensor(y[tr], dtype=torch.float32, device=device)
        ttr = torch.tensor(teacher[tr], dtype=torch.float32, device=device)
        ytr = (ytr-ytr.mean())/(ytr.std()+1e-8); ttr = (ttr-ttr.mean())/(ttr.std()+1e-8)
        acc = torch.zeros(int(te.sum()), device=device)
        for s in range(seeds):
            torch.manual_seed(s)
            m = Head(X.shape[1]).to(device)
            opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-4)
            lf = nn.MSELoss()
            for _ in range(epochs):
                opt.zero_grad()
                ((1-alpha)*lf(m(Xtr), ytr) + alpha*lf(m(Xtr), ttr)).backward()
                opt.step()
            acc += m(Xte).detach()
        oof[te] = (acc/seeds).cpu().numpy()
        del Xtr, Xte, ytr, ttr, acc; torch.cuda.empty_cache()
    torch.set_grad_enabled(False)
    return oof

# ---------- load: 65 assays, released folds ----------
data = []
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    aid = os.path.basename(f)[:-4]
    bench = pd.read_csv(f"{W}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag = f"{W}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo = pd.read_csv(frag)[["mutated_sequence", "fold_random_5"]]
    m = bench.reset_index().merge(fo, on="mutated_sequence", how="left").sort_values("index")
    if m.fold_random_5.isna().any(): continue
    z0 = np.load(f, allow_pickle=True)
    X, y, P = z0["X"], z0["y"], z0["P"]
    if len(y) != len(bench): continue
    ok = np.isfinite(y)
    data.append({"id": aid, "X": X[ok], "y": y[ok],
                 "fold": m.fold_random_5.to_numpy().astype(np.int8)[ok], "P": P[ok]})
n = len(data)
print(f"assays: {n} | variants: {sum(len(d['y']) for d in data)}", flush=True)

G3 = np.array([w for w in itertools.product(np.linspace(0,1,11), repeat=3) if abs(sum(w)-1) < 1e-9])
G4 = np.array([w for w in itertools.product(np.linspace(0,1,11), repeat=4) if abs(sum(w)-1) < 1e-9])
base3 = [[z(d["P"][:, j]) for j in range(3)] for d in data]

def nested_and_oracle(cols, G):
    S = np.empty((len(G), n))
    for gi, w in enumerate(G):
        for i in range(n):
            S[gi, i] = sp(sum(a*b for a, b in zip(w, cols[i])), data[i]["y"])
    nested = np.empty(n)
    for i in range(n):
        others = (S.sum(axis=1) - S[:, i]) / (n-1)
        nested[i] = S[int(np.argmax(others)), i]
    return float(nested.mean()), float(S.max(axis=0).mean())

out = {"n_assays": n, "seeds_encoder": SEEDS, "splits": SPLITS}

# ---------- split-half under the unified protocol ----------
# Reference for both halves is the nested constant: weights fitted on the OTHER assays, so the comparison
# is against the same object the headline table uses.
W_CONST = []
for i in range(n):
    others = [q for k, q in enumerate(data) if k != i]
    best = max(G3, key=lambda w: np.mean([sp(sum(a*b for a, b in zip(w, base3[k])), q["y"])
                                          for k, q in enumerate(data) if k != i]))
    W_CONST.append(best)

rng = np.random.default_rng(0)
inp, tr = [], []
for rep in range(SPLITS):
    a_g, b_g = [], []
    for i, d in enumerate(data):
        m_ = len(d["y"]); idx = rng.permutation(m_)
        A, B = idx[:m_//2], idx[m_//2:]
        XA = d["P"][A]; XB = d["P"][B]
        mu, sd = XA.mean(0), XA.std(0) + 1e-12
        XA = (XA-mu)/sd; XB = (XB-mu)/sd
        yA, yB = d["y"][A], d["y"][B]
        w = max(G3, key=lambda ww: sp(XA @ ww, yA))          # oracle weights from half A
        c = W_CONST[i]                                        # nested constant
        a_g.append(sp(XA @ w, yA) - sp(XA @ c, yA))
        b_g.append(sp(XB @ w, yB) - sp(XB @ c, yB))
    inp.append(float(np.mean(a_g))); tr.append(float(np.mean(b_g)))
out["split_half"] = {"in_place_mean": float(np.mean(inp)), "in_place_sd": float(np.std(inp)),
                     "transfer_mean": float(np.mean(tr)), "transfer_sd": float(np.std(tr)),
                     "survival": float(np.mean(tr)/np.mean(inp))}
print(f"split-half over {SPLITS} splits vs the NESTED constant: "
      f"in-place {np.mean(inp):+.4f}+-{np.std(inp):.4f} | transfer {np.mean(tr):+.4f}+-{np.std(tr):.4f} | "
      f"survival {np.mean(tr)/np.mean(inp):.0%}", flush=True)

# ---------- encoder with more seeds ----------
for alpha in (0.0, 0.9):
    per_seed, oofs = [], []
    for d in data:
        teacher = np.mean([z(d["P"][:, j]) for j in range(3)], axis=0)
        oof = train_student(d["X"], d["y"], teacher, d["fold"], alpha, SEEDS)
        oofs.append(oof)
    studs = np.array([sp(o, d["y"]) for o, d in zip(oofs, data)])
    nc, orc = nested_and_oracle([c + [z(o)] for c, o in zip(base3, oofs)], G4)
    out[f"alpha_{alpha}"] = {"student_mean": float(studs.mean()), "student_sd": float(studs.std()),
                             "student_se": float(studs.std()/np.sqrt(len(studs))),
                             "nested": nc, "oracle": orc, "headroom": orc-nc}
    print(f"ALPHA {alpha} ({SEEDS} seeds): student {studs.mean():.4f} (sd {studs.std():.4f}) | "
          f"4-expert nested {nc:.4f} oracle {orc:.4f} headroom {orc-nc:+.4f}", flush=True)

nc3, orc3 = nested_and_oracle(base3, G3)
out["three_expert"] = {"nested": nc3, "oracle": orc3, "headroom": orc3-nc3}
print(f"3-expert: nested {nc3:.4f} oracle {orc3:.4f} headroom {orc3-nc3:+.4f}", flush=True)
json.dump(out, open(f"{W}/out/unified.json", "w"), indent=2)
print("UNIFIED DONE", flush=True)
