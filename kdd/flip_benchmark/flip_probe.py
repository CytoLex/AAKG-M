"""What is actually in FLIP2's splits: sizes, target ranges, and whether the WT can be inferred."""
import os, glob, gzip, io, collections
import numpy as np, pandas as pd, urllib.request

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
D = f"{R}/aakg-flip2-1120"
os.makedirs(D, exist_ok=True)
BASE = "https://flip.protein.properties/assets/splits"
SPLITS = {
    "amylase": ["one_to_many", "close_to_far", "far_to_close", "by_mutation"],
    "ired": ["two_to_many"],
    "nucb": ["two_to_many"],
    "trpb": ["one_to_many", "two_to_many", "by_position"],
    "hydro": ["three_to_many", "low_to_high", "to_P06241", "to_P0A9X9", "to_P01053"],
    "rhomax": ["by_wild_type"],
    "pdz3": ["single_to_double"],
}
for ds, names in SPLITS.items():
    for nm in names:
        f = f"{D}/{ds}__{nm}.csv.gz"
        if os.path.exists(f):
            continue
        try:
            urllib.request.urlretrieve(f"{BASE}/{ds}/{nm}.csv.gz", f)
        except Exception as e:
            print("FAIL", ds, nm, str(e)[:80])

print(f"{'split':34s} {'rows':>7s} {'train':>7s} {'test':>7s} {'uniq seq':>9s} {'len':>5s} {'target range':>22s}")
for f in sorted(glob.glob(f"{D}/*.csv.gz")):
    d = pd.read_csv(f)
    tr = (d["set"].eq("train") & ~d["validation"].astype(str).str.lower().eq("true")).sum()
    te = d["set"].eq("test").sum()
    lens = d["sequence"].str.len()
    tmin, tmax = d["target"].min(), d["target"].max()
    name = os.path.basename(f)[:-7]
    print(f"{name:34s} {len(d):7d} {tr:7d} {te:7d} {d.sequence.nunique():9d} {lens.mode().iloc[0]:5d} "
          f"{tmin:>10.3f}..{tmax:<10.3f}")

# can a WT be inferred for the substitution-style sets?
print("\nWT inference (per-position modal residue) and how far sequences sit from it:")
for f in sorted(glob.glob(f"{D}/*.csv.gz")):
    d = pd.read_csv(f)
    if d["sequence"].str.len().nunique() > 1:
        print(f"  {os.path.basename(f)[:-7]:32s} variable length -> not a substitution library")
        continue
    seqs = d["sequence"].tolist()
    L = len(seqs[0])
    wt = "".join(collections.Counter(s[i] for s in seqs).most_common(1)[0][0] for i in range(L))
    dist = np.array([sum(a != b for a, b in zip(s, wt)) for s in seqs])
    print(f"  {os.path.basename(f)[:-7]:32s} L={L:4d} modal-residue support={np.mean([collections.Counter(s[i] for s in seqs).most_common(1)[0][1]/len(seqs) for i in range(L)]):.3f} "
          f"| distance to inferred WT: median {int(np.median(dist))}, max {int(dist.max())}")
