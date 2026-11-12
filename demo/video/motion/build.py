#!/usr/bin/env python3
"""Write the HyperFrames project for the Shot List Coverage motion video.

Every shot, status, file name and reason on screen is read from
../../shot-list, ../../expected and ../../generated. The narration is the
existing set in ../narration (copied to assets/audio). Scene timing follows
the narration clip lengths and the pauses inside them.

    python3 demo/video/motion/build.py      # writes index.html and compositions/
    cd demo/video/motion && npx hyperframes check && npx hyperframes render
"""
import csv
import html
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent.parent
COMP = HERE / "compositions"

# ---------------------------------------------------------------- data
def shot_list():
    shots, section, window = [], None, None
    for line in (DEMO / "shot-list/rivera-okoro-shot-list.md").read_text().splitlines():
        m = re.match(r"## (.+?) \((.+)\)", line)
        if m:
            section, window = m.group(1), m.group(2)
            continue
        m = re.match(r"(\d+)\. (.+?)( \*)?$", line)
        if m:
            shots.append({"n": int(m.group(1)), "text": m.group(2), "must": bool(m.group(3)),
                          "section": section, "window": window})
    return shots


def expected(name):
    with open(DEMO / "expected" / name, newline="") as f:
        return {int(r["shot"]): r for r in csv.DictReader(f)}


with open(DEMO / "generated/manifest.csv", newline="") as f:
    PHOTOS = [{"file": r["file"], "time": r["capture_time"][11:16],
               "shot": int(r["shot"]) if r["shot"] else None, "role": r["role"]}
              for r in csv.DictReader(f)]
SHOTS = shot_list()
FULL, EDGE = expected("expected-full.csv"), expected("expected-edge.csv")
for s in SHOTS:
    assert s["text"] == FULL[s["n"]]["text"]
    s["status"] = FULL[s["n"]]["expected_status"]
assert len(SHOTS) == 20 and len(PHOTOS) == 53
N_MUST = sum(s["must"] for s in SHOTS)
COUNT = {k: sum(s["status"] == k for s in SHOTS) for k in ("covered", "weak", "missing")}
EDGE_REMOVED = ["IMG_2027.jpg", "IMG_2030.jpg", "IMG_2032.jpg"]
S10 = [p for p in PHOTOS if p["shot"] == 10]
S10_OPEN = [p for p in S10 if p["role"] == "match"]
S10_CLOSED = [p for p in S10 if p["role"] == "closed-eyes"]
assert sorted(p["file"] for p in S10_OPEN) == EDGE_REMOVED
assert EDGE[10]["expected_status"] == "weak"
ALBUM = [next(p for p in PHOTOS if p["shot"] == s["n"] and p["role"] == "match")
         for s in SHOTS if s["status"] == "covered"]
MUST_MISSING = [s for s in SHOTS if s["must"] and s["status"] != "covered"]
TOAST = [p for p in PHOTOS if "17:00" <= p["time"] < "17:30"]

# ---------------------------------------------------------------- timing
NARR = [9.492, 6.530, 7.800, 7.575, 17.280, 11.100, 8.359, 7.512, 7.300]
LEAD = 0.5
SLOTS = [10.4, 7.4, 8.7, 8.5, 18.2, 12.0, 9.3, 8.4, 9.9]
STARTS = [round(sum(SLOTS[:i]), 2) for i in range(9)]
TOTAL = round(sum(SLOTS), 2)

e = html.escape

CSS = """
#root { position: absolute; inset: 0; color: #eaf0f4; font-family: 'Inter', sans-serif; }
.stage { position: absolute; inset: 0; }
.abs { position: absolute; }
.disp { font-family: 'Outfit', sans-serif; font-weight: 700; letter-spacing: -0.02em; }
.mono { font-family: 'JetBrains Mono', monospace; }
.tag { font-family: 'JetBrains Mono', monospace; font-size: 28px; letter-spacing: 0.06em; text-transform: uppercase; color: #8fa0ae; }
.pill { display: inline-block; font-weight: 700; border-radius: 999px; padding: 6px 18px; font-size: 24px; }
.covered { color: #6fd19c; background: #12382a; }
.weak { color: #f0c36a; background: #3d2f0c; }
.missing { color: #ff9b93; background: #45191a; }
.frame { position: absolute; background: #05080b; padding: 8px 8px 30px; border-radius: 4px; box-shadow: 0 10px 30px rgba(0,0,0,.45); }
.frame img { display: block; width: 100%; height: 100%; object-fit: cover; }
.frame span { position: absolute; left: 8px; bottom: 4px; font-family: 'JetBrains Mono', monospace; font-size: 18px; color: #dfe6ec; }
.panel { position: absolute; background: #162029; border: 2px solid #2f3c48; border-radius: 14px; }
.paper { position: absolute; background: #f3f1ea; color: #17212b; border-radius: 6px; box-shadow: 0 20px 60px rgba(0,0,0,.5); }
.w { display: inline-block; }
"""


def scene(i, body, script):
    sid = "s%d" % i
    return """<template>
  <style>%s</style>
  <div id="root" data-composition-id="%s" data-width="1920" data-height="1080">
    <div id="%s-stage" class="clip stage" data-start="0" data-duration="%s" data-track-index="0">
%s
    </div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      const END = %s;
%s
      window.__timelines["%s"] = tl;
    })();
  </script>
</template>
""" % (CSS, sid, sid, SLOTS[i - 1], body, SLOTS[i - 1], script, sid)


def words(text, cls, pid):
    return "".join('<span class="w %s" id="%s-%d">%s</span> ' % (cls, pid, k, e(w))
                   for k, w in enumerate(text.split()))


