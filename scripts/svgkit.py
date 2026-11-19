"""Shared palette, fonts and helpers for the profile SVGs (stdlib only)."""
import base64
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

# NVIDIA-style palette
GREEN = "#76B900"
GREEN_HI = "#9BE22A"
BLACK = "#000000"
PANEL = "#070707"
PANEL_2 = "#0d0d0d"
LINE = "#1f1f1f"
LINE_2 = "#2b2b2b"
WHITE = "#F2F2F2"
INK_2 = "#A6A6A6"
INK_3 = "#6B6B6B"

# heatmap: empty + 4 steps of one green hue, dark -> bright on the black surface
HEAT = ["#141414", "#25400A", "#3D6B04", "#5A9A00", "#76B900"]

MONO = "'Anon', 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace"
DISPLAY = "'InterD', 'Inter Display', Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
SANS = "'InterM', Inter, 'Segoe UI', Helvetica, Arial, sans-serif"

_FONTS = {
    "Anon": ("mono.woff", 400),
    "AnonB": ("mono-bold.woff", 700),
    "InterD": ("display.woff", 800),
    "InterM": ("sans.woff", 500),
}


def font_css(*names):
    """@font-face rules with the subset fonts embedded as data URIs.
    SVGs shown through <img> on GitHub can't load external fonts, embedded ones work."""
    out = []
    for n in names:
        fn, w = _FONTS[n]
        with open(os.path.join(FONT_DIR, fn), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        out.append(
            f"@font-face{{font-family:'{n}';font-weight:{w};"
            f"src:url(data:font/woff;base64,{b64}) format('woff');}}"
        )
    return "\n".join(out)


def esc(s):
    return escape(str(s), {'"': "&quot;"})


def title_bar(w, title, right=""):
    """Window chrome shared by the terminal and stats cards."""
    return f"""
  <rect x="0.5" y="0.5" width="{w-1}" height="43" fill="{PANEL_2}"/>
  <line x1="0" y1="44" x2="{w}" y2="44" stroke="{LINE}"/>
  <rect x="30" y="17" width="10" height="10" fill="{GREEN}"/>
  <rect x="46" y="17" width="10" height="10" fill="none" stroke="{LINE_2}" stroke-width="1.5"/>
  <rect x="62" y="17" width="10" height="10" fill="none" stroke="{LINE_2}" stroke-width="1.5"/>
  <text x="{w/2}" y="27" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{INK_3}">{esc(title)}</text>
  <text x="{w-20}" y="27" text-anchor="end" font-family="{MONO}" font-size="12" fill="{INK_3}">{esc(right)}</text>"""


def frame(w, h):
    """Outer border with the green corner brackets."""
    L = 22
    return f"""
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" fill="none" stroke="{LINE}"/>
  <path d="M1 {L} V1 H{L}" fill="none" stroke="{GREEN}" stroke-width="3"/>
  <path d="M{w-1} {h-L} V{h-1} H{w-L}" fill="none" stroke="{GREEN}" stroke-width="3"/>"""
