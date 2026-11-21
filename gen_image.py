"""Generate THE WORLD front page for Friday 20 November 2026.

Draws the whole page with PIL primitives only (no external assets, no
network). Deterministic: same input always writes the same bytes.
Run:  python3 gen_image.py   (writes entry.png next to this file)
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 48
USABLE = W - 2 * MARGIN
PAPER = (247, 243, 234)
INK = (17, 17, 17)
GREY = (110, 105, 95)
RED = (178, 34, 34)
NAVY = (16, 28, 52)
NAVY2 = (28, 44, 78)
ORANGE = (255, 140, 40)
GOLD = (255, 196, 66)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, width):
    """Wrap text on word boundaries to fit width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, width, max_lines):
    """Wrap text; fail loudly if it needs more than max_lines."""
    lines = wrap(draw, text, fnt, width)
    assert len(lines) <= max_lines, f"{text!r} needs {len(lines)} lines (max {max_lines})"
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def burst(draw, cx, cy, r, color, rays=12):
    """Jagged explosion: polygon with alternating long/short spikes."""
    pts = []
    for i in range(rays * 2):
        a = math.pi * i / rays
        rr = r * (1.9 if i % 2 == 0 else 0.75)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=color)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- date line ----
    y = 28
    d.text((MARGIN, y), "FRIDAY, 20 NOVEMBER 2026", font=SANS_B(18), fill=INK)
    right = "WORLD EDITION"
    d.text((W - MARGIN - d.textlength(right, font=SANS_B(18)), y), right,
           font=SANS_B(18), fill=GREY)
    y += 28
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)

    # ---- masthead ----
    y += 6
    mast = "THE WORLD"
    f_mast = SERIF_B(60)
    d.text(((W - d.textlength(mast, font=f_mast)) / 2, y), mast, font=f_mast, fill=INK)
    y += 70
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    y += 12

    # ---- kicker + headline ----
    d.text((MARGIN, y), "UKRAINE · THE WAR SPILLS OVER", font=SANS_B(20), fill=RED)
    y += 28
    headline = ["RUSSIA'S BIGGEST BARRAGE", "HITS UKRAINE, SPILLS INTO POLAND"]
    for line in headline:
        size = 54
        while d.textlength(line, font=SERIF_B(size)) > USABLE and size > 44:
            size -= 2
        d.text((MARGIN, y), line, font=SERIF_B(size), fill=INK)
        y += 58
    y += 2

    # ---- subhead ----
    sub = ("404 drones and 111 missiles overnight; two fall inside NATO Poland "
           "as Kyiv's bridges and power grid are hit.")
    lines = fit(d, sub, SERIF_I(23), USABLE, 2)
    y = draw_lines(d, lines, MARGIN, y, SERIF_I(23), INK, 30)
    y += 8

    # ---- illustration: a suspension bridge at night under attack ----
    ill_top = y
    ill_h = 160
    d.rectangle([MARGIN, ill_top, W - MARGIN, ill_top + ill_h], fill=NAVY)
    for (sx, sy) in [(90, 16), (170, 36), (300, 14), (520, 30), (700, 16),
                     (830, 34), (930, 18), (420, 42), (620, 46)]:
        d.ellipse([MARGIN + sx - 2, ill_top + sy - 2, MARGIN + sx + 2, ill_top + sy + 2],
                  fill=(220, 220, 220))
    # missile trails diving in from the top right
    d.line([(MARGIN + 880, ill_top + 6), (MARGIN + 700, ill_top + 72)], fill=ORANGE, width=3)
    d.line([(MARGIN + 940, ill_top + 22), (MARGIN + 800, ill_top + 82)], fill=(255, 220, 160), width=2)
    d.ellipse([MARGIN + 694, ill_top + 66, MARGIN + 706, ill_top + 78], fill=GOLD)
    d.line([(MARGIN + 420, ill_top + 4), (MARGIN + 330, ill_top + 60)], fill=(255, 220, 160), width=2)
    deck_y = ill_top + 112
    steel = (190, 196, 210)

    def cable(x0, x1, y_top, sag):
        pts = []
        for i in range(21):
            t = i / 20
            x = x0 + (x1 - x0) * t
            yy = y_top + sag * 4 * t * (1 - t)
            pts.append((x, yy))
        d.line(pts, fill=steel, width=2)

    # towers: pairs of verticals with a top crossbar
    for tx in (MARGIN + 200, MARGIN + 560):
        d.rectangle([tx, ill_top + 44, tx + 10, deck_y], fill=steel)
        d.rectangle([tx + 56, ill_top + 44, tx + 66, deck_y], fill=steel)
        d.rectangle([tx, ill_top + 44, tx + 66, ill_top + 52], fill=steel)
    cable(MARGIN + 48, MARGIN + 200, ill_top + 48, 52)
    cable(MARGIN + 266, MARGIN + 560, ill_top + 48, 52)
    cable(MARGIN + 626, MARGIN + 880, ill_top + 48, 52)
    # deck band + piers + arches
    d.rectangle([MARGIN, deck_y, W - MARGIN, deck_y + 10], fill=steel)
    d.rectangle([MARGIN, deck_y, W - MARGIN, deck_y + 2], fill=(235, 238, 245))
    for px in (MARGIN + 120, MARGIN + 400, MARGIN + 700, MARGIN + 860):
        d.rectangle([px, deck_y + 10, px + 12, ill_top + ill_h - 8], fill=(120, 128, 150))
    for ax in (MARGIN + 60, MARGIN + 300, MARGIN + 560, MARGIN + 800):
        d.arc([ax, deck_y - 44, ax + 120, deck_y + 6], 180, 360, fill=steel, width=5)
    # river
    d.rectangle([MARGIN, deck_y + 10, W - MARGIN, ill_top + ill_h], fill=NAVY2)
    for rx in (140, 320, 560, 780):
        d.line([(MARGIN + rx, ill_top + ill_h - 22), (MARGIN + rx + 60, ill_top + ill_h - 22)],
               fill=(90, 120, 170), width=2)
    # explosions over the deck
    burst(d, MARGIN + 250, ill_top + 92, 12, ORANGE)
    burst(d, MARGIN + 250, ill_top + 92, 6, GOLD)
    burst(d, MARGIN + 640, ill_top + 78, 9, ORANGE)
    burst(d, MARGIN + 640, ill_top + 78, 4, GOLD)
    y = ill_top + ill_h + 6
    d.text((MARGIN, y), "KYIV'S BRIDGES UNDER FIRE — AND TWO MISSILES LAND IN POLAND",
           font=SANS_B(15), fill=GREY)
    y += 24
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 12

    # ---- secondary row: two columns ----
    col_w = (USABLE - 32) // 2
    secondaries = [
        ("MARKETS",
         "AI SELL-OFF PUSHES WALL ST INTO CORRECTION",
         "Nasdaq -5.3%, S&P -3.7%; Nvidia -14% as the SEC examines its books."),
        ("CLIMATE",
         "COP31 RUNS INTO OVERTIME",
         "Antalya talks miss the Friday deadline as the draft drops fossil-fuel language."),
    ]
    row_y = y
    max_y = y
    for i, (kick, head, body) in enumerate(secondaries):
        x = MARGIN + i * (col_w + 32)
        yy = row_y
        d.text((x, yy), kick, font=SANS_B(17), fill=RED)
        yy += 22
        hl = fit(d, head, SERIF_B(27), col_w, 2)
        yy = draw_lines(d, hl, x, yy, SERIF_B(27), INK, 32)
        yy += 4
        bl = fit(d, body, SANS(19), col_w, 2)
        yy = draw_lines(d, bl, x, yy, SANS(19), INK, 25)
        max_y = max(max_y, yy)
    y = max_y + 10
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 12

    # ---- three summaries: three columns ----
    col3 = (USABLE - 2 * 24) // 3
    summaries = [
        ("UK–EU",
         "BRITAIN AND EU SEAL BIGGEST POST-BREXIT RESET",
         "Food, emissions and youth mobility deals in Brussels."),
        ("GULF",
         "TANKER HIT IN THE STRAIT OF HORMUZ",
         "UKMTO reports a strike and fire; the US blockade holds."),
        ("MIDDLE EAST",
         "HOUTHI MISSILE HITS RIYADH'S TALLEST TOWER",
         "PIF Tower windows blown out across seven floors; no injuries."),
    ]
    row_y = y
    max_y = y
    for i, (kick, head, body) in enumerate(summaries):
        x = MARGIN + i * (col3 + 24)
        yy = row_y
        d.text((x, yy), kick, font=SANS_B(16), fill=RED)
        yy += 20
        hl = fit(d, head, SERIF_B(21), col3, 3)
        yy = draw_lines(d, hl, x, yy, SERIF_B(21), INK, 26)
        yy += 4
        bl = fit(d, body, SANS(17), col3, 2)
        yy = draw_lines(d, bl, x, yy, SANS(17), INK, 23)
        max_y = max(max_y, yy)
    y = max_y + 10

    # ---- also in this edition ----
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=GREY, width=1)
    y += 8
    also = "Also: California subpoenas Nvidia · Toxic liquor kills 11 in Manipur"
    al = fit(d, also, SANS(18), USABLE, 1)
    y = draw_lines(d, al, MARGIN, y, SANS(18), GREY, 24)
    y += 6

    # ---- ticker band ----
    band_h = 62
    band_top = H - 16 - band_h
    assert y <= band_top - 4, f"content overflows into ticker: y={y}, band_top={band_top}"
    d.rectangle([0, band_top, W, band_top + band_h], fill=INK)
    t1 = "ALSO TODAY: Senate passes energy-permitting bill 62–33"
    t2 = "Estonia to shut its Russia border from Dec 1 · Bitcoin slips below $60,000"
    d.text((MARGIN, band_top + 8), t1, font=SANS_B(19), fill=(255, 255, 255))
    d.text((MARGIN, band_top + 33), t2, font=SANS(19), fill=(210, 205, 195))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="JPEG", quality=90, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