def frame(pid, p, x, y, w, extra="", label=True):
    h = round(w * 0.667)
    if not label:
        return ('<div class="frame %s" id="%s" data-layout-ignore style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;padding-bottom:8px">'
                '<img src="assets/photos/%s" alt=""></div>' % (extra, pid, x, y, w + 16, h + 16, p["file"]))
    return ('<div class="frame %s" id="%s" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
            '<img src="assets/photos/%s" alt=""><span data-layout-ignore>%s</span></div>'
            % (extra, pid, x, y, w + 16, h + 38, p["file"], p["file"]))


def ticks(pid, x, y, w=30, gap=8):
    out = []
    for k, s in enumerate(SHOTS):
        out.append('<div class="abs %s-t" id="%s-%d" data-st="%s" style="left:%dpx;top:%dpx;width:%dpx;height:10px;border-radius:5px;background:#33414e"></div>'
                   % (pid, pid, k, s["status"], x + k * (w + gap), y, w))
    return "".join(out)


TICK_JS = """
      document.querySelectorAll(".%(p)s-t").forEach((el, k) => {
        const c = { covered: "#6fd19c", weak: "#f0c36a", missing: "#ff8f86" }[el.dataset.st];
        tl.fromTo(el, { opacity: 0, scaleX: 0.2 }, { opacity: 1, scaleX: 1, duration: 0.3, ease: "power4.out" }, %(t0)s + k * 0.04);
        tl.to(el, { backgroundColor: c, duration: 0.18, ease: "power2.out" }, %(t1)s + k * 0.06);
      });
"""
OUT_JS = """
      tl.to("#%s-stage > *", { opacity: 0, filter: "blur(10px)", duration: 0.28, ease: "power3.in" }, END - 0.3);
"""


# ---------------------------------------------------------------- scene 1: title
def s1():
    sheet = []
    pick = PHOTOS[::3][:18]
    for k, p in enumerate(pick):
        c, r = k % 6, k // 6
        sheet.append(frame("s1-f%d" % k, p, 40 + c * 330, 60 + r * 330, 290, "s1-f", label=False))
    body = """
      <div class="abs" id="s1-sheet" style="left:-60px;top:20px;width:2040px;height:1040px">%s</div>
      <div class="abs" id="s1-veil" style="inset:0;background:radial-gradient(ellipse at 50%% 46%%, rgba(13,19,24,.94) 0%%, rgba(13,19,24,.86) 45%%, rgba(13,19,24,.62) 100%%)"></div>
      <div class="abs disp" id="s1-title" style="left:0;right:0;top:330px;text-align:center;font-size:168px;line-height:1">%s</div>
      %s
      <div class="abs" id="s1-sub" style="left:0;right:0;top:590px;text-align:center;font-size:52px;color:#c7d2db">A UGOS Skill for photographers</div>
      <div class="abs" style="left:0;right:0;top:720px;text-align:center">
        <span class="pill mono" id="s1-c1" style="font-size:28px;color:#f5e3a3;background:#3a300f;margin:0 10px">Concept preview</span>
        <span class="pill mono" id="s1-c2" style="font-size:28px;color:#f5e3a3;background:#3a300f;margin:0 10px">Made with AI-generated photos</span>
      </div>
""" % ("".join(sheet), words("Shot List Coverage", "s1-w", "s1-w"), ticks("s1k", 584, 540))
    js = """
      tl.fromTo(".s1-f", { opacity: 0, scale: 0.86 }, { opacity: 0.55, scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.04 }, 0);
      tl.fromTo("#s1-sheet", { x: 40, rotation: -5 }, { x: -70, rotation: -5, duration: END, ease: "none" }, 0);
      tl.fromTo(".s1-w", { opacity: 0, filter: "blur(14px)", scale: 1.12 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power4.out", stagger: 0.11 }, 0.45);
%s
      tl.fromTo("#s1-sub", { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.5, ease: "expo.out" }, 2.45);
      tl.fromTo("#s1-c1", { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }, 5.4);
      tl.fromTo("#s1-c2", { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }, 7.3);
%s""" % (TICK_JS % {"p": "s1k", "t0": 1.2, "t1": 3.0}, OUT_JS % "s1")
    return scene(1, body, js)


# ---------------------------------------------------------------- scene 2: problem
def s2():
    lines = "".join('<div class="s2-l" style="font-size:27px;line-height:50px;white-space:nowrap">%d. %s%s</div>'
                    % (s["n"], e(s["text"]), " <b>*</b>" if s["must"] else "") for s in SHOTS[:10])
    rot = [-9, 6, -3, 11, -7, 4, -12, 8, 2, -5, 9, -8, 5, -2, 10, -6, 3, -10, 7, -4, 12, -1, 6, -9]
    pile = []
    for k, p in enumerate(PHOTOS[:48:2]):
        x = 1000 + (k * 137) % 520
        y = 130 + (k * 211) % 430
        pile.append(frame("s2-p%d" % k, p, x, y, 300, "s2-p", label=False))
    body = """
      <div class="paper" id="s2-paper" style="left:130px;top:150px;width:720px;height:640px;padding:40px 46px">
        <div class="mono" style="font-size:22px;letter-spacing:.08em;color:#566573;margin-bottom:14px">CLIENT SHOT LIST</div>%s
      </div>
      <div class="abs" id="s2-pile" style="inset:0">%s</div>
      <div class="abs disp" id="s2-q" style="left:0;right:0;top:400px;text-align:center;font-size:132px;line-height:1">%s</div>
""" % (lines, "".join(pile), words("Did you get every shot?", "s2-w", "s2-w"))
    js = """
      const rot = %s;
      tl.fromTo("#s2-paper", { opacity: 0, x: -260, rotation: -7 }, { opacity: 1, x: 0, rotation: -2.5, duration: 0.6, ease: "expo.out" }, 0.2);
      tl.fromTo(".s2-l", { opacity: 0 }, { opacity: 1, duration: 0.2, stagger: 0.05, ease: "power2.out" }, 0.5);
      document.querySelectorAll(".s2-p").forEach((el, k) => {
        tl.fromTo(el, { opacity: 0, scale: 1.5, rotation: rot[k] * 2.2, y: -120 }, { opacity: 1, scale: 1, rotation: rot[k], y: 0, duration: 0.34, ease: "power4.out" }, 2.6 + k * 0.085);
      });
      tl.to(["#s2-paper", "#s2-pile"], { opacity: 0, filter: "blur(16px)", scale: 0.94, duration: 0.3, ease: "power3.in" }, 5.05);
      tl.fromTo(".s2-w", { opacity: 0, filter: "blur(12px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out", stagger: 0.14 }, 5.4);
      tl.fromTo("#s2-w-3", { color: "#eaf0f4" }, { color: "#62c3e4", duration: 0.2 }, 6.0);
%s""" % (json.dumps(rot), OUT_JS % "s2")
    return scene(2, body, js)


