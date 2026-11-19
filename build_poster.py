#!/usr/bin/env python3
"""Render the 19 November 2026 one-image news poster from scratch.

Running this file writes ``entry.png`` (1024 x 1024) next to the script.
It needs Pillow and the bundled DejaVu fonts in ``fonts/``.  Everything is
fixed at authoring time — no network, no clock, no randomness — so a
re-run reproduces the same PNG byte for byte.

Layout, top to bottom: masthead band, GTA VI hero with a sunset panel,
an ICJ feature strip, five story cards, an "ALSO TODAY" ticker, and a
sources footer.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / "fonts"
SYSTEM_FONTS = Path("/usr/share/fonts/truetype/dejavu")

CANVAS_W, CANVAS_H = 1024, 1024

# Palette — deep plum masthead/hero, gold accents, warm paper background.
PLUM = (130, 28, 78)
HERO_PLUM = (94, 23, 69)
DEEP_PURPLE = (58, 27, 92)
PAPER = (246, 239, 227)
GOLD = (240, 165, 0)
SUN_GOLD = (255, 201, 60)
SUNSET = (158, 27, 99)
NIGHT = (42, 10, 51)
WHITE = (255, 255, 255)
CREAM = (250, 243, 230)
INK = (32, 24, 30)
MUTED = (96, 84, 90)
SOFT_PINK = (244, 214, 226)


def pick_font(bold=False, serif=False):
    """Return a loader that finds a DejaVu face at the requested size."""
    if serif:
        names = ["DejaVuSerif-Bold.ttf"]
    elif bold:
        names = ["DejaVuSans-Bold.ttf"]
    else:
        names = ["DejaVuSans.ttf"]

    def load(size):
        for name in names:
            for folder in (FONT_DIR, SYSTEM_FONTS):
                path = folder / name
                if path.is_file():
                    return ImageFont.truetype(str(path), size)
        return ImageFont.load_default()

    return load


SANS = pick_font()
SANS_BOLD = pick_font(bold=True)
SERIF_BOLD = pick_font(serif=True)


def wrap_text(draw, text, font, max_width):
    """Split *text* into lines that fit *max_width* pixels."""
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    """Draw stacked lines and return the y just below the last one."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def rounded_box(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def draw_sunset_panel(draw, left, top, right, bottom):
    """Paint the Vice City sunset: gold sun, stripes, skyline, windows."""
    draw.rectangle([left, top, right, bottom], fill=SUNSET,
                   outline=GOLD, width=3)
    cx, cy, radius = (left + right) // 2, top + 92, 74
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=SUN_GOLD)
    # Horizontal magenta bands cut across the lower half of the sun.
    for i, offset in enumerate((8, 26, 44)):
        band_y = cy + offset
        draw.rectangle([cx - radius, band_y, cx + radius, band_y + 7],
                       fill=SUNSET)
    # Skyline silhouettes, left to right, with a few lit windows.
    towers = [
        (0, 118, 52), (56, 82, 46), (106, 132, 60), (170, 96, 48),
        (222, 142, 58), (284, 70, 52), (340, 118, 52), (396, 92, 44),
    ]
    base = bottom - 34
    for dx, height, width in towers:
        draw.rectangle([left + dx, base - height, left + dx + width, base],
                       fill=NIGHT)
    windows = [(18, 128), (72, 96), (128, 150), (186, 112), (238, 158),
               (300, 84), (330, 128), (362, 148), (404, 106), (52, 162),
               (268, 122), (158, 168)]
    for wx, wy in windows:
        draw.rectangle([left + wx, top + wy, left + wx + 6, top + wy + 6],
                       fill=SUN_GOLD)
    # Foreground road with slanted gold lane marks.
    draw.rectangle([left, base, right, bottom], fill=NIGHT)
    for i in range(7):
        x0 = left + 18 + i * 58
        draw.line([x0, bottom - 4, x0 + 26, base + 6], fill=GOLD, width=2)


def draw_masthead(draw):
    """Top band: title, tagline and the gold date chip."""
    draw.rectangle([0, 0, CANVAS_W, 118], fill=PLUM)
    draw.rectangle([0, 118, CANVAS_W, 122], fill=GOLD)
    title = SERIF_BOLD(32)
    draw.text((28, 18), "THE WORLD IN ONE IMAGE", font=title, fill=WHITE)
    tagline = SANS(19)
    draw.text((30, 66), "One day's world news, in a single picture",
              font=tagline, fill=SOFT_PINK)
    chip_font = SANS_BOLD(19)
    chip_label = "THURSDAY \u00b7 19 NOVEMBER 2026"
    chip_w = int(draw.textlength(chip_label, font=chip_font)) + 44
    chip = [CANVAS_W - 28 - chip_w, 24, CANVAS_W - 28, 62]
    rounded_box(draw, chip, radius=19, fill=GOLD)
    draw.text((chip[0] + 22, 32), chip_label, font=chip_font, fill=INK)


def draw_hero(draw):
    """GTA VI lead story on the left, sunset artwork on the right."""
    draw.rectangle([0, 122, CANVAS_W, 410], fill=HERO_PLUM)
    kicker = SANS_BOLD(18)
    draw.text((28, 138), "CULTURE  \u00b7  THE BIGGEST LAUNCH IN GAMING",
              font=kicker, fill=GOLD)
    headline = SERIF_BOLD(64)
    draw.text((26, 160), "VICE CITY", font=headline, fill=WHITE)
    draw.text((26, 226), "OPENS", font=headline, fill=WHITE)
    deck = SANS(20)
    deck_lines = wrap_text(
        draw,
        "After a 13-year wait, Grand Theft Auto VI rolls out at midnight "
        "local time \u2014 back in neon-soaked Vice City, with two new leads.",
        deck, 520)
    draw_lines(draw, deck_lines, 28, 298, deck, CREAM, 25)
    draw.rectangle([28, 380, 92, 384], fill=GOLD)
    meta = SANS_BOLD(15)
    draw.text((28, 390), "PS5  \u00b7  XBOX SERIES X|S  \u00b7  $79.99  "
              "\u00b7  9.7M PRE-ORDERS", font=meta, fill=GOLD)
    draw_sunset_panel(draw, 580, 138, 996, 394)


