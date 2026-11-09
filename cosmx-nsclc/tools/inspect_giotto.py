"""Print the structure of the paper's Giotto object (an .RData saved from R), read with spatialscape's own R reader,
to find the slot that holds the cell-type calls. Diagnostic only; prepare.py reads what this found.

    srun --mem=32G --time=0:30:00 python inspect_giotto.py
"""
import time
from pathlib import Path

from spatialscape.rdsread import read_rda

HERE = Path(__file__).resolve().parents[1]  # this dataset's folder
PATH = next((HERE / "raw" / "giotto").rglob("SMI_Giotto_Object.RData"))  # inside a folder with spaces in its name


def peek(x, depth=0, maxd=3, name=""):
    pad = "  " * depth
    kind = type(x).__name__
    if isinstance(x, dict):
        keys = list(x.keys())
        print(pad + f"{name}: dict({len(keys)}) {keys[:14]}")
        if depth < maxd:
            for k in keys[:14]:
                peek(x[k], depth + 1, maxd, str(k))
    elif isinstance(x, (list, tuple)):
        print(pad + f"{name}: {kind} len={len(x)}")
        if x and depth < maxd:
            peek(x[0], depth + 1, maxd, "[0]")
    elif hasattr(x, "__dict__") and not hasattr(x, "shape"):
        d = vars(x)
        print(pad + f"{name}: {kind} fields={list(d)[:12]}")
        if depth < maxd:
            for k in list(d)[:12]:
                peek(d[k], depth + 1, maxd, "." + k)
    else:
        shape = getattr(x, "shape", None)
        tail = "" if shape is not None else str(x)[:80]
        print(pad + f"{name}: {kind} {shape if shape is not None else ''} {tail}")


t0 = time.time()
objs = read_rda(PATH)
print("objects:", list(objs), f"({time.time() - t0:.0f} s)")
for k, v in objs.items():
    peek(v, 0, 3, k)


# the cell metadata in detail: one data.table per modality, columns and a few values
def names_of(x):
    n = x.get("attributes", {}).get("names") if isinstance(x, dict) else None
    return list(n["data"]) if isinstance(n, dict) else None


gem = objs["gem"]["attributes"]
meta = gem["cell_metadata"]
print("\ncell_metadata entries:", names_of(meta))
for nm, entry in zip(names_of(meta) or [], meta["data"]):
    cols = names_of(entry)
    print(f"  {nm}: columns {cols}")
    if isinstance(entry.get("data"), list):
        for c, col in zip(cols or [], entry["data"]):
            vals = col.get("data") if isinstance(col, dict) else None
            lv = col.get("attributes", {}).get("levels", {}).get("data") if isinstance(col, dict) and isinstance(col.get("attributes"), dict) and isinstance(col["attributes"].get("levels"), dict) else None
            print(f"     {c}: {type(vals).__name__} n={len(vals) if hasattr(vals, '__len__') else ''} first={list(vals[:3]) if hasattr(vals, '__getitem__') else vals} levels={lv[:8] if lv is not None else None}")
print("\ncell_ID first:", list(gem["cell_ID"]["data"][:3]), "spatial_locs names:", names_of(gem["spatial_locs"]))
sl = gem["spatial_locs"]["data"][0]
print("spatial_locs[0] columns:", names_of(sl), [list(c["data"][:2]) if isinstance(c, dict) and hasattr(c.get("data"), "__getitem__") else c for c in sl["data"][:4]])