# ---------------------------------------------------------------- scene 3: the shot list
def s3():
    cols, y, col = [[], []], [0, 0], 0
    sections = []
    for s in SHOTS:
        if s["section"] not in sections:
            sections.append(s["section"])
            if len(sections) == 4:
                col = 1
            cols[col].append('<div class="abs mono s3-h" style="left:0;top:%dpx;font-size:22px;letter-spacing:.06em;color:#566573;white-space:nowrap">%s · %s</div>'
                             % (y[col], e(s["section"]).upper(), e(s["window"])))
            y[col] += 40
        mark = '<div class="abs s3-hl" style="left:-12px;top:%dpx;width:650px;height:44px;background:#ffd84d;border-radius:4px"></div>' % (y[col] + 2) if s["must"] else ""
        cols[col].append('%s<div class="abs s3-l %s" style="left:0;top:%dpx;font-size:28px;line-height:48px;white-space:nowrap"><span class="mono" style="font-size:24px;color:#566573;display:inline-block;width:50px">%d.</span>%s</div>'
                         % (mark, "s3-m" if s["must"] else "s3-n", y[col], s["n"], e(s["text"])))
        y[col] += 48
        if SHOTS.index(s) + 1 < 20 and SHOTS[SHOTS.index(s) + 1]["section"] != s["section"]:
            y[col] += 22
    body = """
      <div class="paper" id="s3-paper" style="left:120px;top:90px;width:1500px;height:790px">
        <div class="abs disp" style="left:60px;top:36px;font-size:44px">Rivera-Okoro engagement party</div>
        <div class="abs" style="left:60px;top:120px;width:660px;height:640px">%s</div>
        <div class="abs" style="left:790px;top:120px;width:660px;height:640px">%s</div>
      </div>
      <div class="abs" id="s3-c1" style="left:1650px;top:200px;width:230px;text-align:center">
        <div class="disp" id="s3-n1" style="font-size:150px;line-height:1">0</div><div class="tag">shots</div></div>
      <div class="abs" id="s3-c2" style="left:1650px;top:520px;width:230px;text-align:center">
        <div class="disp" id="s3-n2" style="font-size:150px;line-height:1;color:#ffd84d">0</div><div class="tag">must-have</div></div>
""" % ("".join(cols[0]), "".join(cols[1]))
    js = """
      tl.fromTo("#s3-paper", { opacity: 0, scale: 0.8, rotation: -2.5 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.55, ease: "expo.out" }, 0.05);
      tl.fromTo(".s3-h", { opacity: 0 }, { opacity: 1, duration: 0.25, stagger: 0.3 }, 0.4);
      tl.fromTo(".s3-l", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.26, ease: "power4.out", stagger: 0.085 }, 0.5);
      const c1 = { v: 0 }, c2 = { v: 0 };
      tl.fromTo("#s3-c1", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 2.9);
      tl.fromTo(c1, { v: 0 }, { v: %d, duration: 1.3, ease: "power2.out", onUpdate: () => { document.getElementById("s3-n1").textContent = Math.round(c1.v); } }, 2.9);
      tl.fromTo(".s3-hl", { scaleX: 0, transformOrigin: "0%% 50%%" }, { scaleX: 1, duration: 0.28, ease: "power3.out", stagger: 0.1 }, 6.5);
      tl.to(".s3-n", { opacity: 0.38, duration: 0.4, ease: "power2.inOut" }, 6.5);
      tl.fromTo("#s3-c2", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 6.5);
      tl.fromTo(c2, { v: 0 }, { v: %d, duration: 0.9, ease: "power2.out", onUpdate: () => { document.getElementById("s3-n2").textContent = Math.round(c2.v); } }, 6.5);
%s""" % (len(SHOTS), N_MUST, OUT_JS % "s3")
    return scene(3, body, js)


# ---------------------------------------------------------------- scene 4: the request
REQUEST = "Check my shot list Documents/rivera-okoro-shot-list.pdf against Photos/2026-11 Rivera-Okoro party."


