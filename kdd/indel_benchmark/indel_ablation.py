"""Does the indel encoder's lead depend on distillation from the published models?

For alpha in {0.0, 0.9, 1.0} train the same head, report the per-assay Spearman and the four-expert fusion.
alpha = 0 uses only the measured target, alpha = 1 uses only the teacher consensus (no labels).
"""
import os, glob, json, itertools, numpy as np, torch, torch.nn as nn
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
W = f"{R}/indel-benchmark-1119"
device = "cuda"
torch.set_grad_enabled(False)

def z(a):
    a = np.asarray(a, dtype=np.float64)
    return (a - a.mean()) / (a.std() + 1e-12)

class Head(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 256), nn.ReLU(), nn.Dropout(0.1),
                                 nn.Linear(256, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x): return self.net(x).squeeze(-1)

def train_student(X, y, teacher, fold, alpha, seeds=3, epochs=250):
    torch.set_grad_enabled(True)
    oof = np.zeros(len(y))
    for k in range(5):
        tr, te = fold != k, fold == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        Xtr = torch.tensor((X[tr]-mu)/sd, dtype=torch.float32, device=device)
        Xte = torch.tensor((X[te]-mu)/sd, dtype=torch.float32, device=device)
        ytr = torch.tensor(y[tr], dtype=torch.float32, device=device)
        ttr = torch.tensor(teacher[tr], dtype=torch.float32, device=device)
        ytr = (ytr - ytr.mean()) / (ytr.std() + 1e-8)
        ttr = (ttr - ttr.mean()) / (ttr.std() + 1e-8)
        acc = torch.zeros(int(te.sum()), device=device)
        for s in range(seeds):
            torch.manual_seed(s)
            m = Head(X.shape[1]).to(device)
            opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-4)
            lf = nn.MSELoss()
            for _ in range(epochs):
                opt.zero_grad()
                loss = (1-alpha)*lf(m(Xtr), ytr) + alpha*lf(m(Xtr), ttr)
                loss.backward(); opt.step()
            acc += m(Xte).detach()
        oof[te] = (acc/seeds).cpu().numpy()
        del Xtr, Xte, ytr, ttr, acc
        torch.cuda.empty_cache()
    torch.set_grad_enabled(False)
    return oof

def sp(a, b): return spearmanr(a, b).correlation

data = []
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    z0 = np.load(f, allow_pickle=True)
    X, y, fold, P = z0["X"], z0["y"], z0["fold"], z0["P"]
    ok = np.isfinite(y); X, y, fold, P = X[ok], y[ok], fold[ok], P[ok]
    if len(y) < 60: continue
    data.append({"id": os.path.basename(f)[:-4], "X": X, "y": y, "fold": fold, "P": P})
n = len(data)
print("assays:", n, flush=True)
G4 = np.array([w for w in itertools.product(np.linspace(0,1,11), repeat=4) if abs(sum(w)-1) < 1e-9])
print("grid points:", len(G4), flush=True)

def fusion(cols):
    S = np.empty((len(G4), n))
    for gi, w in enumerate(G4):
        for i in range(n):
            S[gi, i] = sp(sum(a*b for a, b in zip(w, cols[i])), data[i]["y"])
    nested = np.empty(n)
    for i in range(n):
        others = (S.sum(axis=1) - S[:, i]) / (n-1)
        nested[i] = S[int(np.argmax(others)), i]
    return float(nested.mean()), float(S.max(axis=0).mean())

out = {}
base3 = [[z(d["P"][:, j]) for j in range(3)] for d in data]
for alpha in (0.0, 0.5, 0.9, 1.0):
    studs = []
    oofs = []
    for d in data:
        teacher = np.mean([z(d["P"][:, j]) for j in range(3)], axis=0)
        oof = train_student(d["X"], d["y"], teacher, d["fold"], alpha)
        oofs.append(oof); studs.append(sp(oof, d["y"]))
    studs = np.array(studs)
    cols4 = [c + [z(o)] for c, o in zip(base3, oofs)]
    nc, orc = fusion(cols4)
    out[str(alpha)] = {"student": float(studs.mean()), "nested_4expert": nc, "oracle_4expert": orc}
    print(f"ALPHA {alpha}: student {studs.mean():.4f} | 4-expert nested {nc:.4f} oracle {orc:.4f}", flush=True)

# reference: the three-expert pool
S = np.empty((66, n))
G3 = np.array([w for w in itertools.product(np.linspace(0,1,11), repeat=3) if abs(sum(w)-1) < 1e-9])
for gi, w in enumerate(G3):
    for i in range(n):
        S[gi, i] = sp(sum(a*b for a, b in zip(w, base3[i])), data[i]["y"])
nested3 = np.empty(n)
for i in range(n):
    others = (S.sum(axis=1) - S[:, i]) / (n-1); nested3[i] = S[int(np.argmax(others)), i]
out["3expert"] = {"nested": float(nested3.mean()), "oracle": float(S.max(axis=0).mean())}
print(f"3-expert reference: nested {nested3.mean():.4f} oracle {S.max(axis=0).mean():.4f}", flush=True)
json.dump(out, open(f"{W}/out/ablation.json", "w"), indent=2)
print("ABLATION DONE", flush=True)
