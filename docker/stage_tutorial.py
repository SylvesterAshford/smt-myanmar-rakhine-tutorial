#!/usr/bin/env python3
"""Headless equivalent of the notebook's STEP 2 + STEP 5 setup cells, run at
image build time. Reads the embedded asset bundle out of the notebook itself
(single source of truth), downloads the Myanmar-Rakhine corpus, generates the
syllable dictionary and placeholder images."""
import base64
import collections
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request

TUT = "/home/ye/exp/SMT-NMT_tutorial"
NB = f"{TUT}/SMT-Tutorial-for-AI-Class-1.ipynb"

for d in [TUT, f"{TUT}/data", f"{TUT}/scripts", f"{TUT}/syl_normalizer",
          f"{TUT}/tool", f"{TUT}/error-examples", f"{TUT}/pbsmt", "/home/lar/tool"]:
    os.makedirs(d, exist_ok=True)

# 1) asset files from the notebook's embedded bundle (STEP 2)
nb = json.load(open(NB, encoding="utf-8"))
step2 = next(c for c in nb["cells"]
             if c["cell_type"] == "code" and "EMBEDDED_B64" in "".join(c["source"]))
b64 = re.search(r'EMBEDDED_B64 = "([^"]+)"', "".join(step2["source"])).group(1)
files = json.loads(base64.b64decode(b64))
for rel, content in files.items():
    p = os.path.join(TUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    if rel.rsplit(".", 1)[-1] in ("pl", "sh", "py"):
        os.chmod(p, 0o755)
print(f"wrote {len(files)} asset files")

# 2) Myanmar-Rakhine corpus (STEP 5) — with retries: docker build networks flake
import time

def fetch(url, dest, attempts=5):
    for i in range(attempts):
        try:
            urllib.request.urlretrieve(url, dest)
            return
        except Exception as e:
            if i == attempts - 1:
                raise
            print(f"retry {i + 1} for {url}: {e}")
            time.sleep(3 * (i + 1))

base = "https://raw.githubusercontent.com/ye-kyaw-thu/MTRSS/master/pbsmt/data/"
for split in ["train", "dev", "test"]:
    for lang in ["my", "rk"]:
        fetch(base + f"{split}.{lang}", f"{TUT}/data/{split}.{lang}")
for f in glob.glob(TUT + "/data/*"):
    b = open(f, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    open(f, "wb").write(b)
print("corpus downloaded:",
      {os.path.basename(f): sum(1 for _ in open(f, encoding="utf-8"))
       for f in sorted(glob.glob(TUT + "/data/*"))})

# 3) syllable dictionary from the Burmese training side
seg = subprocess.run([sys.executable, f"{TUT}/tool/sylbreak.py",
                      "--input", f"{TUT}/data/train.my", "--separator", " "],
                     capture_output=True, text=True).stdout
cnt = collections.Counter(seg.split())
with open(f"{TUT}/syl_normalizer/final_syl_dictionary_13Feb2024.sorted.txt",
          "w", encoding="utf-8") as f:
    for syl, c in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])):
        f.write(f"{syl} {c}\n")
print("dictionary entries:", len(cnt))

# 4) placeholder images for the display cells
from PIL import Image, ImageDraw
for p, label in [
    (f"{TUT}/syl_normalizer/syl_normalizer.png", "syl_normalizer algorithm (placeholder image)"),
    (f"{TUT}/error-examples/GIZA-error.png", "GIZA++ mkcls error (placeholder image)"),
    (f"{TUT}/error-examples/graph.1.my-rk.png", "my-rk EMS pipeline graph (placeholder image)"),
    (f"{TUT}/error-examples/graph.1.my-rk-2ndtime.png", "my-rk EMS graph, 2nd run (placeholder image)"),
]:
    img = Image.new("RGB", (820, 180), (245, 245, 247))
    ImageDraw.Draw(img).text((24, 80), label, fill=(70, 70, 80))
    img.save(p)

print("staging complete")