def s4():
    minis = "".join('<div class="abs s4-m" style="left:250px;top:%dpx;width:90px;height:60px;border:3px solid #05080b;background:url(assets/photos/%s) center/cover"></div>'
                    % (300 + (k % 3) * 70, p["file"]) for k, p in enumerate(PHOTOS[:12]))
    body = """
      <div class="abs tag" id="s4-t1" style="left:140px;top:150px">1 · Copy the card to the NAS</div>
      <div class="abs" id="s4-card" style="left:150px;top:300px;width:170px;height:220px;background:#2f3c48;border-radius:14px 40px 14px 14px;border:3px solid #62c3e4">
        <div class="mono" style="position:absolute;left:0;right:0;top:86px;text-align:center;font-size:34px;color:#eaf0f4">CARD</div></div>
      %s
      <div class="panel" id="s4-folder" style="left:520px;top:270px;width:330px;height:290px;border-color:#62c3e4">
        <div class="mono" style="position:absolute;left:24px;top:22px;font-size:20px;color:#8fa0ae">NAS FOLDER</div>
        <div class="disp" id="s4-n" style="position:absolute;left:24px;top:70px;font-size:120px;line-height:1">0</div>
        <div style="position:absolute;left:24px;top:200px;font-size:26px;color:#c7d2db">images in the demo shoot</div></div>
      <div class="abs mono" id="s4-path" style="left:150px;top:600px;font-size:24px;color:#8fa0ae">Photos/2026-11 Rivera-Okoro party</div>
      <div class="abs tag" id="s4-t2" style="left:980px;top:150px">2 · Ask in plain words</div>
      <div class="panel" id="s4-chat" style="left:970px;top:230px;width:830px;height:600px">
        <div class="mono" style="position:absolute;left:36px;top:26px;font-size:20px;color:#f5e3a3">ILLUSTRATION · EXPECTED FLOW</div>
        <div id="s4-b1" style="position:absolute;left:36px;top:80px;width:760px;min-height:210px;background:#0b5d7a;border-radius:22px;padding:28px 32px;font-size:36px;line-height:1.35"><span id="s4-type"></span><span id="s4-caret" style="display:inline-block;width:4px;height:36px;background:#eaf0f4;margin-left:4px;vertical-align:-6px"></span></div>
        <div id="s4-b2" style="position:absolute;left:36px;top:400px;width:700px;background:#22303c;border-radius:22px;padding:26px 32px;font-size:34px;line-height:1.35">I read <b>%d shots</b>, <b>%d must-have</b>. Is this list correct?</div>
      </div>
""" % (minis, len(SHOTS), N_MUST)
    js = """
      const TEXT = %s;
      tl.fromTo(["#s4-t1", "#s4-card"], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: "expo.out", stagger: 0.08 }, 0.15);
      tl.fromTo(["#s4-folder", "#s4-path"], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: "expo.out", stagger: 0.08 }, 0.5);
      document.querySelectorAll(".s4-m").forEach((el, k) => {
        tl.fromTo(el, { opacity: 0, x: 0, scale: 0.6 }, { opacity: 1, x: 150, scale: 1, duration: 0.2, ease: "power2.out" }, 1.0 + k * 0.1);
        tl.to(el, { x: 380, opacity: 0, scale: 0.5, duration: 0.3, ease: "power3.in" }, 1.2 + k * 0.1);
      });
      const c = { v: 0 };
      tl.fromTo(c, { v: 0 }, { v: %d, duration: 1.4, ease: "power1.out", onUpdate: () => { document.getElementById("s4-n").textContent = Math.round(c.v); } }, 1.3);
      tl.fromTo(["#s4-t2", "#s4-chat"], { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.5, ease: "expo.out", stagger: 0.06 }, 2.9);
      const ty = { v: 0 };
      tl.fromTo(ty, { v: 0 }, { v: TEXT.length, duration: 3.0, ease: "none", onUpdate: () => { document.getElementById("s4-type").textContent = TEXT.slice(0, Math.round(ty.v)); } }, 3.3);
      tl.fromTo("#s4-caret", { opacity: 1 }, { opacity: 0, duration: 0.1 }, 6.35);
      tl.fromTo("#s4-b2", { opacity: 0, y: 30, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.4)" }, 6.45);
%s""" % (json.dumps(REQUEST), len(PHOTOS), OUT_JS % "s4")
    return scene(4, body, js)


