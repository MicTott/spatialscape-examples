"""Build one neighbourhood panel's expression alone and report the peak memory, before committing the whole
dataset to a rebuild. The 1.5 M-nuclei Pallium-Glut panel (7.4 billion stored values) is the one that matters.

    sbatch check_memory.sbatch          # Pallium-Glut, 100 GB
"""
import resource
import shutil
import sys
import time
from pathlib import Path

import anndata as ad
import numpy as np

from spatialscape.build import most_variable_gene
from spatialscape.expression import get_matrix, write_expression

HERE = Path(__file__).resolve().parents[1]  # this dataset's folder
panel = sys.argv[1] if len(sys.argv) > 1 else "Pallium-Glut"
src = HERE / "processed" / "tenx" / f"{panel}.h5ad"
out = HERE / "processed" / "tmp-memory-check" / panel
shutil.rmtree(out, ignore_errors=True)
out.mkdir(parents=True)


def peak_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6  # kB on Linux


t0 = time.time()
adata = ad.read_h5ad(src)
print(f"read {src.name}: {adata.shape}, nnz {adata.X.nnz:,}, {adata.X.format}; peak {peak_gb():.1f} GB after {time.time() - t0:.0f} s", flush=True)
M = get_matrix(adata, "X")
perm = np.random.default_rng(0).permutation(adata.n_obs)
res = write_expression(M, out, order=perm, log=lambda m: print(m, f"| peak {peak_gb():.1f} GB", flush=True) if "genes" in m and int(m.split()[2].split("/")[0]) % 4096 == 0 else None)
print(f"wrote {int(res.keep.sum()):,} genes; peak {peak_gb():.1f} GB; {time.time() - t0:.0f} s", flush=True)
genes = [str(g) for g in adata.var_names[res.keep]]
print(f"opening gene {most_variable_gene(M, res.keep, genes)!r}; peak {peak_gb():.1f} GB (the build's remaining step on the matrix)", flush=True)
shutil.rmtree(out, ignore_errors=True)
