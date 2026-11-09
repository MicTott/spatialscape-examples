"""The paper's cell-type calls, out of the Giotto object and into one small table.

The Giotto object (an .RData of 771,236 cells, read with spatialscape's own R reader, about 80 s and 20 GB) holds
the published cell types and niches in its `cell_metadata$rna` table. This writes the columns the viewer uses to
processed/cell_types.csv (cell_ID, section, fov, cell, cell_type, niche, patient) so that
prepare.py, which runs once per section, never has to open the object.

    srun --mem=32G --time=0:30:00 python celltypes.py
"""
from pathlib import Path

import pandas as pd

from spatialscape.rdsread import read_rda

HERE = Path(__file__).resolve().parent  # this dataset's folder
SRC = next((HERE / "raw" / "giotto").rglob("SMI_Giotto_Object.RData"))
DEST = HERE / "processed" / "cell_types.csv"
KEEP = ["cell_ID", "fov", "Run_Tissue_name", "slide_ID_numeric", "patient", "cell_type", "niche", "remove_flagged_cells"]


def names_of(x) -> list[str] | None:
    n = x.get("attributes", {}).get("names") if isinstance(x, dict) else None
    return list(n["data"]) if isinstance(n, dict) else None


def main() -> None:
    gem = read_rda(SRC)["gem"]["attributes"]
    meta = gem["cell_metadata"]
    rna = meta["data"][names_of(meta).index("rna")]
    cols = names_of(rna)
    table = pd.DataFrame({c: list(col["data"]) for c, col in zip(cols, rna["data"]) if c in KEEP})
    table = table.rename(columns={"Run_Tissue_name": "section"})
    parts = table["cell_ID"].str.split("_", expand=True)  # c_<slide>_<fov>_<cell>
    table["cell"] = parts[3].astype(int)
    table["fov"] = table["fov"].astype(int)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(DEST, index=False)
    print(f"{len(table):,} cells, {table['cell_type'].nunique()} cell types, {table['niche'].nunique()} niches, sections {sorted(table['section'].unique())} -> {DEST}")


if __name__ == "__main__":
    main()
