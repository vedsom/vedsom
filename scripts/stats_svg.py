#!/usr/bin/env python3
"""
GitHub contribution stats -> animated terminal-style SVG (stdlib only).

    GH_TOKEN=... python scripts/stats_svg.py --user vedsom --out assets/contributions.svg
    python scripts/stats_svg.py --demo --out /tmp/demo.svg     # fake data, no token

Run daily by .github/workflows/update-stats.yml.
"""
import argparse
import datetime as dt
import json
import os
import random
import re
import sys
import urllib.request
from pathlib import Path

QUERY = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
  }
}"""

FONT = 'ui-monospace,SFMono-Regular,Menlo,Consolas,"DejaVu Sans Mono",monospace'
LEVELS = ["#1a1a1a", "#0e4429", "#006d32", "#26a641", "#39d353"]
GREEN = "#3fb950"

CSS = """
text{font-family:%FONT%;fill:#d6d6d6;font-size:11px}
.dim{fill:#8a8a8a;font-size:10px}
.big{fill:%GREEN%;font-size:22px;font-weight:700}
.wh{fill:#f2f2f2}
.wk{animation:fin .35s ease-out both}
.fi{animation:fin .6s ease-out both}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
@keyframes fin{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
"""


# ---------------------------------------------------------------- data
def fetch_weeks(login, token):
    to = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    frm = to - dt.timedelta(days=364)
    body = json.dumps({"query": QUERY, "variables": {
        "login": login,
        "from": frm.isoformat().replace("+00:00", "Z"),
        "to": to.isoformat().replace("+00:00", "Z"),
    }}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors") or not data.get("data", {}).get("user"):
        sys.exit(f"GraphQL error: {data.get('errors') or 'user not found'}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]


def demo_weeks():
    rnd = random.Random(7)
    start = dt.date.today() - dt.timedelta(days=52 * 7 + (dt.date.today().weekday() + 1) % 7)
    weeks, d = [], start
    for _ in range(53):
        wk = []
        for _ in range(7):
            if d <= dt.date.today():
                wk.append((d.isoformat(), 0 if rnd.random() < 0.25 else int(rnd.expovariate(1 / 6))))
            d += dt.timedelta(days=1)
        weeks.append(wk)
    return weeks


def compute(weeks):
    flat = sorted(day for w in weeks for day in w)
    counts = [c for _, c in flat]
    total, active = sum(counts), sum(1 for c in counts if c)
    best = max(flat, key=lambda t: t[1])
    run = longest = 0
    for _, c in flat:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i, cur = len(flat) - 1, 0
    if flat[i][1] == 0:  # today may not have contributions yet
        i -= 1
    while i >= 0 and flat[i][1] > 0:
        cur += 1
        i -= 1
    months = {}
    for date, c in flat:
        months[date[:7]] = months.get(date[:7], 0) + c
    keys = sorted(months)[-12:]
    mlabels = [dt.date.fromisoformat(k + "-01").strftime("%b") for k in keys]
    bd = dt.date.fromisoformat(best[0])
    return dict(total=total, active=active, days=len(flat), best=best[1], best_date=f"{bd:%b} {bd.day}",
                avg=total / active if active else 0, longest=longest, current=cur,
                months=[(l, months[k]) for l, k in zip(mlabels, keys)])


# ---------------------------------------------------------------- svg
def level(count, top):
    if count <= 0:
        return 0
    return min(4, max(1, -(-count * 4 // top)))


def build(weeks, s, target_h, user, host):
    pad, cell, pitch = 24, 7, 9
    nweeks = len(weeks)
    W = pad * 2 + nweeks * pitch - 2
    top_count = max(c for w in weeks for _, c in w) or 1

    cards = [
        ("current streak", f"{s['current']}", "days"),
        ("longest streak", f"{s['longest']}", "days (last year)"),
        ("contributions", f"{s['total']:,}", "in the last year"),
        ("active days", f"{s['active']}", f"{round(100 * s['active'] / s['days'])}% of the year"),
        ("best day", f"{s['best']}", s["best_date"]),
        ("avg / active day", f"{s['avg']:.1f}", "contributions"),
    ]
    gy = 98
    cy0 = gy + 7 * pitch + 22
    cw_, ch_, gap = (W - pad * 2 - 10) / 2, 52, 10
    cy_end = cy0 + 3 * ch_ + 2 * gap
    label_y = cy_end + 28
    chart_top = label_y + 14
    H = max(chart_top + 110 + 34, round(target_h))
    chart_h = H - chart_top - 34

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="GitHub contribution stats">',
         f"<style>{CSS.replace('%FONT%', FONT).replace('%GREEN%', GREEN)}</style>",
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="#0b0b0b" stroke="#2a2a2a"/>',
         f'<path d="M1 36H{W - 1}" stroke="#262626"/>']
    for i, c in enumerate(("#e0e0e0", "#8a8a8a", "#4a4a4a")):
        o.append(f'<circle cx="{22 + i * 20}" cy="18" r="6" fill="{c}"/>')
    o.append(f'<text x="{W / 2:.0f}" y="22" text-anchor="middle" class="dim" style="font-size:12px">'
             f'{user}@{host}: ~</text>')
    o.append(f'<text x="{pad}" y="62" class="fi" style="font-size:13px;animation-delay:.2s">'
             f'{user}@{host} ~ $ ./contributions.sh</text>')
    o.append(f'<text x="{pad}" y="86" class="dim fi" style="animation-delay:.4s">'
             f'<tspan style="fill:{GREEN}">{s["total"]:,}</tspan> contributions in the last year</text>')

    # contribution grid, week by week
    for wi, week in enumerate(weeks):
        o.append(f'<g class="wk" style="animation-delay:{0.5 + wi * 0.03:.2f}s">')
        for date, c in week:
            row = (dt.date.fromisoformat(date).weekday() + 1) % 7  # Sunday = 0
            o.append(f'<rect x="{pad + wi * pitch}" y="{gy + row * pitch}" width="{cell}" height="{cell}" '
                     f'rx="1.5" fill="{LEVELS[level(c, top_count)]}"/>')
        o.append("</g>")

    # stat cards
    for i, (label, value, sub) in enumerate(cards):
        x = pad + (i % 2) * (cw_ + 10)
        y = cy0 + (i // 2) * (ch_ + gap)
        d = 1.6 + i * 0.12
        o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">'
                 f'<rect x="{x:.1f}" y="{y}" width="{cw_:.1f}" height="{ch_}" rx="6" fill="#161616" stroke="#262626"/>'
                 f'<text x="{x + 12:.1f}" y="{y + 16}" class="dim">{label}</text>'
                 f'<text x="{x + 12:.1f}" y="{y + 40}" class="big">{value}</text>'
                 f'<text x="{x + cw_ - 12:.1f}" y="{y + 40}" class="dim" text-anchor="end">{sub}</text></g>')

    # monthly bars
    o.append(f'<text x="{pad}" y="{label_y}" class="dim fi" style="animation-delay:2.4s">'
             f'$ contributions / month</text>')
    months = s["months"]
    slot = (W - pad * 2) / len(months)
    mx = max(v for _, v in months) or 1
    for i, (lab, v) in enumerate(months):
        h = max(2, v / mx * (chart_h - 14))
        x = pad + i * slot + slot * 0.2
        y = chart_top + chart_h - h
        d = 2.5 + i * 0.07
        o.append(f'<rect class="bar" x="{x:.1f}" y="{y:.1f}" width="{slot * 0.6:.1f}" height="{h:.1f}" rx="2" '
                 f'fill="{GREEN}" style="animation-delay:{d:.2f}s"/>')
        o.append(f'<text class="dim fi" x="{x + slot * 0.3:.1f}" y="{y - 4:.1f}" text-anchor="middle" '
                 f'style="font-size:9px;fill:{GREEN};animation-delay:{d + 0.5:.2f}s">{v}</text>')
        o.append(f'<text class="dim" x="{x + slot * 0.3:.1f}" y="{chart_top + chart_h + 16}" '
                 f'text-anchor="middle" style="font-size:9px">{lab}</text>')
    o.append("</svg>")
    return "\n".join(o)


def match_height(ascii_svg):
    """Use the ASCII terminal's height so both windows line up in the README."""
    p = Path(ascii_svg)
    if p.exists():
        m = re.search(r'viewBox="0 0 \d+ (\d+)"', p.read_text(encoding="utf-8")[:400])
        if m:
            return int(m.group(1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="vedsom")
    ap.add_argument("--host", default="github")
    ap.add_argument("--shell-user", default="abhishek", help="name shown in the terminal prompt")
    ap.add_argument("--out", default="assets/contributions.svg")
    ap.add_argument("--match", default="assets/terminal-ascii.svg", help="copy height of this SVG")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    if a.demo:
        weeks = demo_weeks()
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("Set GH_TOKEN (or GITHUB_TOKEN), or use --demo")
        weeks = fetch_weeks(a.user, token)

    svg = build(weeks, compute(weeks), match_height(a.match), a.shell_user, a.host)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({len(svg) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
