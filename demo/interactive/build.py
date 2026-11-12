#!/usr/bin/env python3
"""Build the clickable concept demo page for Shot List Coverage.

Reads the shot list, the expected results, and the photo manifest from
../shot-list, ../expected and ../generated. Writes index.html and the
downscaled photos in img/. Nothing in the page is typed by hand except the
layout text: every shot, status, frame and reason comes from those files.

    python3 demo/interactive/build.py

Needs Python with Pillow.
"""
import csv
import json
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent
IMG = HERE / "img"

NAMES = {"Ana": "Ana Rivera", "Daniel": "Daniel Okoro",
         "Grandma Rosa": "Rosa Rivera", "Maya": "Maya Chen"}
# Objects are listed only when the client's line names them.
OBJECT_WORDS = ["ring", "flowers", "welcome sign", "glasses", "cake", "topper",
                "place card", "menu card", "plate", "string lights",
                "dessert table", "front door", "house"]


def read_shot_list():
    shots, section, window = [], None, None
    for line in (DEMO / "shot-list/rivera-okoro-shot-list.md").read_text().splitlines():
        m = re.match(r"## (.+?) \((.+)\)", line)
        if m:
            section, window = m.group(1), m.group(2)
            continue
        m = re.match(r"(\d+)\. (.+?)( \*)?$", line)
        if m:
            text = m.group(2)
            quoted = re.findall(r'"([^"]+)"', text)
            plain = re.sub(r'"[^"]+"', "", text)
            people = [k for k in NAMES if re.search(r"\b%s\b" % k, plain)]
            objects = [w for w in OBJECT_WORDS if re.search(r"\b%s\b" % w, plain.lower())]
            shots.append({"n": int(m.group(1)), "text": text, "must": bool(m.group(3)),
                          "section": section, "window": window,
                          "people": [NAMES[p] for p in people],
                          "visibleText": quoted, "objects": objects})
    return shots


def read_expected(name):
    with open(DEMO / "expected" / name, newline="") as f:
        return {int(r["shot"]): r for r in csv.DictReader(f)}


def read_manifest():
    with open(DEMO / "generated/manifest.csv", newline="") as f:
        return [{"file": r["file"], "time": r["capture_time"][11:16],
                 "shot": int(r["shot"]) if r["shot"] else None,
                 "role": r["role"], "content": r["content"]}
                for r in csv.DictReader(f)]


def main():
    shots = read_shot_list()
    full, edge = read_expected("expected-full.csv"), read_expected("expected-edge.csv")
    photos = read_manifest()
    assert len(shots) == 20 and len(photos) == 53
    for s in shots:
        assert s["text"] == full[s["n"]]["text"], s
        assert s["must"] == (full[s["n"]]["must_have"] == "yes"), s
        s["status"] = full[s["n"]]["expected_status"]
        s["reason"] = full[s["n"]]["reason"]
        s["edgeStatus"] = edge[s["n"]]["expected_status"]
        s["edgeReason"] = edge[s["n"]]["reason"]

    IMG.mkdir(exist_ok=True)
    for p in photos:
        out = IMG / p["file"]
        if not out.exists():
            im = Image.open(DEMO / "generated/photos" / p["file"]).convert("RGB")
            im.thumbnail((480, 480))
            im.save(out, "JPEG", quality=72, optimize=True)

    data = {"shots": shots, "photos": photos,
            "edgeRemoved": ["IMG_2027.jpg", "IMG_2030.jpg", "IMG_2032.jpg"]}
    html = (HERE / "template.html").read_text()
    html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (HERE / "index.html").write_text(html)
    size = sum(f.stat().st_size for f in IMG.iterdir()) + len(html.encode())
    print("index.html written; payload %.1f MB" % (size / 1e6))


if __name__ == "__main__":
    main()
