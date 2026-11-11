#!/usr/bin/env python3
"""Generate the Shot List Coverage demo kit.

Makes:
  shot-list/   the 20-line client shot list as PDF, Word, and Markdown
  expected/    expected results for the full shoot, the edge-case run, and the smoke test
  smoke/       a 6-line smoke-test shot list and 24 synthetic photos with EXIF capture times

All names and events are fictional. Run from any directory:

    python3 demo/generate.py

Needs: reportlab, Pillow, python-docx.
"""
import csv
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from docx import Document
from docx.shared import Pt
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
random.seed(11)

CLIENT = "Ana Rivera and Daniel Okoro"
EVENT = "Rivera-Okoro engagement party"
PHOTOGRAPHER = "Studio Lumen (fictional)"

# (number, section, time window, shot text, must-have, expected status in the full run, reason)
SECTIONS = [
    ("Getting ready", "4:00 pm to 4:30 pm"),
    ("Arrival", "4:30 pm to 5:00 pm"),
    ("Toast", "5:00 pm to 5:30 pm"),
    ("Cake", "5:30 pm to 6:00 pm"),
    ("Details", "any time"),
    ("Group photos", "6:00 pm to 6:30 pm"),
]
SHOTS = [
    (1, 0, "Ana's ring, close-up on her hand", True, "covered", ""),
    (2, 0, "Flowers on the main table, wide", False, "covered", ""),
    (3, 0, 'Welcome sign "Congratulations Ana & Daniel"', False, "covered", ""),
    (4, 1, "Ana and Daniel together, full length", True, "covered", ""),
    (5, 1, "Daniel with his parents", True, "missing", "Planned miss: the parents are not at the shoot."),
    (6, 1, "Guests arriving at the front door", False, "covered", ""),
    (7, 2, "Daniel giving the toast", True, "covered", ""),
    (8, 2, "Ana laughing during the toast", True, "covered", ""),
    (9, 2, "Glasses raised, close-up", False, "covered", ""),
    (10, 2, "Ana with Grandma Rosa", True, "covered", "Edge run: only closed-eyes frames remain, so the status must be weak."),
    (11, 3, 'Cake with the topper "A & D"', True, "covered", ""),
    (12, 3, "Ana and Daniel cutting the cake", False, "covered", ""),
    (13, 3, "First bite", False, "covered", ""),
    (14, 3, "Kids at the dessert table", False, "missing", "Planned miss: no children at the shoot."),
    (15, 4, 'Place card "Table 4"', False, "covered", ""),
    (16, 4, "Menu card on a plate", False, "missing", "Planned miss: the photographer forgets this shot on purpose."),
    (17, 4, "String lights at dusk, wide", False, "covered", ""),
    (18, 5, "Everyone together, group photo outside", True, "covered", ""),
    (19, 5, "Ana with her best friend Maya", False, "covered", ""),
    (20, 5, "Drone view of the house", False, "missing", "Planned miss: no drone."),
]

# Smoke test: (number, shot text, must-have, expected status, also acceptable, reason)
SMOKE = [
    (1, 'Welcome sign "Congratulations Ana & Daniel"', True, "covered", "", "3 good frames, 1 cut off, 1 blurred."),
    (2, 'Cake with the topper "A & D"', True, "covered", "", "4 good frames, 1 cut off."),
    (3, 'Place card "Table 4"', False, "weak", "missing", "All 4 frames are out of focus."),
    (4, "Menu card on a plate", False, "missing", "", "No frame shows a menu card."),
    (5, "Drone view of the house", False, "missing", "", "No frame shows the house from above."),
    (6, "String lights, wide", False, "covered", "weak", "3 frames show string lights on a wall."),
]

FOOTER = "SAMPLE - fictional shot list for Shot List Coverage testing."


def font(name, size):
    for p in Path("/usr/share/fonts/truetype").rglob(name):
        return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


# ---------- Shot list documents ----------

def shot_list_pdf(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle(f"Shot list - {EVENT}")
    w, h = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.8 * inch, h - 0.9 * inch, f"Shot list: {EVENT}")
    c.setFont("Helvetica", 10)
    c.drawString(0.8 * inch, h - 1.15 * inch, f"Client: {CLIENT}    Photographer: {PHOTOGRAPHER}")
    c.drawString(0.8 * inch, h - 1.32 * inch, "Shots marked * are must-have.")
    y = h - 1.75 * inch
    for si, (section, window) in enumerate(SECTIONS):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.8 * inch, y, f"{section} ({window})")
        y -= 18
        c.setFont("Helvetica", 11)
        for num, sec, text, must, _, _ in SHOTS:
            if sec != si:
                continue
            c.drawString(1.0 * inch, y, f"{num}. {text}{' *' if must else ''}")
            y -= 16
        y -= 8
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawString(0.8 * inch, 0.5 * inch, FOOTER)
    c.save()


