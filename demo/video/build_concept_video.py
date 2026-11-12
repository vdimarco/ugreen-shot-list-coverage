#!/usr/bin/env python3
"""Build the Shot List Coverage concept preview video.

This video is a concept preview. It shows the expected report from
demo/expected/expected-full.csv with the AI-generated demo shoot. It is not a
recording of the Skill on a UGREEN AI NAS. The Round 2 video must be recorded on
the assigned NAS; see demo/video/README.md.

Usage:
    python3 demo/video/build_concept_video.py NARRATION_DIR OUT.mp4

NARRATION_DIR holds scene1 ... scene9 audio files (wav or mp3). Needs Pillow, ffmpeg, pdftoppm.
"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEMO = Path(__file__).resolve().parents[1]
PHOTOS = DEMO / "generated/photos"
W, H = 1920, 1080
BG, FG, MUTED = (22, 24, 31), (245, 246, 248), (160, 168, 180)
GREEN, AMBER, RED, GRAY = (72, 180, 110), (236, 182, 62), (222, 84, 84), (120, 126, 138)
CHIP = {"covered": GREEN, "weak": AMBER, "missing": RED}
BANNER = "CONCEPT PREVIEW  ·  AI-generated fictional photos  ·  Expected results shown  ·  Not recorded on a UGREEN NAS"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for p in Path("/usr/share/fonts").rglob(name):
        return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def canvas():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)


def banner(im):
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 46, W, H), fill=(10, 11, 15))
    f = font(20, True)
    d.text(((W - d.textlength(BANNER, font=f)) / 2, H - 36), BANNER, fill=(255, 210, 120), font=f)
    return im


def thumb(path, w, h):
    im = Image.open(path).convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def chip(d, x, y, status, size=26):
    f = font(size, True)
    tw = d.textlength(status, font=f)
    d.rounded_rectangle((x, y, x + tw + 36, y + size + 18), (size + 18) // 2, fill=CHIP.get(status.split()[0], GRAY))
    d.text((x + 18, y + 8), status, fill=(20, 20, 20), font=f)
    return tw + 36


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) > width and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t
    return lines + [cur]


def load_data():
    man = list(csv.DictReader(open(DEMO / "generated/manifest.csv")))
    exp = list(csv.DictReader(open(DEMO / "expected/expected-full.csv")))
    by_shot = {}
    for r in man:
        if r["role"] == "match":
            by_shot.setdefault(int(r["shot"]), []).append(r["file"])
    return man, exp, by_shot


# ---------- Scenes ----------

def s1_title():
    im, d = canvas()
    files = sorted(PHOTOS.glob("*.jpg"))
    strip = [files[i] for i in (3, 9, 17, 27, 40, 47)]
    for k, p in enumerate(strip):
        im.paste(thumb(p, 320, 300), (k * 320, 0))
    im.paste(Image.new("RGB", (W, 300), BG).convert("RGB"), (0, 300))
    d.text((120, 400), "Shot List Coverage", fill=FG, font=font(110, True))
    d.text((124, 545), "A UGOS Skill for photographers", fill=MUTED, font=font(46))
    d.text((124, 640), "Did you get every shot on the client's list?", fill=FG, font=font(40))
    pill = "Concept preview with AI-generated photos"
    pw = d.textlength(pill, font=font(30, True))
    d.rounded_rectangle((124, 760, 124 + pw + 68, 830), 35, fill=AMBER)
    d.text((158, 775), pill, fill=(20, 20, 20), font=font(30, True))
    d.text((124, 900), "UGREEN Hackathon 2026 on AI NAS  ·  Track: Unleash Your Creativity", fill=MUTED, font=font(28))
    return im


def s2_problem():
    im, d = canvas()
    files = sorted(PHOTOS.glob("*.jpg"))
    cols, rows, tw, th = 8, 5, 240, 160
    for k in range(cols * rows):
        p = files[(k * 7) % len(files)]
        im.paste(thumb(p, tw - 6, th - 6), ((k % cols) * tw + 3, (k // cols) * th + 3))
    over = Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.blend(im, over, 0.55)
    d = ImageDraw.Draw(im)
    d.text((120, 830), "53 frames  ·  20 shots on the list", fill=FG, font=font(52, True))
    d.text((120, 905), "Did you get every shot?", fill=(255, 210, 120), font=font(52, True))
    return im


def s3_shotlist(tmp):
    im, d = canvas()
    png = Path(tmp) / "shotlist"
    subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", str(DEMO / "shot-list/rivera-okoro-shot-list.pdf"), str(png)], check=True)
    page = Image.open(str(png) + ".png").convert("RGB")
    page = page.resize((int(page.width * 960 / page.height), 960))
    im.paste(page, (100, 50))
    x = 100 + page.width + 90
    d.text((x, 160), "The client's shot list", fill=FG, font=font(56, True))
    for i, line in enumerate(["20 shots in 6 parts of the day", "8 shots marked * are must-have", "Named people: Ana, Daniel,", "Grandma Rosa, and Maya", "PDF, Word, text, or pasted"]):
        d.text((x, 280 + i * 70), line, fill=MUTED if i in (2, 3) else FG, font=font(38))
    return im


def bubble(d, x, y, w, text, who, color):
    f = font(32)
    lines = wrap(d, text, f, w - 60)
    h = 40 + 44 * len(lines) + 40
    d.rounded_rectangle((x, y, x + w, y + h), 28, fill=color)
    d.text((x + 30, y + 16), who, fill=MUTED, font=font(24, True))
    for i, ln in enumerate(lines):
        d.text((x + 30, y + 52 + i * 44), ln, fill=FG, font=f)
    return y + h + 30


def s4_request():
    im, d = canvas()
    d.text((120, 70), "The request", fill=FG, font=font(56, True))
    d.text((120, 150), "Illustration of the conversation (expected flow)", fill=MUTED, font=font(30))
    y = 240
    y = bubble(d, 520, y, 1280, "Check my shot list Documents/rivera-okoro-shot-list.pdf against Photos/2026-11 Rivera-Okoro party. Ana is Ana Rivera, Daniel is Daniel Okoro, Grandma Rosa is Rosa Rivera, and Maya is Maya Chen.", "YOU", (52, 72, 110))
    y = bubble(d, 120, y, 1280, "The folder has 53 images, and the photo search finds all 53. I read 20 shots from the list, and 8 are must-have. Please confirm the list before I search.", "SHOT LIST COVERAGE", (44, 48, 60))
    bubble(d, 520, y, 1280, "Confirmed.", "YOU", (52, 72, 110))
    return im


def s5_how(by_shot):
    im, d = canvas()
    d.text((120, 70), "How it checks each shot", fill=FG, font=font(56, True))
    x, y = 120, 190
    d.text((x, y), "1  Search the shoot folder", fill=FG, font=font(38, True))
    cx = x
    for c in ["scene", "named people", "objects", "text in the photo", "time window"]:
        f = font(30, True)
        tw = d.textlength(c, font=f)
        d.rounded_rectangle((cx, y + 70, cx + tw + 40, y + 120), 25, outline=(120, 170, 230), width=3)
        d.text((cx + 20, y + 78), c, fill=(170, 205, 245), font=f)
        cx += tw + 60
    d.text((x, y + 160), "2  Check the best frames with the NAS vision model", fill=FG, font=font(38, True))
    qs = ["Does the photo show the shot?", "Is the main subject in focus?", "Are the eyes open?", "Is anyone cut off at the edge?"]
    for i, q in enumerate(qs):
        d.text((x + 40, y + 230 + i * 56), f"Q{i + 1}  {q}", fill=FG, font=font(32))
    ex = by_shot[11][:2] + by_shot[12][:1]
    d.text((1180, y + 225), 'Example: 11. Cake with the topper "A & D" *', fill=MUTED, font=font(26, True))
    for k, f_ in enumerate(ex):
        px = 1180 + k * 210
        im.paste(thumb(PHOTOS / f_, 200, 150), (px, y + 270))
        ok = k < 2
        d.text((px + 8, y + 430), "yes  ·  sharp" if ok else "no: no topper", fill=GREEN if ok else RED, font=font(22, True))
    d.text((x, y + 500), "3  Give each shot a status", fill=FG, font=font(38, True))
    cx = x + 40
    for s in ("covered", "weak", "missing"):
        cx += chip(d, cx, y + 570, s, 30) + 30
    d.text((x + 40, y + 650), "Covered needs a clear yes, in focus, eyes open, nothing cut off.", fill=MUTED, font=font(30))
    return im


def s6_report(exp, by_shot):
    im, d = canvas()
    d.text((80, 40), "The coverage report", fill=FG, font=font(50, True))
    d.text((80, 108), "Example of the expected report for this shoot", fill=MUTED, font=font(26))
    d.rounded_rectangle((80, 160, 1840, 240), 16, fill=(70, 30, 34))
    d.text((110, 182), "Missing must-have:  5. Daniel with his parents *  ·  missing: no photo shows Daniel with his parents", fill=FG, font=font(28, True))
    counts = {"covered": 0, "weak": 0, "missing": 0}
    for r in exp:
        counts[r["expected_status"]] += 1
    cx = 80
    for s, n in counts.items():
        cx += chip(d, cx, 262, f"{s} {n}", 26) + 20
    rows = exp
    top, rh = 330, 34
    colx = (80, 140, 900, 1080, 1260)
    for i, r in enumerate(rows):
        y = top + (i % 10) * (rh * 2) + (0 if i < 10 else 0)
        x0 = 0 if i < 10 else 960
        y = top + (i % 10) * 68
        n, text, must, st = int(r["shot"]), r["text"], r["must_have"] == "yes", r["expected_status"]
        d.text((x0 + 80, y + 14), f"{n:>2}.", fill=MUTED, font=font(24, True))
        label = (text[:30] + "…" if len(text) > 31 else text) + (" *" if must else "")
        d.text((x0 + 130, y + 14), label, fill=FG, font=font(24))
        chip(d, x0 + 600, y + 8, st, 20)
        if st == "covered":
            im.paste(thumb(PHOTOS / by_shot[n][0], 90, 60), (x0 + 760, y + 2))
            d.text((x0 + 860, y + 18), f"+{min(2, len(by_shot[n]) - 1)}", fill=MUTED, font=font(20))
    return im


def s7_edge(man):
    im, d = canvas()
    d.text((120, 70), "Edge case: closed eyes", fill=FG, font=font(56, True))
    d.text((120, 150), "The edge run keeps only these frames of shot 10", fill=MUTED, font=font(30))
    closed = [r["file"] for r in man if r["role"] == "closed-eyes"]
    for k, f_ in enumerate(closed):
        im.paste(thumb(PHOTOS / f_, 540, 380), (120 + k * 570, 230))
        d.text((130 + k * 570, 625), f"{f_}  ·  Q3 eyes open: no", fill=AMBER, font=font(24, True))
    d.text((120, 720), "10. Ana with Grandma Rosa *", fill=FG, font=font(40, True))
    w = chip(d, 760, 716, "weak", 32)
    d.text((780 + w, 724), "Eyes closed in all 3 matches.", fill=FG, font=font(34))
    d.text((120, 820), "Weak, not covered. You know while you can still take the shot again.", fill=MUTED, font=font(32))
    return im


def s8_album(by_shot):
    im, d = canvas()
    d.text((80, 40), "Album: Rivera-Okoro engagement party shot list", fill=FG, font=font(46, True))
    d.text((80, 108), "16 best frames, in shot list order  ·  made only after you approve", fill=MUTED, font=font(28))
    shots = sorted(by_shot)
    for k, s in enumerate(shots):
        x, y = 80 + (k % 8) * 222, 170 + (k // 8) * 330
        im.paste(thumb(PHOTOS / by_shot[s][0], 212, 260), (x, y))
        d.text((x + 6, y + 266), f"shot {s}", fill=MUTED, font=font(22, True))
    d.text((80, 850), "Report saved:  Rivera-Okoro engagement party shot list coverage.md", fill=FG, font=font(30))
    d.text((80, 905), "Photos moved, renamed, or changed:  0", fill=GREEN, font=font(30, True))
    return im


def s9_close():
    im, d = canvas()
    d.text((120, 260), "Shot List Coverage", fill=FG, font=font(100, True))
    for i, t in enumerate(["Private: it runs on your NAS, where the photos already are.", "Read-only: it never changes a photo.", "Based on your client's own words."]):
        d.text((124, 420 + i * 70), t, fill=FG, font=font(40))
    d.text((124, 690), "github.com/vdimarco/ugreen-shot-list-coverage", fill=(170, 205, 245), font=font(34, True))
    d.text((124, 760), "Final demo: recorded on a UGREEN AI NAS in Round 2.", fill=MUTED, font=font(30))
    return im


# ---------- Assembly ----------

def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    narr, out = Path(sys.argv[1]), Path(sys.argv[2])
    man, exp, by_shot = load_data()
    with tempfile.TemporaryDirectory() as tmp:
        scenes = [s1_title(), s2_problem(), s3_shotlist(tmp), s4_request(), s5_how(by_shot),
                  s6_report(exp, by_shot), s7_edge(man), s8_album(by_shot), s9_close()]
        parts = []
        for i, im in enumerate(scenes, start=1):
            png = Path(tmp) / f"scene{i}.png"
            im.save(png)
            audio = next(narr.glob(f"scene{i}.*"))
            dur = duration(audio) + 1.6
            part = Path(tmp) / f"part{i}.mp4"
            frames = int(dur * 30)
            vf = (f"scale=2880:-1,zoompan=z='min(zoom+0.00025,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={frames}:s={W}x{H}:fps=30,fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.4:.2f}:d=0.4,format=yuv420p")
            strip = Path(tmp) / "banner.png"
            if not strip.exists():
                banner(Image.new("RGB", (W, H), BG)).crop((0, H - 46, W, H)).save(strip)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-i", str(audio),
                            "-loop", "1", "-i", str(strip),
                            "-filter_complex", f"[0:v]{vf}[z];[z][2:v]overlay=0:{H - 46}:shortest=1,format=yuv420p[v];"
                                               f"[1:a]adelay=600|600,apad,aresample=48000[a]",
                            "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}", "-r", "30",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", str(part)],
                           check=True)
            parts.append(part)
            scenes[i - 1].save(out.parent / f"frame_scene{i}.jpg", quality=80) if "--frames" in sys.argv else None
        lst = Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        "-movflags", "+faststart", str(out)], check=True)
        for i, im in enumerate(scenes, start=1):
            banner(im).resize((960, 540)).save(Path(tmp) / f"s{i}.jpg")
        sheet = Image.new("RGB", (960 * 3, 540 * 3))
        for i in range(9):
            sheet.paste(Image.open(Path(tmp) / f"s{i + 1}.jpg"), ((i % 3) * 960, (i // 3) * 540))
        sheet.save(out.with_name(out.stem + "-storyboard.jpg"), quality=80)
    print(f"{out}  {duration(out):.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
