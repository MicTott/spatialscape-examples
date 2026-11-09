"""Write files.tsv: the Allen Brain Cell Atlas files this app needs, with sizes, md5 and URLs, from the release
manifest (https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/releases/20250531/manifest.json).

    python files_from_manifest.py [manifest.json]

Kept: the whole-brain MERFISH log2 matrix and its metadata; the CCF parcellation per MERFISH cell; the taxonomy;
the published UMAPs (whole brain and per neighbourhood); the 10x cell metadata; the log2 matrices of WMB-10Xv2,
WMB-10Xv3 and WMB-10XMulti. Left out: the raw-count twins of every matrix and the MapMyCells statistics.
"""
import json
import sys
import urllib.request
from pathlib import Path

MANIFEST = "https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/releases/20250531/manifest.json"
KEEP = {
    "MERFISH-C57BL6J-638850": lambda p: "raw" not in p,
    "MERFISH-C57BL6J-638850-CCF": lambda p: True,
    "WMB-taxonomy": lambda p: True,
    "WMB-neighborhoods": lambda p: True,
    "WMB-10X": lambda p: p[0] == "metadata",
    "WMB-10Xv2": lambda p: "log2" in p,
    "WMB-10Xv3": lambda p: "log2" in p,
    "WMB-10XMulti": lambda p: "log2" in p,
}
# a path is e.g. ("expression_matrices", "WMB-10Xv2-CTXsp", "log2", "files", "h5ad"): the matrix kind sits third from the end


def files(node, path=()):
    if isinstance(node, dict):
        if "url" in node and "size" in node:
            yield path, node
        else:
            for k, v in node.items():
                yield from files(v, path + (k,))


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else MANIFEST
    text = Path(src).read_text() if Path(src).exists() else urllib.request.urlopen(src).read().decode()
    listing = json.loads(text)["file_listing"]
    out = HERE / "files.tsv"
    rows = [(d, f["relative_path"], f["size"], f["file_hash"], f["url"]) for d, keep in KEEP.items() for p, f in files(listing[d]) if keep(p)]
    with open(out, "w") as fh:
        fh.write("directory\trelative_path\tsize_bytes\tmd5\turl\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    print(f"{out}: {len(rows)} files, {sum(r[2] for r in rows) / 1e9:.1f} GB")


if __name__ == "__main__":
    main()