# ---------------------------------------------------------------- scene 5: how it checks
def s5():
    by = {s["n"]: s for s in SHOTS}
    cues = [("Scene", by[18]["text"], 18), ("People", "Ana Rivera · Rosa Rivera", 10),
            ("Objects", "cake · topper", 11), ("Text", "“Table 4”", 15),
            ("Time", by[10]["window"], 10)]
    chips = "".join("""<div class="panel s5-cue" id="s5-cue%d" style="left:120px;top:%dpx;width:640px;height:104px">
        <div class="disp" style="position:absolute;left:28px;top:24px;font-size:44px;color:#62c3e4">%s</div>
        <div style="position:absolute;left:230px;top:20px;font-size:23px;line-height:34px;white-space:nowrap">%s</div>
        <div class="mono" style="position:absolute;left:230px;top:60px;font-size:18px;color:#8fa0ae">from shot %d</div></div>"""
                    % (k, 250 + k * 122, name, e(val), n) for k, (name, val, n) in enumerate(cues))
    tiles = []
    for k, p in enumerate(PHOTOS):
        c, r = k % 9, k // 9
        cls = "s5-t" + (" s5-toast" if p in TOAST else " s5-other") + (" s5-ten" if p["shot"] == 10 else "")
        tiles.append('<div class="abs %s" style="left:%dpx;top:%dpx;width:108px;height:72px;border:3px solid #05080b;background:url(assets/photos/%s) center/cover"></div>'
                     % (cls, c * 116, r * 80, p["file"]))
    order = S10_OPEN + S10_CLOSED
    cand, rows = [], []
    for k, p in enumerate(order):
        x = 132 + k * 282
        cand.append(frame("s5-c%d" % k, p, x, 250, 238, "s5-c"))
        closed = p["role"] == "closed-eyes"
        for r, name in enumerate(["match", "focus", "eyes", "framing"]):
            if name == "match":
                col, txt = "#6fd19c", "shows the shot"
            elif name == "eyes":
                col, txt = ("#f0c36a", "eyes closed") if closed else ("#6fd19c", "eyes open")
            else:
                col, txt = "#62c3e4", name + " checked"
            rows.append('<div class="abs mono s5-r%d" style="left:%dpx;top:%dpx;width:254px;height:48px;border-radius:8px;border:2px solid %s;color:%s;font-size:23px;line-height:44px;text-align:center">%s</div>'
                        % (r, x, 470 + r * 60, col, col, txt))
    labels = ""
    body = """
      <div class="abs" id="s5-a" style="inset:0">
        <div class="abs tag" style="left:120px;top:120px">Step 1 · Search the shoot folder for each line</div>
        <div class="abs disp" style="left:120px;top:160px;font-size:60px">Five cues from the client's own words</div>
        %s
        <div class="abs" id="s5-sheet" style="left:820px;top:250px;width:1040px;height:480px">%s
          <div class="abs" id="s5-scan" style="left:-8px;top:-10px;width:8px;height:500px;background:#62c3e4;box-shadow:0 0 30px 8px rgba(98,195,228,.6)"></div></div>
      </div>
      <div class="abs" id="s5-b" style="inset:0">
        <div class="abs tag" style="left:132px;top:120px">Step 2 · The NAS vision model checks the best frames</div>
        <div class="abs disp" style="left:132px;top:160px;font-size:60px">Shot 10 · Ana with Grandma Rosa</div>
        %s %s %s
        <div class="abs mono" id="s5-note" style="left:132px;top:730px;font-size:24px;color:#f5e3a3">Illustration of the check. Eyes open or closed is from the demo photo manifest.</div>
        <div class="abs" id="s5-res" style="left:132px;top:790px;font-size:40px">At least one good frame <span class="pill covered" style="font-size:34px;margin-left:16px">covered</span></div>
      </div>
""" % (chips, "".join(tiles), "".join(cand), "".join(rows), labels)
    js = """
      tl.fromTo("#s5-a > .tag, #s5-a > .disp", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.08 }, 0.2);
      tl.fromTo(".s5-t", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "power4.out", stagger: 0.012 }, 0.7);
      const at = [3.15, 3.95, 4.7, 5.65, 6.5];
      at.forEach((t, k) => {
        tl.fromTo("#s5-cue" + k, { opacity: 0, x: -80, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.32, ease: "power4.out" }, t);
        tl.fromTo("#s5-scan", { x: 0, opacity: 1 }, { x: 1050, opacity: 1, duration: 0.45, ease: "power2.inOut" }, t + 0.05);
      });
      tl.fromTo("#s5-scan", { opacity: 1 }, { opacity: 0, duration: 0.1 }, 7.05);
      tl.to(".s5-other", { opacity: 0.16, duration: 0.3, ease: "power2.out" }, 6.8);
      tl.to(".s5-toast:not(.s5-ten)", { opacity: 0.16, duration: 0.3, ease: "power2.out" }, 7.5);
      tl.to(".s5-ten", { borderColor: "#62c3e4", scale: 1.12, duration: 0.3, ease: "back.out(2)" }, 7.5);
      tl.to("#s5-a", { opacity: 0, filter: "blur(12px)", x: -120, duration: 0.3, ease: "power3.in" }, 8.1);
      tl.fromTo("#s5-b", { opacity: 0 }, { opacity: 1, duration: 0.05 }, 8.35);
      tl.fromTo("#s5-b > .tag, #s5-b > .disp", { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.4, ease: "expo.out", stagger: 0.06 }, 8.4);
      tl.fromTo(".s5-c", { opacity: 0, y: 80, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "expo.out", stagger: 0.07 }, 8.7);
      [12.2, 13.5, 14.65, 16.0].forEach((t, r) => {
        tl.fromTo(".s5-r" + r, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.8)", stagger: 0.05 }, t);
      });
      tl.fromTo("#s5-note", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 12.2);
      tl.fromTo("#s5-res", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }, 16.3);
      tl.to("#s5-b", { opacity: 0, filter: "blur(10px)", duration: 0.28, ease: "power3.in" }, END - 0.3);
"""
    return scene(5, body, js)


