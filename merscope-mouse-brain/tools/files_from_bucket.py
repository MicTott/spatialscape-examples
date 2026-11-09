"""Write files.tsv: what download.sh fetches from Vizgen's public bucket for the MERSCOPE mouse brain receptor map.

    python files_from_bucket.py      # lists the bucket over HTTPS, needs no credentials

The bucket (gs://vizgen-mouse-brain-map, 1.7 TB) holds three coronal slices with three replicates each. We take the
first replicate of each slice and, of its 14 mosaic images (DAPI and polyT at seven z planes, 11 GB each), the two
at z3: the cell table, the cell-by-gene matrix, every transcript, the 1,120 cell-boundary files and the
micron-to-mosaic transform are small beside them. One line per file: slice, path in the bucket, bytes, md5 (base64).
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

BUCKET = "vizgen-mouse-brain-map"
DATASETS = ["Slice1/Replicate1", "Slice2/Replicate1", "Slice3/Replicate1"]
IMAGES = ["mosaic_DAPI_z3.tif", "mosaic_polyT_z3.tif", "micron_to_mosaic_pixel_transform.csv"]


def objects(prefix: str) -> list[dict]:
    url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o?maxResults=1000&prefix={urllib.parse.quote(prefix, safe='')}"
    items, token = [], None
    while True:
        page = json.load(urllib.request.urlopen(url + (f"&pageToken={token}" if token else "")))
        items += page.get("items", [])
        token = page.get("nextPageToken")
        if not token:
            return items


def wanted(name: str) -> bool:
    if "/images/" in name:
        return name.split("/")[-1] in IMAGES
    return True  # cell_by_gene.csv, cell_metadata.csv, detected_transcripts.csv, cell_boundaries/*.hdf5


rows = []
for ds in DATASETS:
    for o in objects(f"BrainReceptorShowcase/{ds}/"):
        if wanted(o["name"]):
            rows.append((ds.replace("/", "_"), o["name"], o["size"], o.get("md5Hash", "")))
out = HERE / "files.tsv"
out.write_text("dataset\tpath\tbytes\tmd5_base64\n" + "".join("\t".join(r) + "\n" for r in rows))
total = sum(int(r[2]) for r in rows)
print(f"{len(rows)} files, {total / 1e9:.1f} GB -> {out}")
