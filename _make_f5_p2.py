# -*- coding: utf-8 -*-
"""Figure 5: A validation funnel (696->403->209->4); B host x network-complexity gradient with Wilson intervals.
Outputs F5_... (png/svg/csv); visual style follows _figlib2.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _figlib2 import INK, render  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "输出")
INK2 = "#444444"
C1, C2, C3, C4 = "#1f4e79", "#6b9ac4", "#a8c6a0", "#c0504d"

FUNNEL = [("Records in the analytic corpus", 696, "100%"),
          ("Relate a network property to host state", 403, "57.9%"),
          ("Report an intervention or independent validation", 209, "30.0%"),
          ("Test a network-identified candidate in the biological system", 4, "0.6%")]
# host -> [(complexity label, k, n)]
GRID = {
    "Human": [("internal", 32, 246), ("multi-omics", 2, 53), ("cross-kingdom", 0, 4), ("host as node", 0, 1)],
    "Animal": [("internal", 134, 262), ("multi-omics", 20, 38), ("cross-kingdom", 1, 5)],
    "Plant": [("internal", 18, 70), ("multi-omics", 2, 13), ("cross-kingdom", 0, 2), ("host as node", 0, 1)],
}


def save_csv():
    with open(os.path.join(OUT, "F5_validation_funnel_gradient_20261117.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["panel", "series", "stage_or_complexity", "k", "n", "share"])
        for lab, n, sh in FUNNEL:
            w.writerow(["A", "funnel", lab, "", n, sh])
        for h, cells in GRID.items():
            for c, k, n in cells:
                w.writerow(["B", h, c, k, n, "%.4f" % (k / n)])


def draw(c):
    c.text(46, 26, "Figure 5. Where candidates are lost, and where validation stops", 13, INK, weight="bold")
    c.text(46, 46, "A. The funnel from corpus to network-directed validation.   "
                   "B. Validation share by host system and network complexity.", 9.5, INK2)
    # ---- A funnel
    xlab, x0, y0, h, step = 46, 220, 88, 24, 58
    maxw = 290
    for i, (lab, n, sh) in enumerate(FUNNEL):
        y = y0 + i * step
        w = maxw * (n / 696.0) ** 0.5 if n > 0 else 2
        c.rect(x0, y, max(2, w), h, fill=[C1, C2, C3, C4][i])
        c.text(x0 + maxw + 10, y + 16, "%d  (%s)" % (n, sh), 9.5, INK)
        wrapped = __import__("textwrap").wrap(lab, 28)
        top = y + h / 2 - 8 * (len(wrapped) - 1)
        for j, line in enumerate(wrapped):
            c.text(xlab, top + 11 * j, line, 8.6, INK2)
    # ---- B gradient
    bx, by, bw, bh = 590, 84, 350, 250
    c.text(bx, by - 6, "Validation share (%)", 9, INK2)
    for gv in (0, 25, 50, 75, 100):
        y = by + bh - bh * gv / 100.0
        c.line(bx, y, bx + bw, y, "#e3e3e3", 1)
        c.text(bx - 8, y + 3, str(gv), 8, "#666666", anchor="end")
    c.line(bx, by, bx, by + bh, "#999999", 1)
    c.line(bx, by + bh, bx + bw, by + bh, "#999999", 1)
    labels = ["internal", "multi", "cross", "host-node"]
    colors = {"Human": C1, "Animal": C3, "Plant": C4}
    for hi, (hname, cells) in enumerate(GRID.items()):
        for ci, (clab, k, n) in enumerate(cells):
            x = bx + 34 + ci * 92 + hi * 16
            p = k / n
            y = by + bh - bh * p
            # Wilson 95%
            z = 1.96
            d = 1 + z * z / n
            cc = (p + z * z / (2 * n)) / d
            hh = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
            lo, hi95 = max(0, cc - hh), min(1, cc + hh)
            c.line(x, by + bh - bh * lo, x, by + bh - bh * hi95, "#bbbbbb", 1.2)
            c.rect(x - 3, y - 3, 6, 6, fill=colors[hname])
            c.text(x, y - 8, "%d/%d" % (k, n), 7.4, INK2, anchor="middle")
    for ci, lab in enumerate(labels):
        c.text(bx + 34 + ci * 92 + 24, by + bh + 18, lab, 8, INK2, anchor="middle")
    lx = bx
    for hname in ("Human", "Animal", "Plant"):
        c.rect(lx, by + bh + 34, 6, 6, fill=colors[hname])
        c.text(lx + 10, by + bh + 40, hname, 8.5, INK2)
        lx += 62
    c.text(46, 430, "Bars in A are drawn on a square-root scale so that the final step remains visible. "
                    "Whiskers in B are Wilson 95% intervals; cells with n below 6 are labelled but not interpreted.",
           8.4, "#666666")


if __name__ == "__main__":
    save_csv()
    print(render("F5_validation_funnel_gradient_20261117", 1000, 470, draw))