# ---------------------------------------------------------------- scene 6: the report
def s6():
    rows = []
    for k, s in enumerate(SHOTS):
        c, r = k // 10, k % 10
        rows.append("""<div class="abs s6-row" style="left:%dpx;top:%dpx;width:560px;height:44px;border-bottom:1px solid #2f3c48">
          <span class="mono" style="position:absolute;left:0;top:8px;font-size:20px;color:#8fa0ae;width:36px;text-align:right">%d</span>
          <span style="position:absolute;left:52px;top:5px;font-size:23px;white-space:nowrap;max-width:360px;overflow:hidden">%s</span>
          <span class="pill %s s6-pill s6-%s" style="position:absolute;right:0;top:5px;font-size:18px;padding:4px 14px">%s</span></div>"""
                    % (36 + c * 600, 372 + r * 44, s["n"], e(s["text"][:30] + ("…" if len(s["text"]) > 30 else "")), s["status"], s["status"], s["status"]))
    miss = "".join('<div style="font-size:32px;line-height:1.3"><b>%d. %s</b> (must-have): %s</div>' % (s["n"], e(s["text"]), s["status"]) for s in MUST_MISSING)
    ring = [p for p in PHOTOS if p["shot"] == 1 and p["role"] == "match"][:3]
    body = """
      <div class="panel" id="s6-rep" style="left:96px;top:60px;width:1250px;height:840px;overflow:hidden" data-layout-allow-overflow>
        <div class="abs mono" style="left:36px;top:24px;font-size:20px;color:#f5e3a3">EXAMPLE OF THE EXPECTED REPORT</div>
        <div class="abs disp" id="s6-h" style="left:36px;top:56px;font-size:40px;white-space:nowrap">Rivera-Okoro engagement party: shot list coverage</div>
        <div class="abs" id="s6-miss" style="left:36px;top:130px;width:1178px;height:150px;background:#45191a;border-left:10px solid #ff8f86;border-radius:0 10px 10px 0;padding:20px 28px;color:#ffd6d2">
          <div class="mono" style="font-size:20px;letter-spacing:.08em;margin-bottom:10px">MISSING MUST-HAVE SHOTS</div>%s</div>
        <div class="abs tag" id="s6-all" style="left:36px;top:310px">All shots</div>
        %s
      </div>
      <div class="abs" id="s6-sum" style="left:1390px;top:60px;width:440px">
        <div class="abs s6-cnt" style="left:0;top:0;width:140px;text-align:center"><div class="disp" id="s6-n0" style="font-size:96px;line-height:1;color:#6fd19c">0</div><div class="mono" style="font-size:20px;color:#6fd19c">covered</div></div>
        <div class="abs s6-cnt" style="left:150px;top:0;width:140px;text-align:center"><div class="disp" id="s6-n1" style="font-size:96px;line-height:1;color:#f0c36a">0</div><div class="mono" style="font-size:20px;color:#f0c36a">weak</div></div>
        <div class="abs s6-cnt" style="left:300px;top:0;width:140px;text-align:center"><div class="disp" id="s6-n2" style="font-size:96px;line-height:1;color:#ff9b93">0</div><div class="mono" style="font-size:20px;color:#ff9b93">missing</div></div>
      </div>
      <div class="panel" id="s6-det" style="left:1390px;top:230px;width:440px;height:670px">
        <div class="abs mono" style="left:24px;top:20px;font-size:18px;color:#8fa0ae">SHOT 1 · MUST-HAVE</div>
        <div class="abs disp" style="left:24px;top:48px;font-size:28px;width:400px">%s</div>
        <div class="abs mono s6-lab" style="left:24px;top:130px;font-size:20px;color:#8fa0ae">BEST FRAME</div>
        %s
        <div class="abs mono s6-lab" style="left:24px;top:434px;font-size:20px;color:#8fa0ae">TWO ALTERNATES</div>
        %s %s
        <div class="abs" style="left:24px;top:628px;font-size:20px;color:#f5e3a3;white-space:nowrap">Example frames. The NAS picks the best.</div>
      </div>
""" % (miss, "".join(rows), e(SHOTS[0]["text"]),
       frame("s6-f0", ring[0], 24, 160, 340, "s6-f"), frame("s6-f1", ring[1], 24, 464, 176, "s6-f"), frame("s6-f2", ring[2], 224, 464, 176, "s6-f"))
    js = """
      tl.fromTo("#s6-rep", { opacity: 0, y: 60, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "expo.out" }, 0.15);
      tl.fromTo("#s6-h", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out" }, 0.5);
      tl.fromTo("#s6-miss", { opacity: 0, x: -140 }, { opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }, 2.6);
      tl.fromTo("#s6-miss", { scale: 1 }, { scale: 1.02, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.inOut" }, 3.5);
      tl.fromTo("#s6-all", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 5.2);
      tl.fromTo(".s6-row", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.22, ease: "power4.out", stagger: 0.035 }, 5.3);
      tl.fromTo(".s6-pill", { opacity: 0 }, { opacity: 0.25, duration: 0.1 }, 5.5);
      tl.fromTo(".s6-cnt", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "expo.out", stagger: 0.08 }, 5.6);
      tl.to(".s6-covered", { opacity: 1, scale: 1.12, duration: 0.14, ease: "power2.out", stagger: 0.02 }, 6.45);
      tl.to(".s6-covered", { scale: 1, duration: 0.2, ease: "power2.inOut" }, 6.95);
      tl.to(".s6-missing", { opacity: 1, scale: 1.18, duration: 0.16, ease: "power2.out", stagger: 0.06 }, 8.15);
      tl.to(".s6-missing", { scale: 1, duration: 0.2, ease: "power2.inOut" }, 8.65);
      const n = [{ v: 0 }, { v: 0 }, { v: 0 }], target = [%d, %d, %d], t0 = [6.45, 7.4, 8.15];
      n.forEach((o, k) => tl.fromTo(o, { v: 0 }, { v: target[k], duration: 0.6, ease: "power2.out", onUpdate: () => { document.getElementById("s6-n" + k).textContent = Math.round(o.v); } }, t0[k]));
      tl.fromTo("#s6-det", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }, 9.0);
      tl.fromTo("#s6-f0", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.5)" }, 9.5);
      tl.fromTo(["#s6-f1", "#s6-f2"], { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.5)", stagger: 0.18 }, 10.4);
%s""" % (COUNT["covered"], COUNT["weak"], COUNT["missing"], OUT_JS % "s6")
    return scene(6, body, js)


