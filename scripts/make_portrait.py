#!/usr/bin/env python3
"""Turn a photo into the ASCII grid used by the terminal card (scripts/portrait.json).

  pip install opencv-python-headless numpy
  python scripts/make_portrait.py photo.jpg --subject 14 10 100 222 --crop 30 4 92 76
  python scripts/build_static.py

--subject  box (x0 y0 x1 y1, original pixels) around the whole person, used to cut out the background
--crop     box to turn into ASCII (head + shoulders works best)
A sharp, front-lit headshot where the face fills the crop gives the clearest result.
"""
import argparse
import json
import os

import cv2
import numpy as np

RAMP = " .:-=+*#%@"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--subject", nargs=4, type=int, help="x0 y0 x1 y1 around the person")
    ap.add_argument("--crop", nargs=4, type=int, help="x0 y0 x1 y1 to render (default: subject)")
    ap.add_argument("--cols", type=int, default=110)
    ap.add_argument("--mix", type=float, default=0.6, help="global tone vs local detail (0-1)")
    ap.add_argument("--gamma", type=float, default=0.9)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "portrait.json"))
    a = ap.parse_args()

    img = cv2.imread(a.image, cv2.IMREAD_COLOR)
    S = max(1, int(round(1200 / max(img.shape[:2]))))  # work at ~1200px
    big = cv2.resize(img, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
    H, W = big.shape[:2]
    sx0, sy0, sx1, sy1 = a.subject or (int(W * .05 / S), int(H * .02 / S), int(W * .95 / S), int(H / S) - 1)

    # background removal (GrabCut seeded with the subject box)
    mask = np.zeros((H, W), np.uint8)
    bm, fm = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(big, mask, (sx0 * S, sy0 * S, (sx1 - sx0) * S, (sy1 - sy0) * S), bm, fm, 6, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))

    x0, y0, x1, y1 = a.crop or (sx0, sy0, sx1, sy1)
    g = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)[y0 * S:y1 * S, x0 * S:x1 * S]
    g = cv2.bilateralFilter(g, 9, 40, 9)
    glob = g.astype(np.float32) / 255
    loc = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(g)
    loc = cv2.addWeighted(loc, 2.0, cv2.GaussianBlur(loc, (0, 0), 4), -1.0, 0).astype(np.float32) / 255
    tone = a.mix * glob + (1 - a.mix) * loc
    mk = m[y0 * S:y1 * S, x0 * S:x1 * S].astype(np.float32) / 255

    h, w = tone.shape
    rows = int(round(h / (w / a.cols / 0.6)))  # monospace cell is 0.6 wide : 1 tall
    v = cv2.resize(tone, (a.cols, rows), interpolation=cv2.INTER_AREA)
    inside = cv2.resize(mk, (a.cols, rows), interpolation=cv2.INTER_AREA) > 0.5
    lo, hi = np.percentile(v[inside], 1), np.percentile(v[inside], 99.7)
    d = 0.14 + 0.86 * np.clip((v - lo) / (hi - lo), 0, 1) ** a.gamma

    grid = [[[RAMP[min(9, int(d[r, c] * 9 + .5))], min(3, int(d[r, c] * 4))] if inside[r, c] else [" ", 0]
             for c in range(a.cols)] for r in range(rows)]
    while grid and all(ch == " " for ch, _ in grid[0]): grid.pop(0)
    while grid and all(ch == " " for ch, _ in grid[-1]): grid.pop()
    json.dump(grid, open(a.out, "w"))
    print(f"wrote {a.out}: {len(grid)} rows x {a.cols} cols")


if __name__ == "__main__":
    main()