def shot_list_docx(path):
    d = Document()
    d.add_heading(f"Shot list: {EVENT}", level=1)
    d.add_paragraph(f"Client: {CLIENT}. Photographer: {PHOTOGRAPHER}.")
    d.add_paragraph("Shots marked * are must-have.")
    for si, (section, window) in enumerate(SECTIONS):
        d.add_heading(f"{section} ({window})", level=2)
        for num, sec, text, must, _, _ in SHOTS:
            if sec == si:
                d.add_paragraph(f"{num}. {text}{' *' if must else ''}")
    p = d.add_paragraph(FOOTER)
    p.runs[0].italic = True
    p.runs[0].font.size = Pt(8)
    d.save(str(path))


def shot_list_md(path):
    lines = [f"# Shot list: {EVENT}", "", f"Client: {CLIENT}. Shots marked * are must-have.", ""]
    for si, (section, window) in enumerate(SECTIONS):
        lines += [f"## {section} ({window})", ""]
        lines += [f"{num}. {text}{' *' if must else ''}" for num, sec, text, must, _, _ in SHOTS if sec == si]
        lines.append("")
    lines.append(f"_{FOOTER}_")
    path.write_text("\n".join(lines) + "\n")


# ---------- Expected results ----------

def expected_csvs(out):
    fields = ["shot", "text", "must_have", "expected_status", "also_ok", "reason"]
    with open(out / "expected-full.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(fields)
        for num, _, text, must, status, reason in SHOTS:
            wr.writerow([num, text, "yes" if must else "", status, "", reason if status != "covered" else ""])
    with open(out / "expected-edge.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(fields)
        for num, _, text, must, status, reason in SHOTS:
            if num == 10:
                status, reason = "weak", "Only closed-eyes frames of Ana with Grandma Rosa are in the folder."
            wr.writerow([num, text, "yes" if must else "", status, "", reason if status != "covered" else ""])
    with open(out / "expected-smoke.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(fields)
        for num, text, must, status, also_ok, reason in SMOKE:
            wr.writerow([num, text, "yes" if must else "", status, also_ok, reason])


# ---------- Smoke-test photos ----------

def finish(img, path, when, blur=0.5, angle=0.0):
    d = ImageDraw.Draw(img)
    d.text((18, img.height - 34), "SAMPLE - synthetic test image", fill=(140, 140, 140), font=font("DejaVuSans.ttf", 18))
    if angle:
        img = img.rotate(angle, expand=False, fillcolor=(60, 55, 50))
    img = img.filter(ImageFilter.GaussianBlur(blur))
    px = img.load()
    for _ in range(img.width * img.height // 30):
        x, y = random.randrange(img.width), random.randrange(img.height)
        r, g, b = px[x, y]
        n = random.randint(-8, 8)
        px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    exif = Image.Exif()
    stamp = when.strftime("%Y:%m:%d %H:%M:%S")
    exif[0x0132] = stamp            # DateTime
    exif[0x010F] = "SAMPLE"         # Make
    exif[0x0110] = "SyntheticCam"   # Model
    ifd = exif.get_ifd(0x8769)
    ifd[0x9003] = stamp             # DateTimeOriginal
    ifd[0x9004] = stamp             # DateTimeDigitized
    img.save(path, quality=90, exif=exif)


def room(w=1600, h=1067, top=(214, 200, 182), floor=(150, 112, 80)):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        c = top if t < 0.7 else floor
        shade = int(18 * (t if t < 0.7 else 1 - t))
        d.line((0, y, w, y), fill=tuple(max(0, v - shade) for v in c))
    return img, d


def banner(offset_x=0, scale=1.0):
    img, d = room()
    bw, bh = int(1100 * scale), int(260 * scale)
    x0 = 250 + offset_x
    y0 = 260
    for i in range(14):  # bunting
        x = x0 - 60 + i * (bw + 120) // 14
        d.polygon([(x, 170), (x + 60, 170), (x + 30, 240)], fill=[(220, 80, 90), (90, 150, 210), (240, 200, 80)][i % 3])
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 20, fill=(250, 246, 236), outline=(190, 160, 110), width=8)
    f = font("DejaVuSerif-Bold.ttf", int(64 * scale))
    d.text((x0 + 60 * scale, y0 + 50 * scale), "Congratulations", fill=(120, 70, 50), font=f)
    d.text((x0 + 140 * scale, y0 + 140 * scale), "Ana & Daniel", fill=(120, 70, 50), font=f)
    return img


def cake(zoom=1.0, offset_x=0):
    img, d = room(top=(232, 226, 214), floor=(205, 190, 170))
    cx, base = 800 + offset_x, 860
    d.rectangle((0, 760, 1600, 1067), fill=(240, 238, 232))  # tablecloth
    w1, w2 = int(520 * zoom), int(380 * zoom)
    h1, h2 = int(210 * zoom), int(170 * zoom)
    d.ellipse((cx - w1 // 2 - 70, base - 30, cx + w1 // 2 + 70, base + 50), fill=(200, 200, 205))  # plate
    d.rectangle((cx - w1 // 2, base - h1, cx + w1 // 2, base), fill=(252, 240, 245))
    d.ellipse((cx - w1 // 2, base - h1 - 40, cx + w1 // 2, base - h1 + 40), fill=(255, 246, 250))
    d.rectangle((cx - w2 // 2, base - h1 - h2, cx + w2 // 2, base - h1), fill=(252, 236, 242))
    d.ellipse((cx - w2 // 2, base - h1 - h2 - 34, cx + w2 // 2, base - h1 - h2 + 34), fill=(255, 246, 250))
    for i in range(9):
        x = cx - w1 // 2 + 20 + i * (w1 - 40) // 8
        d.ellipse((x - 14, base - 70, x + 14, base - 42), fill=(230, 120, 150))
    top = base - h1 - h2 - 30
    d.line((cx - 60, top, cx - 60, top - 160), fill=(200, 170, 60), width=6)
    d.line((cx + 60, top, cx + 60, top - 160), fill=(200, 170, 60), width=6)
    d.text((cx - 150, top - 330), "A & D", fill=(200, 160, 40), font=font("DejaVuSerif-Bold.ttf", int(130 * zoom)))
    return img


def place_card():
    img, d = room(top=(225, 222, 215), floor=(238, 236, 230))
    d.rectangle((0, 600, 1600, 1067), fill=(246, 245, 240))
    d.ellipse((380, 640, 1220, 1000), fill=(255, 255, 255), outline=(210, 210, 210), width=6)  # plate
    d.polygon([(560, 520), (1040, 520), (1100, 700), (500, 700)], fill=(252, 250, 244), outline=(180, 170, 150))
    d.text((600, 560), "Table 4", fill=(60, 60, 70), font=font("DejaVuSerif-Bold.ttf", 96))
    return img


def string_lights():
    img, d = room(top=(48, 52, 78), floor=(40, 36, 34))
    for row in range(3):
        y0 = 160 + row * 140
        pts = [(x, y0 + int(40 * ((x / 200) % 2 - 1) ** 2)) for x in range(0, 1601, 20)]
        d.line(pts, fill=(30, 30, 30), width=3)
        for x, y in pts[::4]:
            d.ellipse((x - 12, y + 6, x + 12, y + 30), fill=(255, 220, 140))
    return img


def filler(i):
    palettes = [((214, 220, 226), (120, 98, 80)), ((230, 214, 196), (90, 80, 70)), ((198, 214, 200), (140, 120, 90))]
    top, floor = palettes[i % 3]
    img, d = room(top=top, floor=floor)
    for _ in range(4):  # furniture blocks
        x = random.randint(0, 1300)
        y = random.randint(500, 800)
        d.rectangle((x, y, x + random.randint(180, 400), y + random.randint(120, 260)),
                    fill=tuple(random.randint(60, 200) for _ in range(3)))
    if i % 2:
        d.rectangle((1100, 160, 1450, 460), fill=(240, 240, 235), outline=(90, 70, 50), width=14)  # picture frame
    return img


def smoke_photos(out):
    out.mkdir(parents=True, exist_ok=True)
    t = datetime(2026, 11, 21, 16, 5, 0)
    frames = []
    frames += [("banner", banner(0, 1.0), 0.4, -1.5), ("banner", banner(40, 0.95), 0.5, 1.0),
               ("banner", banner(-30, 1.05), 0.4, 0.0), ("banner", banner(-520, 1.1), 0.5, 0.0),
               ("banner", banner(0, 1.0), 10.0, 0.0)]
    frames += [("cake", cake(1.0), 0.4, 0.0), ("cake", cake(0.95, 60), 0.5, -2.0), ("cake", cake(1.05, -40), 0.4, 1.5),
               ("cake", cake(1.0, 20), 0.6, 0.0), ("cake", cake(1.0, 620), 0.5, 0.0)]
    frames += [("card", place_card(), r, a) for r, a in ((9.0, 0.0), (10.0, 2.0), (8.5, -1.5), (11.0, 1.0))]
    frames += [("lights", string_lights(), 0.6, a) for a in (0.0, 1.5, -1.0)]
    frames += [("filler", filler(i), 0.6, 0.0) for i in range(7)]
    random.shuffle(frames)
    manifest = []
    for n, (kind, img, blur, angle) in enumerate(frames, start=1):
        name = f"SMK_{n:04d}.jpg"
        finish(img, out / name, t, blur=blur, angle=angle)
        manifest.append((name, kind, t.strftime("%Y-%m-%d %H:%M:%S"), blur))
        t += timedelta(minutes=random.randint(3, 8))
    with open(out.parent / "smoke-manifest.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["file", "content", "capture_time", "blur_radius"])
        wr.writerows(manifest)


def smoke_list(path_md, path_pdf):
    lines = ["# Smoke test shot list", "", "Shots marked * are must-have.", ""]
    lines += [f"{n}. {text}{' *' if must else ''}" for n, text, must, *_ in SMOKE]
    lines += ["", "_SAMPLE - synthetic smoke test._"]
    path_md.write_text("\n".join(lines) + "\n")
    c = canvas.Canvas(str(path_pdf), pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.8 * inch, h - 0.9 * inch, "Smoke test shot list")
    c.setFont("Helvetica", 11)
    c.drawString(0.8 * inch, h - 1.2 * inch, "Shots marked * are must-have.")
    y = h - 1.6 * inch
    for n, text, must, *_ in SMOKE:
        c.drawString(1.0 * inch, y, f"{n}. {text}{' *' if must else ''}")
        y -= 18
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(0.8 * inch, 0.5 * inch, "SAMPLE - synthetic smoke test.")
    c.save()


def printables(path):
    """Props to print for the staged shoot: welcome sign, cake topper, place card."""
    from reportlab.lib.pagesizes import landscape
    w, h = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    c.setTitle("Shot List Coverage demo props")
    c.setFont("Times-Bold", 72)
    c.drawCentredString(w / 2, h / 2 + 30, "Congratulations")
    c.drawCentredString(w / 2, h / 2 - 60, "Ana & Daniel")
    c.setFont("Helvetica", 9)
    c.drawString(0.5 * inch, 0.4 * inch, "Prop 1: welcome sign (shot 3). Print in color and tape to a wall or easel.")
    c.showPage()
    c.setFont("Times-Bold", 160)
    c.drawCentredString(w / 2, h / 2 - 50, "A & D")
    c.setFont("Helvetica", 9)
    c.drawString(0.5 * inch, 0.4 * inch, "Prop 2: cake topper (shot 11). Print, cut out, and tape to two skewers.")
    c.showPage()
    for i, (x, y) in enumerate(((w / 4, h * 0.68), (w * 0.75, h * 0.68), (w / 4, h * 0.25), (w * 0.75, h * 0.25))):
        c.rect(x - 1.6 * inch, y - 0.8 * inch, 3.2 * inch, 1.6 * inch)
        c.setFont("Times-Bold", 44)
        c.drawCentredString(x, y - 0.2 * inch, "Table 4")
    c.setFont("Helvetica", 9)
    c.drawString(0.5 * inch, 0.4 * inch, "Prop 3: place cards (shot 15). Cut out and fold. Do not make menu cards: shot 16 is a planned miss.")
    c.showPage()
    c.save()


def main():
    for sub in ("shot-list", "expected", "smoke"):
        if (HERE / sub).exists():
            shutil.rmtree(HERE / sub)
        (HERE / sub).mkdir(parents=True)
    shot_list_pdf(HERE / "shot-list/rivera-okoro-shot-list.pdf")
    shot_list_docx(HERE / "shot-list/rivera-okoro-shot-list.docx")
    shot_list_md(HERE / "shot-list/rivera-okoro-shot-list.md")
    expected_csvs(HERE / "expected")
    smoke_list(HERE / "smoke/smoke-shot-list.md", HERE / "smoke/smoke-shot-list.pdf")
    printables(HERE / "shot-list/props-to-print.pdf")
    smoke_photos(HERE / "smoke/photos")
    for p in sorted(HERE.rglob("*")):
        if p.is_file() and p.suffix != ".py" and "photos" not in p.parts:
            print(p.relative_to(HERE))
    print(f"smoke/photos: {len(list((HERE / 'smoke/photos').glob('*.jpg')))} images")


if __name__ == "__main__":
    main()
