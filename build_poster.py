#!/usr/bin/env python3
"""Render the one-image news poster for Thursday 19 November 2026.

Dev-time generator: draws entry.png with Pillow and the DejaVu fonts bundled
in fonts/ (loaded by relative path, so the render is identical on any
machine). The graded entrypoint is main.py, which copies the committed
entry.png to the output directory. No randomness, no clock, no network:
re-running this script reproduces entry.png byte for byte.

Layout (1024 x 1024): magenta neon masthead, a hero panel with a drawn
Vice City sunset skyline, a wide ICJ feature strip, a 2x2 grid of story
cards, an "also today" ticker, and a sources footer.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

W, H = 1024, 1024
MAGENTA = (158, 22, 84)
MAGENTA_DEEP = (94, 12, 58)
VIOLET = (58, 24, 96)
PAPER = (250, 244, 236)
INK = (24, 16, 22)
GREY = (102, 92, 96)
CARD = (255, 255, 255)
CARD_LINE = (222, 206, 212)
GOLD = (255, 176, 32)
GOLD_DK = (176, 110, 8)
TEAL = (12, 122, 116)
RED = (190, 42, 54)
BLUE = (28, 84, 150)
GREEN = (46, 125, 70)
PURPLE = (98, 70, 140)
ORANGE = (232, 98, 34)
MIST = (245, 214, 228)  # light text on magenta
SUNSET_TOP = (72, 18, 92)
SUNSET_MID = (196, 38, 110)
SUNSET_LOW = (255, 122, 54)


def load(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if serif else (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def measure(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if measure(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def vgrad(draw, box, stops):
    """Vertical gradient through a list of (position, colour) stops."""
    x0, y0, x1, y1 = box
    height = max(1, y1 - y0)
    for y in range(y0, y1, 2):
        t = (y - y0) / height
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = tuple(int(c0[c] + (c1[c] - c0[c]) * f)
                            for c in range(3))
                break
        else:
            col = stops[-1][1]
        draw.rectangle([x0, y, x1, min(y + 2, y1)], fill=col)


# ---------------------------------------------------------------- stories
HERO = {
    "kicker": "CULTURE  ·  THE BIGGEST LAUNCH IN GAMING",
    "headline": ["VICE CITY", "OPENS"],
    "deck": ("After a 13-year wait, Grand Theft Auto VI rolls out at "
             "midnight local time — back in neon-soaked Vice City, "
             "with two new leads."),
    "foot": "PS5  ·  XBOX SERIES X|S   ·   $79.99   ·   9.7M PRE-ORDERS",
}

FEATURE = {
    "tag": "THE HAGUE  ·  JUSTICE",
    "headline": "The World Court rules on the Rohingya",
    "body": ("The ICJ delivers its judgment today in The Gambia v. Myanmar — "
             "the first state ever could be found responsible for genocide."),
}

CARDS = [
    ("SHENZHEN", BLUE, "Three presidents, one table",
     "Trump, Xi and Putin meet at APEC to talk nuclear cuts and Iran."),
    ("WASHINGTON", RED, "Jeffries makes history",
     "Jeffries nominated 251–11 — on track to be the first "
     "Black Speaker."),
    ("INDIA", TEAL, "Cyclone Akvan closes in",
     "Cyclone heads for landfall between Machilipatnam and Puri."),
    ("BRUSSELS", GOLD_DK, "€45 billion for Kyiv",
     "The EU proposes a €45bn loan for Ukraine, to be repaid "
     "once Russia pays reparations."),
    ("SPACE", PURPLE, "One light-day out",
     "After almost 50 years in flight, Voyager 1 reaches one "
     "light-day from Earth; NASA confirms today."),
]

TICKER = [
    "Pew: Islam largest faith by 2035",
    "Nvidia promises earlier pay rises",
    "Australia sanctions settlers",
]


def draw_skyline(draw):
    """Neon Vice City sunset: gradient sky, sun, skyline, palms, grid."""
    x0, y0, x1, y1 = 600, 108, 996, 424
    vgrad(draw, (x0, y0, x1, y1),
          [(0.0, SUNSET_TOP), (0.55, SUNSET_MID), (1.0, SUNSET_LOW)])
    # sun disc with horizontal slits
    cx, cy, r = 798, 250, 74
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 96))
    for sy in range(cy + 6, cy + r, 14):
        half = int((r * r - (sy - cy) ** 2) ** 0.5)
        draw.rectangle([cx - half, sy, cx + half, sy + 5],
                       fill=SUNSET_MID)
    # skyline silhouettes
    base = y1 - 78
    buildings = [(600, 210, 640), (640, 260, 700), (700, 180, 742),
                 (742, 300, 800), (800, 230, 846), (846, 290, 900),
                 (900, 200, 950), (950, 260, 996)]
    for bx0, top, bx1 in buildings:
        draw.rectangle([bx0, top, bx1, y1], fill=(30, 8, 40))
    # windows: tiny lit dots on the towers
    for wx, wy in [(618, 300), (660, 320), (716, 260), (770, 330),
                   (822, 300), (872, 340), (922, 280), (968, 320),
                   (690, 350), (830, 360), (940, 350)]:
        draw.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 214, 96))
    # palm silhouettes flanking the road
    for px, py, s in [(636, 392, 1.0), (948, 396, 0.85)]:
        draw.line([(px, py), (px + 6 * s, py - 44 * s)], fill=(30, 8, 40),
                  width=4)
        for dx, dy in [(-26, -14), (-18, -26), (0, -30), (18, -24),
                       (26, -12)]:
            draw.line([(px + 6 * s, py - 44 * s),
                       (px + 6 * s + dx * s, py - 44 * s + dy * s)],
                      fill=(30, 8, 40), width=3)
    # reflective road grid at the bottom
    draw.rectangle([x0, y1 - 34, x1, y1], fill=(24, 6, 34))
    for gx in range(x0 + 24, x1 - 24, 46):
        draw.line([(gx, y1 - 34), (gx + 14, y1)], fill=(255, 122, 54),
                  width=2)
    draw.line([(x0, y1 - 18), (x1, y1 - 18)], fill=(255, 176, 32), width=2)
    draw.rectangle([x0, y0, x1, y1], outline=(255, 176, 32), width=2)


def draw_card(draw, x, y, w, h, tag, colour, headline, summary,
              body_size=17, max_body=3):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=CARD,
                           outline=CARD_LINE, width=1)
    draw.rectangle([x, y + 8, x + 6, y + h - 8], fill=colour)
    tx = x + 20
    f_tag = load(15, bold=True)
    draw.text((tx, y + 12), tag, font=f_tag, fill=colour)
    f_head = load(24, bold=True)
    lines = wrap_text(draw, headline, f_head, w - 40)
    ly = y + 36
    for line in lines[:2]:
        draw.text((tx, ly), line, font=f_head, fill=INK)
        ly += 29
    f_body = load(body_size)
    blines = wrap_text(draw, summary, f_body, w - 40)
    by = ly + 4
    for line in blines[:max_body]:
        draw.text((tx, by), line, font=f_body, fill=GREY)
        by += 21


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    vgrad(d, (0, 0, W, 92), [(0.0, MAGENTA_DEEP), (1.0, MAGENTA)])
    d.text((28, 20), "THE WORLD IN ONE IMAGE",
           font=load(32, bold=True), fill=(255, 255, 255))
    d.text((28, 60), "One day's world news, in a single picture",
           font=load(16), fill=MIST)
    chip = "THURSDAY  ·  19 NOVEMBER 2026"
    f_chip = load(19, bold=True)
    cw = measure(d, chip, f_chip) + 28
    d.rounded_rectangle([W - 28 - cw, 26, W - 28, 26 + 40], radius=20,
                        fill=GOLD)
    d.text((W - 28 - cw + 14, 35), chip, font=f_chip, fill=(40, 10, 26))
    d.rectangle([0, 92, W, 96], fill=GOLD)

    # ---- hero
    vgrad(d, (0, 96, W, 440),
          [(0.0, VIOLET), (0.6, MAGENTA_DEEP), (1.0, (60, 10, 44))])
    d.text((28, 118), HERO["kicker"], font=load(18, bold=True), fill=GOLD)
    f_hero = load(64, serif=True)
    hy = 146
    for line in HERO["headline"]:
        d.text((28, hy), line, font=f_hero, fill=(255, 255, 255))
        hy += 72
    f_deck = load(21)
    for i, line in enumerate(wrap_text(d, HERO["deck"], f_deck, 520)):
        d.text((28, 302 + i * 28), line, font=f_deck, fill=MIST)
    d.rectangle([28, 392, 88, 396], fill=GOLD)
    d.text((28, 406), HERO["foot"], font=load(16, bold=True), fill=GOLD)
    draw_skyline(d)

    # ---- ICJ feature strip
    fy = 450
    d.rounded_rectangle([28, fy, 996, fy + 116], radius=8, fill=VIOLET)
    d.rectangle([28, fy + 10, 34, fy + 106], fill=GOLD)
    d.text((52, fy + 12), FEATURE["tag"], font=load(15, bold=True),
           fill=GOLD)
    d.text((52, fy + 36), FEATURE["headline"], font=load(28, bold=True),
           fill=(255, 255, 255))
    f_feat = load(17)
    for i, line in enumerate(wrap_text(d, FEATURE["body"], f_feat, 880)):
        d.text((52, fy + 72 + i * 22), line, font=f_feat, fill=MIST)

    # ---- grid header
    f_grid = load(20, bold=True)
    d.text((28, 578), "THE REST OF THE DAY", font=f_grid, fill=MAGENTA_DEEP)
    rule_x = 28 + measure(d, "THE REST OF THE DAY", f_grid) + 16
    d.line([(rule_x, 590), (996, 590)], fill=CARD_LINE, width=2)

    # ---- story cards: 3 on the top row, 2 on the bottom row
    gap = 14
    top_widths = [314, 313, 313]
    for i, (tag, colour, head, summ) in enumerate(CARDS):
        if i < 3:
            cx = 28 + sum(top_widths[:i]) + i * gap
            cy = 600
            w, h = top_widths[i], 156
            draw_card(d, cx, cy, w, h, tag, colour, head, summ,
                      body_size=15, max_body=2)
        else:
            cx = 28 + (i - 3) * (477 + gap)
            cy = 768
            draw_card(d, cx, cy, 477, 146, tag, colour, head, summ)

    # ---- ticker
    d.rectangle([0, 922, W, 962], fill=MAGENTA_DEEP)
    d.text((28, 933), "ALSO TODAY", font=load(16, bold=True), fill=GOLD)
    tx = 28 + measure(d, "ALSO TODAY", load(16, bold=True)) + 22
    f_tick = load(16)
    for item in TICKER:
        d.text((tx, 933), item, font=f_tick, fill=(255, 255, 255))
        tx += measure(d, item, f_tick) + 18
        d.ellipse([tx - 9, 941, tx - 3, 947], fill=GOLD)
        tx += 10

    # ---- footer
    d.text((28, 974),
           "Sources: AP · Reuters · ICJ · FT · The Hindu · Rockstar Games",
           font=load(13), fill=GREY)
    d.text((W - 28 - measure(d, "ONE IMAGE · ONE DAY", load(13, bold=True)),
            974), "ONE IMAGE · ONE DAY", font=load(13, bold=True), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    return out


if __name__ == "__main__":
    path = build()
    print("wrote", path, os.path.getsize(path), "bytes")
