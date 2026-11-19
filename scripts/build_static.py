#!/usr/bin/env python3
"""Build the static profile SVGs: header, ASCII terminal, project cards, footer.

  python scripts/build_static.py

The portrait grid comes from scripts/portrait.json ([[char, brightness 0-3], ...] per row).
"""
import json
import os

from svgkit import (BLACK, GREEN, GREEN_HI, INK_2, INK_3, LINE, LINE_2, MONO, PANEL, WHITE,
                    esc, font_css, frame, title_bar)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


def write(name, svg):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote assets/" + name)


# --------------------------------------------------------------------------- header
def header():
    W, H = 1200, 370
    phrases = [
        "building digital twins in NVIDIA Isaac Sim",
        "Go2 · G1 · UR5 — sim to real",
        "voice + vision agents on humanoids",
        "multi-robot fleets that work together",
    ]
    cw = 0.5459 * 20  # Anonymous Pro advance at 20px
    period = 4.5 * len(phrases)
    typing, css = [], []
    for i, p in enumerate(phrases):
        n = len(p)
        a, b = 100 * i / len(phrases), 100 * (i + 1) / len(phrases)
        t_end = a + (b - a) * 0.45  # finish typing
        hold = b - 1.2
        css.append(f"""
@keyframes v{i}{{0%,{a:.2f}%{{opacity:0}}{a + .01:.2f}%,{hold:.2f}%{{opacity:1}}{hold + .01:.2f}%,100%{{opacity:0}}}}
@keyframes w{i}{{0%,{a:.2f}%{{width:0}}{t_end:.2f}%,100%{{width:{n * cw + 2:.1f}px}}}}
@keyframes k{i}{{0%,{a:.2f}%{{transform:translateX(0)}}{t_end:.2f}%,100%{{transform:translateX({n * cw:.1f}px)}}}}
.p{i}{{animation:v{i} {period}s linear infinite}}
.r{i}{{animation:w{i} {period}s steps({n * 4}) infinite}}
.k{i}{{animation:k{i} {period}s steps({n * 4}) infinite}}""")
        typing.append(f"""
  <clipPath id="cp{i}"><rect class="r{i}" x="96" y="268" height="34" width="{n * cw + 2:.1f}"/></clipPath>
  <g class="p{i}" {'' if i == 0 else 'opacity="0"'}>
    <text clip-path="url(#cp{i})" x="96" y="292" font-family="{MONO}" font-size="20" fill="{WHITE}" xml:space="preserve">{esc(p)}</text>
    <rect class="k{i} cur" x="98" y="275" width="11" height="22" fill="{GREEN}"/>
  </g>""")

    telemetry = [
        ("go2.nav", "AUTONOMOUS"),
        ("g1.voice", "LISTENING"),
        ("amr.odom", "STREAMING"),
        ("isaac_sim", "TWIN SYNCED"),
    ]
    tel = []
    for i, (k, v) in enumerate(telemetry):
        y = 98 + i * 30
        tel.append(f"""
    <g class="tl" style="animation-delay:{0.6 + i * 0.15:.2f}s">
      <rect x="878" y="{y - 11}" width="8" height="8" fill="{GREEN}" class="blink" style="animation-delay:{i * 0.4:.1f}s"/>
      <text x="898" y="{y - 2}" fill="{INK_2}">{k}</text>
      <text x="1140" y="{y - 2}" text-anchor="end" fill="{WHITE}">{v}</text>
      <line x1="878" y1="{y + 10}" x2="1140" y2="{y + 10}" stroke="{LINE}"/>
    </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">Abhishek Pandey — Robotics Engineer · NVIDIA Omniverse Specialist · Physical AI Engineer</title>
<defs>
  <radialGradient id="glow" cx="0.08" cy="1.05" r="0.75">
    <stop offset="0" stop-color="{GREEN}" stop-opacity="0.28"/>
    <stop offset="0.55" stop-color="{GREEN}" stop-opacity="0.05"/>
    <stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#ffffff" fill-opacity="0.07"/>
  </pattern>
  <linearGradient id="fadeR" x1="0" x2="1">
    <stop offset="0" stop-color="{BLACK}" stop-opacity="1"/><stop offset="0.5" stop-color="{BLACK}" stop-opacity="0"/>
  </linearGradient>
</defs>
<style>
{font_css("Anon", "AnonB", "InterD")}
{''.join(css)}
.blink{{animation:bl 1.6s steps(1) infinite}}
@keyframes bl{{50%{{opacity:.25}}}}
.tl{{opacity:0;animation:in .6s ease-out forwards}}
.rise{{opacity:0;animation:up .9s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes in{{to{{opacity:1}}}}
@keyframes up{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
.scan{{animation:scan 5s linear infinite}}
@keyframes scan{{from{{transform:translateY(-20px)}}to{{transform:translateY({H}px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important}}}}
</style>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<rect class="scan" x="0" y="0" width="{W}" height="2" fill="{GREEN}" fill-opacity="0.12"/>

<g class="rise">
  <text x="56" y="150" font-family="'InterD', sans-serif" font-weight="800" font-size="84" letter-spacing="-2" fill="{WHITE}">Abhishek Pandey</text>
  <text x="60" y="226" font-family="'InterD', sans-serif" font-weight="800" font-size="30" letter-spacing="-0.3" fill="{GREEN}" xml:space="preserve">Robotics Engineer<tspan fill="{INK_3}">   /   </tspan>NVIDIA Omniverse Specialist<tspan fill="{INK_3}">   /   </tspan>Physical AI Engineer</text>
</g>
<text x="60" y="292" font-family="{MONO}" font-weight="700" font-size="20" fill="{GREEN}">&gt;_</text>
{''.join(typing)}

<g font-family="{MONO}" font-size="14">
  <text x="878" y="60" fill="{INK_3}" letter-spacing="2">FLEET STATUS</text>
  {''.join(tel)}
</g>

<path d="M0 {H - 6} H{W} V{H} H0 Z" fill="{GREEN}"/>
<path d="M0 {H - 6} H372 L348 {H - 30} H0 Z" fill="{GREEN}"/>
<text x="24" y="{H - 13}" font-family="{MONO}" font-weight="700" font-size="11" letter-spacing="2" fill="{BLACK}">PHYSICAL AI · DIGITAL TWINS</text>
</svg>
"""


# --------------------------------------------------------------------------- terminal
def terminal():
    rows = json.load(open(os.path.join(HERE, "portrait.json")))
    cols = max(len(r) for r in rows)
    fs, cw, lh = 10, 6, 10
    W = 720
    px = (W - cols * cw) / 2
    H = 840
    y0 = H - 44 - len(rows) * lh
    alpha = [0.42, 0.62, 0.84, 1.0]
    step = 0.022
    lines = []
    for i, r in enumerate(rows):
        r = r + [[" ", 0]] * (cols - len(r))
        spans, cur, buf = [], None, ""
        for ch, lv in r:
            lv = lv if ch != " " else (cur if cur is not None else 0)
            if cur is None:
                cur = lv
            if lv != cur:
                spans.append((cur, buf)); buf, cur = "", lv
            buf += ch
        spans.append((cur, buf))
        body = "".join(f'<tspan fill-opacity="{alpha[lv]}">{esc(t)}</tspan>' for lv, t in spans)
        lines.append(f'<text class="l" style="animation-delay:{0.9 + i * step:.3f}s" x="{px}" y="{y0 + (i + 1) * lh - 2}" '
                     f'textLength="{cols * cw}" lengthAdjust="spacing" xml:space="preserve">{body}</text>')
    t_end = 0.9 + len(rows) * step
    cmd = "./whoami --ascii"
    ccw = 0.5459 * 15
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">ASCII portrait of Abhishek Pandey rendering in a terminal</title>
<style>
{font_css("Anon")}
.l{{white-space:pre;opacity:0;animation:fade .25s ease-out forwards}}
@keyframes fade{{to{{opacity:1}}}}
.type{{animation:type .7s steps({len(cmd)}) .1s both}}
@keyframes type{{from{{width:0}}to{{width:{len(cmd) * ccw + 2:.1f}px}}}}
.scan{{opacity:0;animation:scan {len(rows) * step:.2f}s linear .9s forwards}}
@keyframes scan{{0%{{opacity:1;transform:translateY(0)}}96%{{opacity:1}}100%{{opacity:0;transform:translateY({len(rows) * lh}px)}}}}
.cursor{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.done{{opacity:0;animation:fade .3s {t_end:.2f}s forwards}}
@media (prefers-reduced-motion:reduce){{.l,.done{{opacity:1;animation:none}}.scan{{display:none}}.type{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
{title_bar(W, "abhishek@physical-ai: ~", "tty1")}
<clipPath id="tc"><rect class="type" x="{40 + 1.6 * ccw:.1f}" y="62" height="24" width="{len(cmd) * ccw + 2:.1f}"/></clipPath>
<text x="40" y="80" font-family="{MONO}" font-size="15" fill="{WHITE}" xml:space="preserve"><tspan fill="{GREEN}">$</tspan> </text>
<text x="{40 + 2 * ccw:.1f}" y="80" font-family="{MONO}" font-size="15" fill="{WHITE}" clip-path="url(#tc)">{cmd}</text>
<g font-family="{MONO}" font-size="{fs}" fill="#FFFFFF" xml:space="preserve">
{chr(10).join(lines)}
</g>
<rect class="scan" x="{px - 10}" y="{y0}" width="{cols * cw + 20}" height="2" fill="{GREEN}" fill-opacity="0.85"/>
<g class="done" font-family="{MONO}" font-size="15">
  <text x="40" y="{H - 24}" fill="{WHITE}" xml:space="preserve"><tspan fill="{GREEN}">abhishek@physical-ai</tspan><tspan fill="{INK_3}">:</tspan><tspan fill="{WHITE}">~</tspan><tspan fill="{GREEN}">$</tspan> </text>
  <rect class="cursor" x="{40 + 25 * ccw:.1f}" y="{H - 38}" width="9" height="18" fill="{GREEN}"/>
</g>
{frame(W, H)}
</svg>
"""


# --------------------------------------------------------------------------- project cards
PROJECTS = [
    dict(slug="fleet", n="01", title="Physical AI Fleet Twin",
         desc=["Go2 inspects and raises a work order, a MiR200",
               "brings the tools, a G1 guides the repair by voice.",
               "Live digital twins in Isaac Sim 6.0."],
         tags=["Isaac Sim", "Nemotron VL", "Cosmos", "Nebius"]),
    dict(slug="go2", n="02", title="Go2 Autonomous Navigation",
         desc=["3D LiDAR map with LIO-SAM, a topological graph",
               "of waypoints, A* planning and PID following.",
               "Send the Go2 to any node by number."],
         tags=["ROS 2", "LIO-SAM", "C++", "CycloneDDS"]),
    dict(slug="amr", n="03", title="Autonomous AMR Digital Twin",
         desc=["A real MiR200's odometry, read over rosbridge",
               "and streamed by UDP, drives its twin in Isaac",
               "Sim so the sim mirrors the robot in real time."],
         tags=["ROS", "rosbridge", "UDP", "Isaac Sim"]),
    dict(slug="industrial", n="04", title="Multi-Agent Industrial Twin",
         desc=["NVIDIA × Nebius hackathon build: a G1 humanoid",
               "walks with the worker, reads SOPs step by step,",
               "answers what it sees and follows on command."],
         tags=["Parakeet", "Nemotron Nano", "Cosmos Reason", "G1"]),
]


def glyph(slug, x, y):
    s = f'fill="none" stroke="{GREEN}" stroke-width="2" stroke-linecap="square"'
    if slug == "fleet":  # three nodes linked to a hub
        return (f'<g {s}><circle cx="{x+32}" cy="{y+32}" r="7"/><circle cx="{x+6}" cy="{y+8}" r="5"/>'
                f'<circle cx="{x+60}" cy="{y+10}" r="5"/><circle cx="{x+34}" cy="{y+62}" r="5"/>'
                f'<path d="M{x+10} {y+12} L{x+26} {y+27} M{x+56} {y+14} L{x+38} {y+28} M{x+33} {y+40} L{x+34} {y+57}"/></g>')
    if slug == "go2":  # waypoint graph with a path
        pts = [(4, 56), (22, 30), (44, 44), (62, 10)]
        d = " ".join(f"{'M' if i == 0 else 'L'}{x+a} {y+b}" for i, (a, b) in enumerate(pts))
        dots = "".join(f'<rect x="{x+a-4}" y="{y+b-4}" width="8" height="8" fill="{GREEN if i==3 else BLACK}" stroke="{GREEN}" stroke-width="2"/>' for i, (a, b) in enumerate(pts))
        return f'<path d="{d}" {s} stroke-dasharray="4 4"/>{dots}'
    if slug == "amr":  # mobile base with lidar + wheels
        return (f'<g {s}><rect x="{x+4}" y="{y+22}" width="58" height="26"/><circle cx="{x+16}" cy="{y+54}" r="6"/>'
                f'<circle cx="{x+50}" cy="{y+54}" r="6"/><rect x="{x+26}" y="{y+12}" width="14" height="10"/>'
                f'<path d="M{x+18} {y+6} Q{x+33} {y-4} {x+48} {y+6}"/></g>')
    # voice waveform
    hs = [10, 22, 36, 48, 30, 18, 40, 26, 12]
    return "".join(f'<rect x="{x+2+i*7}" y="{y+34-h/2}" width="3" height="{h}" fill="{GREEN}"/>' for i, h in enumerate(hs))


def card(p):
    W, H = 600, 300
    tags, tx = [], 32
    for t in p["tags"]:
        w = len(t) * 0.5459 * 13 + 20
        tags.append(f'<rect x="{tx}" y="226" width="{w:.1f}" height="26" fill="none" stroke="{LINE_2}"/>'
                    f'<text x="{tx + 10}" y="243.5" fill="{INK_2}">{esc(t)}</text>')
        tx += w + 8
    desc = "".join(f'<text x="32" y="{124 + i * 24}">{esc(l)}</text>' for i, l in enumerate(p["desc"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">{esc(p['title'])}</title>
<style>
{font_css("Anon", "AnonB", "InterD", "InterM")}
.in{{opacity:0;animation:in .7s ease-out .15s forwards}}
@keyframes in{{to{{opacity:1}}}}
.pulse{{animation:pl 2.4s ease-in-out infinite}}
@keyframes pl{{50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{.in{{opacity:1;animation:none}}.pulse{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{PANEL}"/>
<rect x="0" y="0" width="{W}" height="3" fill="{GREEN}"/>
<g class="in">
<text x="32" y="48" font-family="{MONO}" font-weight="700" font-size="14" letter-spacing="2" fill="{GREEN}">{p['n']} /</text>
<text x="32" y="86" font-family="'InterD', sans-serif" font-weight="800" font-size="29" letter-spacing="-0.5" fill="{WHITE}">{esc(p['title'])}</text>
<g font-family="'InterM', sans-serif" font-weight="500" font-size="16.5" fill="{INK_2}">{desc}</g>
<g class="pulse">{glyph(p['slug'], 500, 26)}</g>
<g font-family="{MONO}" font-size="13">{''.join(tags)}</g>
<text x="{W - 32}" y="243.5" text-anchor="end" font-family="{MONO}" font-weight="700" font-size="14" fill="{GREEN}">view repo →</text>
</g>
{frame(W, H)}
</svg>
"""


# --------------------------------------------------------------------------- simulation work
SECTORS = [("Oil & Gas", "oil"), ("Automotive", "car"), ("Dairy", "dairy"), ("Aviation", "plane")]
CLIENTS = ["Chevron", "Toyota", "GTA Airport"]
SIM_TOOLS = ["Isaac Sim", "Isaac Lab", "Isaac Lab Arena", "Omniverse", "OpenUSD"]


def sector_icon(kind, x, y):
    s = f'fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"'
    if kind == "oil":  # refinery: tower, tank and flame
        return (f'<g {s}><path d="M{x+6} {y+46} V{y+14} H{x+16} V{y+46}"/><path d="M{x+11} {y+14} V{y+4}"/>'
                f'<rect x="{x+22}" y="{y+26}" width="22" height="20" rx="3"/><path d="M{x} {y+46} H{x+48}"/>'
                f'<path d="M{x+11} {y+4} q-4 -6 0 -10 q4 4 0 10"/></g>')
    if kind == "car":
        return (f'<g {s}><path d="M{x+2} {y+36} V{y+26} L{x+10} {y+24} L{x+17} {y+12} H{x+33} L{x+41} {y+24} L{x+46} {y+26} V{y+36} Z"/>'
                f'<circle cx="{x+13}" cy="{y+38}" r="5" fill="{PANEL}"/><circle cx="{x+36}" cy="{y+38}" r="5" fill="{PANEL}"/></g>')
    if kind == "dairy":  # milk bottle + tank
        return (f'<g {s}><path d="M{x+8} {y+4} H{x+18} V{y+12} L{x+22} {y+20} V{y+46} H{x+4} V{y+20} L{x+8} {y+12} Z"/>'
                f'<path d="M{x+4} {y+30} H{x+22}"/><rect x="{x+28}" y="{y+16}" width="18" height="30" rx="9"/></g>')
    return (f'<g {s}><path d="M{x+24} {y+4} C{x+28} {y+4} {x+28} {y+10} {x+28} {y+14} V{y+20} L{x+46} {y+30} V{y+34} L{x+28} {y+29} '
            f'V{y+38} L{x+33} {y+42} V{y+45} L{x+24} {y+42} L{x+15} {y+45} V{y+42} L{x+20} {y+38} V{y+29} L{x+2} {y+34} V{y+30} '
            f'L{x+20} {y+20} V{y+14} C{x+20} {y+10} {x+20} {y+4} {x+24} {y+4} Z"/></g>')


def simulations():
    W, H = 1200, 340
    tiles = []
    tx0, tw, tg = 470, 160, 14
    for i, (name, kind) in enumerate(SECTORS):
        x = tx0 + i * (tw + tg)
        tiles.append(f"""
  <g class="in" style="animation-delay:{0.3 + i * 0.12:.2f}s">
    <rect x="{x}" y="44" width="{tw}" height="160" fill="{PANEL}" stroke="{LINE}"/>
    <rect x="{x}" y="44" width="{tw}" height="3" fill="{GREEN}"/>
    <text x="{x + 20}" y="76" font-family="{MONO}" font-weight="700" font-size="13" fill="{INK_3}">0{i + 1}</text>
    {sector_icon(kind, x + tw - 68, 62)}
    <text x="{x + 20}" y="180" font-family="'InterD', sans-serif" font-weight="800" font-size="22" fill="{WHITE}">{esc(name)}</text>
  </g>""")
    chips, cx = [], W - 48
    for t in reversed(SIM_TOOLS):
        w = len(t) * 0.5459 * 14 + 22
        cx -= w
        chips.append(f'<rect x="{cx:.1f}" y="276" width="{w:.1f}" height="30" fill="none" stroke="{LINE_2}"/>'
                     f'<text x="{cx + 11:.1f}" y="296" fill="{WHITE}">{esc(t)}</text>')
        cx -= 8
    clients = '<tspan fill="#5a5a5a">  ·  </tspan>'.join(esc(c) for c in CLIENTS)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">50+ Isaac Sim simulations across oil and gas, automotive, dairy and aviation for clients including {', '.join(CLIENTS)}</title>
<style>
{font_css("Anon", "AnonB", "InterD", "InterM")}
.in{{opacity:0;animation:in .7s ease-out forwards}}
@keyframes in{{to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.in{{opacity:1;animation:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
<g class="in">
  <text x="48" y="64" font-family="{MONO}" font-weight="700" font-size="15" letter-spacing="3" fill="{GREEN}">// INDUSTRIAL SIMULATION</text>
  <text x="42" y="182" font-family="'InterD', sans-serif" font-weight="800" font-size="132" letter-spacing="-3" fill="{GREEN}">50+</text>
  <text x="48" y="214" font-family="'InterM', sans-serif" font-weight="500" font-size="20" fill="{WHITE}">Isaac Sim simulations built for industry</text>
</g>
{''.join(tiles)}
<line x1="48" y1="240.5" x2="{W - 48}" y2="240.5" stroke="{LINE}"/>
<g class="in" style="animation-delay:.8s">
  <text x="48" y="270" font-family="{MONO}" font-weight="700" font-size="13" letter-spacing="2" fill="{INK_3}">CLIENTS</text>
  <text x="48" y="304" font-family="'InterD', sans-serif" font-weight="800" font-size="26" fill="{WHITE}" xml:space="preserve">{clients}</text>
  <text x="{W - 48}" y="262" text-anchor="end" font-family="{MONO}" font-weight="700" font-size="13" letter-spacing="2" fill="{INK_3}">TOOLS</text>
  <g font-family="{MONO}" font-weight="700" font-size="14">{''.join(chips)}</g>
</g>
{frame(W, H)}
</svg>
"""


def footer():
    W, H = 1200, 70
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="sim to real">
<style>{font_css("Anon")}
.m{{animation:mv 6s linear infinite}}@keyframes mv{{from{{transform:translateX(-160px)}}to{{transform:translateX({W}px)}}}}
@media (prefers-reduced-motion:reduce){{.m{{animation:none}}}}</style>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
<rect y="{H - 6}" width="{W}" height="6" fill="{GREEN}"/>
<rect class="m" x="0" y="{H - 10}" width="160" height="4" fill="{GREEN_HI}"/>
<text x="{W / 2}" y="34" text-anchor="middle" font-family="{MONO}" font-size="14" letter-spacing="4" fill="{INK_3}">SIM <tspan fill="{GREEN}">→</tspan> REAL · BUILT IN BENGALURU</text>
</svg>
"""


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    write("header.svg", header())
    write("terminal-ascii.svg", terminal())
    for p in PROJECTS:
        write(f"card-{p['slug']}.svg", card(p))
    write("simulations.svg", simulations())
    write("footer.svg", footer())