# ---------------------------------------------------------------- scene 7: closed eyes
def s7():
    fr = []
    for k, p in enumerate(S10_OPEN):
        fr.append(frame("s7-o%d" % k, p, 120 + k * 400, 230, 340, "s7-o"))
    for k, p in enumerate(S10_CLOSED):
        fr.append(frame("s7-c%d" % k, p, 120 + k * 400, 530, 340, "s7-c"))
    body = """
      <div class="abs tag" style="left:120px;top:110px" id="s7-tag">Shot 10 · must-have · edge run from the test plan</div>
      <div class="abs disp" id="s7-h" style="left:120px;top:146px;font-size:60px">Ana with Grandma Rosa</div>
      %s
      <div class="abs mono" id="s7-lo" style="left:1340px;top:330px;font-size:26px;color:#6fd19c;width:480px">3 frames with eyes open</div>
      <div class="abs mono" id="s7-lx" style="left:1340px;top:372px;font-size:22px;color:#8fa0ae;width:480px">removed from the folder for the edge run</div>
      <div class="abs mono" id="s7-lc" style="left:1340px;top:560px;font-size:26px;color:#f0c36a;width:480px">3 frames with eyes closed</div>
      <div class="abs" id="s7-st" style="left:1340px;top:640px;width:500px">
        <div class="abs disp" id="s7-cov" style="left:0;top:0;font-size:84px;color:#6fd19c">covered</div>
        <div class="abs" id="s7-strike" style="left:-10px;top:58px;width:340px;height:10px;background:#ff8f86;border-radius:5px"></div>
        <div class="abs disp" id="s7-weak" style="left:0;top:100px;font-size:150px;color:#f0c36a;line-height:1">weak</div>
      </div>
""" % "".join(fr)
    js = """
      tl.fromTo(["#s7-tag", "#s7-h"], { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.07 }, 0.15);
      tl.fromTo(".s7-o, .s7-c", { opacity: 0, scale: 0.8, y: 40 }, { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.06 }, 0.35);
      tl.fromTo(["#s7-lo", "#s7-lc"], { opacity: 0 }, { opacity: 1, duration: 0.3, stagger: 0.1 }, 0.9);
      tl.fromTo("#s7-cov", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.6)" }, 1.1);
      tl.to(".s7-o", { opacity: 0.12, y: -30, scale: 0.94, filter: "grayscale(1)", duration: 0.4, ease: "power3.in", stagger: 0.12 }, 1.9);
      tl.fromTo("#s7-lx", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 2.2);
      tl.to("#s7-lo", { opacity: 0.4, duration: 0.3 }, 2.2);
      tl.to(".s7-c", { boxShadow: "0 0 0 6px #f0c36a, 0 10px 30px rgba(0,0,0,.45)", duration: 0.3, ease: "power2.out", stagger: 0.1 }, 2.9);
      tl.fromTo("#s7-weak", { opacity: 0, scale: 1.6, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out" }, 4.75);
      tl.fromTo("#s7-strike", { scaleX: 0, transformOrigin: "0%% 50%%" }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, 5.7);
      tl.to("#s7-cov", { opacity: 0.45, duration: 0.3 }, 5.7);
%s""" % (OUT_JS % "s7")
    return scene(7, body, js)


# ---------------------------------------------------------------- scene 8: album
def s8():
    tiles = []
    for k, p in enumerate(ALBUM):
        c, r = k % 8, k // 8
        tiles.append(frame("s8-a%d" % k, p, 40 + c * 198, 96 + r * 190, 166, "s8-a"))
    body = """
      <div class="panel" id="s8-ask" style="left:120px;top:90px;width:1100px;height:170px">
        <div class="abs mono" style="left:30px;top:20px;font-size:18px;color:#f5e3a3">ILLUSTRATION · EXPECTED FLOW</div>
        <div class="abs" style="left:30px;top:58px;font-size:34px;line-height:1.3;width:1040px">Make an album with the best frames and save this report in the shoot folder?</div></div>
      <div class="abs disp" id="s8-btn" style="left:1270px;top:110px;width:420px;height:130px;border-radius:20px;border:3px solid #62c3e4;color:#62c3e4;font-size:44px;line-height:124px;text-align:center">Album and report</div>
      <div class="abs disp" id="s8-btn2" style="left:1270px;top:110px;width:420px;height:130px;border-radius:20px;border:3px solid #62c3e4;background:#62c3e4;color:#06222d;font-size:44px;line-height:124px;text-align:center">Approved</div>
      <div class="panel" id="s8-album" style="left:120px;top:300px;width:1660px;height:480px">
        <div class="abs disp" style="left:40px;top:26px;font-size:36px;white-space:nowrap">Album · Rivera-Okoro engagement party shot list</div>
        <div class="abs mono" id="s8-cnt" style="right:40px;top:34px;font-size:26px;color:#6fd19c">0 photos</div>
        %s
      </div>
      <div class="abs mono" id="s8-file" style="left:120px;top:806px;font-size:26px;color:#c7d2db;background:#22303c;border-radius:10px;padding:12px 22px;white-space:nowrap">Saved: Rivera-Okoro engagement party shot list coverage.md</div>
      <div class="abs disp" id="s8-safe" style="left:1150px;top:796px;width:680px;text-align:right;font-size:50px;color:#6fd19c;white-space:nowrap">It never changes a photo.</div>
""" % "".join(tiles)
    js = """
      tl.fromTo(["#s8-ask", "#s8-btn"], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.08 }, 0.1);
      tl.fromTo("#s8-btn", { scale: 1 }, { scale: 0.93, duration: 0.1, ease: "power2.in" }, 1.25);
      tl.to("#s8-btn", { opacity: 0, duration: 0.08 }, 1.35);
      tl.fromTo("#s8-btn2", { opacity: 0, scale: 0.93 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }, 1.35);
      tl.fromTo("#s8-album", { opacity: 0, y: 80, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "expo.out" }, 1.7);
      const rot = [-8, 6, -4, 9, -6, 3, -9, 7, 5, -7, 8, -3, 6, -5, 4, -8];
      document.querySelectorAll(".s8-a").forEach((el, k) => {
        tl.fromTo(el, { opacity: 0, y: -260, scale: 1.5, rotation: rot[k] * 2 }, { opacity: 1, y: 0, scale: 1, rotation: 0, duration: 0.4, ease: "power4.out" }, 2.2 + k * 0.14);
      });
      const c = { v: 0 };
      tl.fromTo(c, { v: 0 }, { v: %d, duration: 16 * 0.14, ease: "none", onUpdate: () => { document.getElementById("s8-cnt").textContent = Math.round(c.v) + " photos, in shot list order"; } }, 2.4);
      tl.fromTo("#s8-file", { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: 0.4, ease: "expo.out" }, 4.7);
      tl.fromTo("#s8-safe", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out" }, 6.2);
%s""" % (len(ALBUM), OUT_JS % "s8")
    return scene(8, body, js)


