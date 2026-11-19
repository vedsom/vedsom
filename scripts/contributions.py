#!/usr/bin/env python3
"""Render assets/contributions.svg (NVIDIA green/black) from your GitHub contribution calendar.

  GITHUB_TOKEN=... python scripts/contributions.py --user vedsom
  python scripts/contributions.py --sample          # offline preview with sample data

Stdlib only, so it runs on a bare GitHub Actions runner.
"""
import argparse
import datetime as dt
import json
import os
import urllib.request

from svgkit import (BLACK, GREEN, HEAT, INK_2, INK_3, LINE, MONO, PANEL, WHITE,
                    esc, font_css, frame, title_bar)

W, H = 920, 840
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-contributions-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GitHub API error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = []
    for w in weeks:
        for d in w["contributionDays"]:
            days.append((dt.date.fromisoformat(d["date"]), d["contributionCount"],
                         LEVELS.get(d["contributionLevel"], 0)))
    return days


def sample(today):
    """Offline sample shaped like the existing card (138 in the last year)."""
    counts = {}
    def put(m, d, c, y=None):
        counts[dt.date(y or (today.year if m <= today.month else today.year - 1), m, d)] = c
    put(4, 8, 4); put(4, 22, 3); put(7, 9, 2); put(7, 24, 2); put(8, 14, 2); put(9, 3, 2); put(9, 17, 2)
    october = {2: 3, 3: 2, 6: 4, 7: 6, 8: 5, 9: 3, 10: 4, 13: 7, 14: 8, 15: 13, 16: 8, 20: 4, 21: 3, 23: 5, 24: 1, 27: 2, 28: 4, 30: 2, 31: 2}
    for d, c in october.items(): put(10, d, c)
    november = {2: 3, 3: 4, 4: 2, 6: 3, 9: 2, 10: 3, 11: 4, 12: 2, 13: 3, 16: 2, 17: 3, 19: 4}
    for d, c in november.items(): put(11, d, c)
    start = today - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    days, d = [], start
    while d <= today:
        days.append((d, counts.get(d, 0), None)); d += dt.timedelta(days=1)
    return days


def stats(days, today):
    days = [x for x in days if x[0] <= today]
    year = [x for x in days if x[0] > today - dt.timedelta(days=365)]
    total = sum(c for _, c, _ in year)
    active = [x for x in year if x[1] > 0]
    longest = run = 0
    for _, c, _ in year:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    seq = list(reversed(year))
    if seq and seq[0][1] == 0:  # today not counted yet doesn't break a streak
        seq = seq[1:]
    for _, c, _ in seq:
        if not c: break
        cur += 1
    best = max(year, key=lambda x: x[1]) if year else (today, 0, 0)
    months = []
    y, m = today.year, today.month
    for _ in range(12):
        months.append((y, m)); m -= 1
        if m == 0: y, m = y - 1, 12
    months.reverse()
    mtot = [(dt.date(y, m, 1).strftime("%b"), sum(c for d, c, _ in days if d.year == y and d.month == m))
            for y, m in months]
    return dict(total=total, active=len(active), longest=longest, current=cur, best=best,
                avg=(total / len(active)) if active else 0, months=mtot, pct=round(100 * len(active) / 365))


def level(c, lv, q):
    if lv is not None: return lv
    if c == 0: return 0
    return 1 + sum(c > t for t in q)


