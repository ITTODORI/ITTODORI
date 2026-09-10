"""
Generates a crisp, side-by-side terminal SVG banner for GitHub profile READMEs,
with proper ASCII aspect-ratio scaling and clear alignment.
"""
from PIL import Image, ImageEnhance, ImageFilter
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "profile-card.svg")

# --- ASCII Portrait Config ---
# Grid size adjusted to keep correct proportions and avoid overflow
COLS = 64
ROWS = 36
CELL_W = 7
CELL_H = 12
RAMP = " .`:-=+*cs#%@"

CONTRAST = 1.10
BRIGHTNESS = 1.0
GAMMA = 1.15
SHARPEN = False
WHITE_FLOOR = 0.82

PAD = 20
TITLEBAR_H = 32
STATUS_H = 32

ART_W = COLS * CELL_W   # 448px
ART_H = ROWS * CELL_H   # 432px

# --- Unified Canvas Dimensions ---
GAP = 30
RIGHT_PANEL_W = 380
TOTAL_W = PAD + ART_W + GAP + RIGHT_PANEL_W + PAD  # 898px
TOTAL_H = TITLEBAR_H + ART_H + STATUS_H + 20        # 516px

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 0.08
STAGGER = 0.035
STATIC = bool(os.environ.get("STATIC"))

# --- Info Card Config ---
HOST = "ITTODORI"
RIGHT_START_X = PAD + ART_W + GAP
KEY_X = RIGHT_START_X
VAL_X = RIGHT_START_X + 85
LINE_H = 21
KEY_COLOR = "#ffa657"
SECTION_COLOR = "#58a6ff"
GREEN = "#3fb950"
ACCENT = "#22d3ee"

ROWS_DATA = [
    ("host",),
    ("kv", "Name", "iMen.dev"),
    ("kv", "Job", "Software Engineer"),
    ("kv", "Mail", "aminalfarisi.id@gmail.com"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Frontend", "Typescript"),
    ("kv", "Backend", "Node.js, PHP, Python"),
    ("kv", "Data", "mySQL, PostgreSQL"),
    ("kv", "Mobile", "React Native"),
    ("kv", "Deploy", "Vercel"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "Published packages on PyPI"),
    ("bul", "112 public repos, 266 followers"),
]

def esc(s):
    return html.escape(s)

# --- Process Image with Aspect Correction ---
im = Image.open(SRC).convert("L")
if SHARPEN:
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)

# Account for ~1:2 character cell aspect ratio to prevent vertical stretching
aspect_adjust = CELL_W / CELL_H
scaled_w = COLS
scaled_h = int(ROWS / aspect_adjust)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

art_top = TITLEBAR_H + 10

# --- Assemble SVG ---
parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}" height="{TOTAL_H}" '
    f'viewBox="0 0 {TOTAL_W} {TOTAL_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')

# Outer Frame
parts.append(f'<rect width="{TOTAL_W}" height="{TOTAL_H}" rx="10" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{TOTAL_W-1}" height="{TOTAL_H-1}" rx="10" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

# Window Header
parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{TOTAL_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{TOTAL_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">{esc(HOST)}@github: ~$ neofetch</text>')

# ASCII Portrait (Left Side)
font_size = CELL_H * 0.95
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.78
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = html.escape(line)
    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')

    if STATIC:
        parts.append(text)
        continue

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

# Neofetch Info Card (Right Side)
card_y = TITLEBAR_H + 28
for i, row in enumerate(ROWS_DATA):
    kind = row[0]
    if kind == "gap":
        card_y += LINE_H * 0.4
        continue

    if kind == "host":
        host = esc(HOST)
        rule_x = KEY_X + (len(HOST) + 7) * 8 + 8
        inner = (f'<text x="{KEY_X}" y="{card_y:.1f}" font-size="13.5" font-weight="700">'
                 f'<tspan fill="{GREEN}">{host}</tspan><tspan fill="{TITLE_TEXT}">@</tspan>'
                 f'<tspan fill="{ACCENT}">github</tspan></text>'
                 f'<line x1="{rule_x}" y1="{card_y-4:.1f}" x2="{TOTAL_W - PAD}" y2="{card_y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{card_y:.1f}" fill="{SECTION_COLOR}" font-size="12" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 12 + len(row[1])*8}" y1="{card_y-4:.1f}" x2="{TOTAL_W - PAD}" y2="{card_y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{card_y:.1f}" fill="{KEY_COLOR}" font-size="12" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{card_y:.1f}" fill="{INK}" font-size="12">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+3}" cy="{card_y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+14}" y="{card_y:.1f}" fill="{INK}" font-size="12">{txt}</text>')
    else:
        continue

    if STATIC:
        parts.append(f'<g>{inner}</g>')
    else:
        delay = 0.10 + i * 0.05
        parts.append(
            f'<g opacity="0" transform="translate(0,4)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 4" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.35s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
        )
    card_y += LINE_H

# Bottom Status Line
status_line_y = TOTAL_H - STATUS_H
status_y = status_line_y + 20
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{TOTAL_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="12.5">'
             f'ITTODORI@github:~$ whoami <tspan fill="{INK}">iMen.dev</tspan></text>')
parts.append(f'<rect x="{PAD+215}" y="{status_y-11:.1f}" width="7" height="13" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)

with open(OUT, "w") as f:
    f.write(svg)

print("Generated tidy terminal banner SVG:", OUT, f"({TOTAL_W}x{TOTAL_H}px)")