# ---------------------------------------------------------------- scene 9: close
def s9():
    sheet = []
    for k, p in enumerate(ALBUM[:16] + [q for q in PHOTOS if q["role"] == "filler"][:2]):
        c, r = k % 6, k // 6
        sheet.append(frame("s9-f%d" % k, p, 40 + c * 330, 60 + r * 330, 290, "s9-f", label=False))
    lines = ["Private", "On your NAS", "Your client’s own words"]
    body = """
      <div class="abs" id="s9-sheet" style="left:-60px;top:20px;width:2040px;height:1040px">%s</div>
      <div class="abs" style="inset:0;background:radial-gradient(ellipse at 50%% 46%%, rgba(13,19,24,.95) 0%%, rgba(13,19,24,.88) 45%%, rgba(13,19,24,.66) 100%%)"></div>
      <div class="abs disp" id="s9-title" style="left:0;right:0;top:250px;text-align:center;font-size:150px;line-height:1">%s</div>
      %s
      <div class="abs" style="left:0;right:0;top:560px;text-align:center;font-size:58px;line-height:1.5">
        <div class="s9-l" style="color:#c7d2db">%s</div><div class="s9-l" style="color:#c7d2db">%s</div><div class="s9-l" style="color:#62c3e4">%s</div>
      </div>
""" % ("".join(sheet), words("Shot List Coverage", "s9-w", "s9-w"), ticks("s9k", 584, 450), *lines)
    js = """
      tl.fromTo(".s9-f", { opacity: 0 }, { opacity: 0.5, duration: 0.5, stagger: 0.03 }, 0);
      tl.fromTo("#s9-sheet", { x: -70, rotation: 4 }, { x: 40, rotation: 4, duration: END, ease: "none" }, 0);
      tl.fromTo(".s9-w", { opacity: 0, filter: "blur(14px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out", stagger: 0.12 }, 1.5);
%s
      [3.7, 4.55, 5.75].forEach((t, k) => tl.fromTo(document.querySelectorAll(".s9-l")[k], { opacity: 0, y: 24, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, t));
""" % (TICK_JS % {"p": "s9k", "t0": 1.9, "t1": 2.3})
    return scene(9, body, js)


LABEL = """<template>
  <style>#root { position: absolute; inset: 0; }</style>
  <div id="root" data-composition-id="label" data-width="1920" data-height="1080" data-no-timeline>
    <div id="label-band" class="clip" data-start="0" data-duration="%s" data-track-index="0"
         style="position:absolute;left:96px;right:96px;top:918px;height:54px;border-radius:27px;background:#3a300f;border:2px solid #6b5a1c;color:#f5e3a3;font-family:'Inter',sans-serif;font-weight:700;font-size:28px;line-height:50px;text-align:center;white-space:nowrap">
      CONCEPT PREVIEW · AI-generated photos, fictional people · Expected report shown · Not a recording on a UGREEN AI NAS
    </div>
  </div>
</template>
""" % TOTAL


def index():
    hosts = "".join("""
      <div id="s%d" data-composition-id="s%d" data-composition-src="compositions/s%d.html" data-start="%s" data-duration="%s"
           data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:%d"></div>"""
                    % (i, i, i, STARTS[i - 1], SLOTS[i - 1], i + 1) for i in range(1, 10))
    audio = "".join("""
      <audio id="vo%d" class="clip" src="assets/audio/scene%d.m4a" data-start="%s" data-duration="%s" data-track-index="3" data-volume="1"></audio>"""
                    % (i, i, round(STARTS[i - 1] + LEAD, 2), NARR[i - 1]) for i in range(1, 10))
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #0d1318; }
      #root { position: relative; width: 1920px; height: 1080px; font-family: 'Inter', sans-serif; }
      #ground { position: absolute; inset: 0; background: #0d1318;
        background-image: linear-gradient(rgba(98,195,228,.05) 2px, transparent 2px), linear-gradient(90deg, rgba(98,195,228,.05) 2px, transparent 2px);
        background-size: 96px 96px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="%s" data-width="1920" data-height="1080">
      <div id="ground"></div>%s
      <div id="label" data-composition-id="label" data-composition-src="compositions/label.html" data-start="0" data-duration="%s"
           data-track-index="2" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:50"></div>%s
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
""" % (TOTAL, hosts, TOTAL, audio)


def main():
    COMP.mkdir(exist_ok=True)
    (HERE / "assets/audio").mkdir(parents=True, exist_ok=True)
    (HERE / "assets/photos").mkdir(parents=True, exist_ok=True)
    for i in range(1, 10):
        shutil.copy(HERE.parent / "narration" / ("scene%d.m4a" % i), HERE / "assets/audio")
    for p in PHOTOS:
        shutil.copy(DEMO / "generated/photos" / p["file"], HERE / "assets/photos")
    for i, fn in enumerate([s1, s2, s3, s4, s5, s6, s7, s8, s9], 1):
        (COMP / ("s%d.html" % i)).write_text(fn())
    (COMP / "label.html").write_text(LABEL)
    (HERE / "index.html").write_text(index())
    print("wrote 9 scenes, total %.1f s" % TOTAL)


if __name__ == "__main__":
    main()
