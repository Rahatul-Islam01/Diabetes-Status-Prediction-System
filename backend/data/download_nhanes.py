"""Download NHANES 2021-2023 (August 2021-August 2023) XPT data files from official CDC source."""
import os
import requests

BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "raw")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

FILES = [
    "DEMO_L",
    "BMX_L",
    "BPXO_L",
    "GHB_L",
    "GLU_L",
    "DIQ_L",
    "PAQ_L",
    "SMQ_L",
    "ALQ_L",
    "SLQ_L",
]

for name in FILES:
    url = f"{BASE}/{name}.xpt"
    dest = os.path.join(OUT, f"{name}.xpt")
    if os.path.exists(dest):
        print(f"Already exists: {name}")
        continue
    print(f"Downloading {name} ...")
    r = requests.get(url, timeout=120)
    print(f"  status={r.status_code} size={len(r.content)}")
    if r.status_code == 200:
        with open(dest, "wb") as f:
            f.write(r.content)
    else:
        print(f"  FAILED: {r.text[:200]}")

print("Done.")