def render(days, today, user):
    s = stats(days, today)
    nz = sorted(c for _, c, _ in days if c)
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)] if nz else [1, 2, 3]

    # heatmap: weeks as columns, Sunday on top
    start = days[0][0]
    cell, gap, x0, y0 = 13, 3, 36, 128
    heat, month_lbl, last_m = [], [], None
    for d, c, lv in days:
        wk = (d - start).days // 7
        dow = (d.weekday() + 1) % 7
        x, y = x0 + wk * (cell + gap), y0 + dow * (cell + gap)
        heat.append(f'<rect class="c" style="animation-delay:{0.25 + wk * 0.018:.3f}s" x="{x}" y="{y}" '
                    f'width="{cell}" height="{cell}" rx="2" fill="{HEAT[level(c, lv, q)]}">'
                    f'<title>{d.isoformat()}: {c}</title></rect>')
        if dow == 0 and d.month != last_m and d.day <= 7:
            month_lbl.append(f'<text x="{x}" y="{y0 + 7 * (cell + gap) + 14}">{d.strftime("%b")}</text>')
            last_m = d.month
    ncols = (days[-1][0] - start).days // 7 + 1
    legend_x = x0 + ncols * (cell + gap) - gap - 5 * 16 - 36
    legend = "".join(f'<rect x="{legend_x + i * 16}" y="100" width="12" height="12" rx="2" fill="{h}"/>'
                     for i, h in enumerate(HEAT))

    # stat tiles
    tiles = [
        ("contributions", s["total"], "last 12 months"),
        ("active days", s["active"], f'{s["pct"]}% of the year'),
        ("avg / active day", f'{s["avg"]:.1f}', "contributions"),
        ("current streak", s["current"], "days"),
        ("longest streak", s["longest"], "days"),
        ("best day", s["best"][1], s["best"][0].strftime("%b %d").replace(" 0", " ")),
    ]
    tw, th, tg, ty0 = 272, 92, 16, 290
    tile_svg = []
    for i, (lab, val, sub) in enumerate(tiles):
        tx, ty = x0 + (i % 3) * (tw + tg), ty0 + (i // 3) * (th + tg)
        tile_svg.append(f"""
  <g class="t" style="animation-delay:{0.9 + i * 0.08:.2f}s">
    <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{PANEL}" stroke="{LINE}"/>
    <rect x="{tx}" y="{ty}" width="3" height="{th}" fill="{GREEN}"/>
    <text x="{tx + 20}" y="{ty + 28}" font-family="{MONO}" font-weight="700" font-size="14" fill="{INK_2}">{esc(lab)}</text>
    <text x="{tx + 20}" y="{ty + 72}" font-family="'InterD', sans-serif" font-weight="800" font-size="36" fill="{WHITE}">{esc(val)}</text>
    <text x="{tx + tw - 18}" y="{ty + 71}" text-anchor="end" font-family="{MONO}" font-weight="700" font-size="15" fill="{WHITE}">{esc(sub)}</text>
  </g>""")

    # monthly bars (single series -> one hue, labels only where non-zero)
    by0, by1 = 548, 790
    mx = max([v for _, v in s["months"]] + [1])
    slot = (848) / 12
    bw = 30
    bars = []
    for i, (lab, v) in enumerate(s["months"]):
        cx = x0 + slot * i + slot / 2
        hgt = (by1 - by0 - 26) * v / mx
        if v:
            r = min(4, hgt)
            x = cx - bw / 2
            path = (f"M{x:.1f},{by1} V{by1 - hgt + r:.1f} Q{x:.1f},{by1 - hgt:.1f} {x + r:.1f},{by1 - hgt:.1f} "
                    f"H{x + bw - r:.1f} Q{x + bw:.1f},{by1 - hgt:.1f} {x + bw:.1f},{by1 - hgt + r:.1f} V{by1} Z")
            bars.append(f'<path class="b" style="animation-delay:{1.4 + i * 0.05:.2f}s" d="{path}" fill="{GREEN}">'
                        f'<title>{lab}: {v}</title></path>')
            bars.append(f'<text class="t" style="animation-delay:{1.9 + i * 0.05:.2f}s" x="{cx:.1f}" y="{by1 - hgt - 8:.1f}" '
                        f'text-anchor="middle" fill="{WHITE}" font-weight="700" font-size="15">{v}</text>')
        else:
            bars.append(f'<rect x="{cx - bw / 2:.1f}" y="{by1 - 2}" width="{bw}" height="2" fill="#2a2a2a"/>')
        bars.append(f'<text x="{cx:.1f}" y="{by1 + 22}" text-anchor="middle" fill="{INK_2}" font-weight="700" font-size="13">{lab}</text>')

    desc = (f"{s['total']} contributions in the last year, {s['active']} active days, "
            f"longest streak {s['longest']} days, best day {s['best'][1]} on {s['best'][0]}.")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">GitHub contributions for {esc(user)}</title><desc id="d">{esc(desc)}</desc>
<style>
{font_css("Anon", "AnonB", "InterD")}
.c{{opacity:0;animation:fade .5s ease-out forwards}}
.t{{opacity:0;animation:fade .6s ease-out forwards}}
.b{{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes grow{{to{{transform:scaleY(1)}}}}
@media (prefers-reduced-motion:reduce){{.c,.t{{opacity:1;animation:none}}.b{{transform:none;animation:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
{title_bar(W, "abhishek@physical-ai: ~/stats", "updated " + today.isoformat())}
<g font-family="{MONO}">
  <text x="{x0}" y="84" font-size="16" fill="{WHITE}"><tspan fill="{GREEN}">$</tspan> ./contributions.sh --user {esc(user)}</text>
  <text x="{x0}" y="110" font-size="14" fill="{INK_2}"><tspan fill="{GREEN}" font-weight="700">{s['total']}</tspan> contributions in the last year</text>
</g>
<g>{''.join(heat)}</g>
<g font-family="{MONO}" font-weight="700" font-size="12" fill="{INK_2}">{''.join(month_lbl)}
  <text x="{legend_x - 8}" y="110" text-anchor="end">less</text>{legend}
  <text x="{legend_x + 5 * 16 + 4}" y="110">more</text>
</g>
{''.join(tile_svg)}
<text x="{x0}" y="{by0 - 22}" font-family="{MONO}" font-size="14" fill="{WHITE}"><tspan fill="{GREEN}">$</tspan> contributions / month</text>
<line x1="{x0}" y1="{by1 + 0.5}" x2="{x0 + 848}" y2="{by1 + 0.5}" stroke="{LINE}"/>
<g font-family="{MONO}">{''.join(bars)}</g>
{frame(W, H)}
</svg>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GH_USER", "vedsom"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "assets", "contributions.svg"))
    ap.add_argument("--sample", action="store_true", help="render with offline sample data")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(dt.timezone.utc).date()
    if a.sample:
        days = sample(today)
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise SystemExit("Set GITHUB_TOKEN (or run with --sample).")
        days = fetch(a.user, token)
        today = max(d for d, _, _ in days)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(render(days, today, a.user))
    print("wrote", os.path.normpath(a.out))


if __name__ == "__main__":
    main()