def draw_icj_strip(draw):
    """Feature strip: the World Court's Rohingya judgment."""
    strip = [28, 422, 996, 534]
    rounded_box(draw, strip, radius=10, fill=DEEP_PURPLE)
    draw.rectangle([28, 432, 38, 524], fill=GOLD)
    kicker = SANS_BOLD(16)
    draw.text((52, 434), "THE HAGUE  \u00b7  JUSTICE", font=kicker, fill=GOLD)
    headline = SERIF_BOLD(30)
    draw.text((52, 458), "The World Court rules on the Rohingya",
              font=headline, fill=WHITE)
    body = SANS(17)
    body_lines = wrap_text(
        draw,
        "The ICJ delivers its judgment today in The Gambia v. Myanmar "
        "\u2014 the first state ever found responsible for genocide.",
        body, 920)
    draw_lines(draw, body_lines, 52, 492, body, CREAM, 20)


def draw_card(draw, box, accent, place, headline_text, body_text):
    """One white story card with a coloured spine on its left edge."""
    left, top, right, bottom = box
    rounded_box(draw, [left, top, right, bottom], radius=8, fill=WHITE,
                outline=(214, 200, 186), width=1)
    draw.rectangle([left, top + 8, left + 6, bottom - 8], fill=accent)
    label = SANS_BOLD(15)
    draw.text((left + 20, top + 12), place, font=label, fill=accent)
    head_font = SANS_BOLD(25)
    head_lines = wrap_text(draw, headline_text, head_font,
                           right - left - 40)
    end_y = draw_lines(draw, head_lines, left + 20, top + 36, head_font,
                       INK, 29)
    body_font = SANS(16)
    body_lines = wrap_text(draw, body_text, body_font,
                           right - left - 40)
    draw_lines(draw, body_lines, left + 20, end_y + 8, body_font, MUTED, 21)


def draw_cards(draw):
    """Five story cards: three across, then two wider ones below."""
    section = SANS_BOLD(19)
    draw.text((28, 546), "THE REST OF THE DAY", font=section, fill=PLUM)
    draw.line([252, 560, 996, 560], fill=(214, 200, 186), width=1)

    top_row = [
        ((28, 570, 340, 736), (31, 92, 168), "SHENZHEN",
         "Three presidents, one table",
         "Trump, Xi and Putin meet at APEC to talk nuclear cuts and Iran."),
        ((352, 570, 664, 736), (178, 34, 52), "WASHINGTON",
         "Jeffries makes history",
         "Nominated 251\u201311 \u2014 on track to be the first Black "
         "Speaker."),
        ((676, 570, 996, 736), (0, 128, 128), "INDIA",
         "Cyclone Akvan closes in",
         "Cyclone heads for landfall between Machilipatnam and Puri."),
    ]
    for box, accent, place, headline_text, body_text in top_row:
        draw_card(draw, box, accent, place, headline_text, body_text)

    bottom_row = [
        ((28, 748, 506, 888), (176, 124, 0), "BRUSSELS",
         "\u20ac45 billion for Kyiv",
         "The EU proposes a \u20ac45bn loan for Ukraine, to be repaid once "
         "Russia pays reparations."),
        ((518, 748, 996, 888), (88, 44, 150), "SPACE",
         "One light-day out",
         "After almost 50 years in flight, Voyager 1 reaches one "
         "light-day from Earth; NASA confirms today."),
    ]
    for box, accent, place, headline_text, body_text in bottom_row:
        draw_card(draw, box, accent, place, headline_text, body_text)


def draw_ticker_and_footer(draw):
    """Dark ticker band, then the sources line at the very bottom."""
    draw.rectangle([0, 900, CANVAS_W, 940], fill=HERO_PLUM)
    label = SANS_BOLD(16)
    draw.text((28, 912), "ALSO TODAY", font=label, fill=GOLD)
    ticker = SANS(15)
    items = ("Pew: Islam largest faith by 2035  \u00b7  Nvidia promises "
             "earlier pay rises  \u00b7  Australia sanctions settlers")
    draw.text((172, 913), items, font=ticker, fill=WHITE)
    footer = SANS(14)
    draw.text((28, 960),
              "Sources: AP \u00b7 Reuters \u00b7 ICJ \u00b7 FT \u00b7 The Hindu "
              "\u00b7 Rockstar Games",
              font=footer, fill=MUTED)
    right = SANS_BOLD(14)
    tail = "ONE IMAGE \u00b7 ONE DAY"
    tail_w = draw.textlength(tail, font=right)
    draw.text((CANVAS_W - 28 - tail_w, 960), tail, font=right, fill=MUTED)


def render():
    """Build the poster image and return it."""
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw_masthead(draw)
    draw_hero(draw)
    draw_icj_strip(draw)
    draw_cards(draw)
    draw_ticker_and_footer(draw)
    return canvas


def main():
    poster = render()
    target = HERE / "entry.png"
    poster.save(target, format="PNG")
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
