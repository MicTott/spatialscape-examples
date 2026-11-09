"""palette.json for dataset.yaml: the atlas's own colour for every taxonomy term and CCF parcellation, so the app
shows the same colours as the Allen Brain Cell Atlas viewer.

    python make_palette.py    ->  palette.json
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]  # this dataset's folder
TERMS = HERE / "raw/metadata/WMB-taxonomy/20231215/cluster_annotation_term.csv"
CCF = HERE / "raw/metadata/MERFISH-C57BL6J-638850-CCF/20231215/views/cell_metadata_with_parcellation_annotation.csv"


def main() -> None:
    terms = pd.read_csv(TERMS, keep_default_na=False)  # the neurotransmitter term named "NA" is a label, not a missing value
    palette = {}
    for level in ["neurotransmitter", "class", "subclass", "supertype", "cluster"]:
        rows = terms[terms["cluster_annotation_term_set_name"] == level]
        palette[level] = dict(zip(rows["name"], rows["color_hex_triplet"], strict=True))
    ccf = pd.read_csv(CCF, usecols=["parcellation_division", "parcellation_division_color", "parcellation_structure", "parcellation_structure_color"], keep_default_na=False).drop_duplicates()
    for level in ["parcellation_division", "parcellation_structure"]:
        palette[level] = dict(zip(ccf[level].astype(str), ccf[f"{level}_color"], strict=True))
    out = HERE / "palette.json"
    out.write_text(json.dumps(palette, indent=1))
    print(f"{out}: " + ", ".join(f"{k} {len(v)}" for k, v in palette.items()))


if __name__ == "__main__":
    main()
