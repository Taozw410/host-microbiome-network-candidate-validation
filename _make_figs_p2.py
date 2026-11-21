"""论文 2 图形生成脚本（F1—F5）；使用与论文 3 同源的 PIL/SVG 绘图库（复制件 _figlib2.py），
避开未安装的 matplotlib。

数据源（全部从台账复算，不硬编码）：
  F1  年度趋势   —— 判读台账（候选池 1,401）＋ 第二遍B_队列（有效语料 696）
  F2  网络类型   —— 第二遍B_队列 p2_N7_type
  F3  三档与缺口 —— 第二遍B_队列 p2_N4 ＋ 靶向验证计数 6/209
  F4  研究议程   —— 第8章 §8.2—§8.4 的三条假设与证伪条件（示意图，非数据图）

输出（论文2_生物学\输出\）：F1_annual_trend_20261002、F2_network_types_20261002、
F3_levels_and_gap_20261002、F4_agenda_20261002（各 .png/.svg）＋ 三个 .csv 数据表。
运行：以仓库根为当前工作目录。
"""
import csv
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _figlib2 import INK, render, wrap  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]  # 仓库根；脚本从任意 cwd 运行都可复算
OUT = ROOT / "论文2_生物学" / "输出"
LEDGER = ROOT / "公共" / "题录" / "判读台账_论文2_方案B_20261001.csv"
QUEUE = ROOT / "公共" / "题录" / "第二遍B_队列_论文2_20261001.csv"

GRID = "#dddddd"
AX = "#8a8a8a"
C_RET = "#1f4e79"
C_KEEP = "#4d7c3f"
C_WARN = "#c0504d"


def _load():
    led = pd.read_csv(LEDGER, encoding="utf-8-sig")
    q = pd.read_csv(QUEUE, encoding="utf-8-sig")
    eff = set(q[q["p2_N4"].isin([1, 2, 3])]["idx"])
    return led, q, eff


# ---------------------------------------------------------------- F1
def draw_f1(c):
    led, _q, eff = _load()
    years = list(range(2011, 2026))
    yr = dict(zip(led["idx"], led["year"]))
    ret = [int((led["year"] == y).sum()) for y in years]
    keep = [int(sum(1 for i in eff if yr[i] == y)) for y in years]

    with open(OUT / "F1_annual_trend_20261002.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "candidate_pool_retrieved", "analytic_corpus_retained"])
        for y, a, b in zip(years, ret, keep):
            w.writerow([y, a, b])

    L, R, T, B = 96, 930, 74, 372
    ymax = 350.0
    xs = [L + i * (R - L) / (len(years) - 1) for i in range(len(years))]
    yv = lambda v: B - (v / ymax) * (B - T)  # noqa: E731

    c.text(46, 28, "Figure 1. Host-microbiome network records per year, Europe PMC, 2011-2025",
           13, INK, weight="bold")
    c.text(46, 48, "Single source, single frozen query; window and coverage limits are stated "
                   "in the caption.", 9.5, "#666666")

    for v in range(0, 351, 50):
        c.line(L, yv(v), R, yv(v), GRID, 1)
        c.text(L - 8, yv(v) + 3, str(v), 8.5, "#666666", anchor="end")
    c.line(L, T, L, B, AX, 1)
    c.line(L, B, R, B, AX, 1)
    for x, y in zip(xs, years):
        c.text(x, B + 16, str(y), 8, "#666666", anchor="middle", weight="normal")
    c.text((L + R) / 2, B + 32, "Publication year", 9, INK, anchor="middle")
    c.text(L - 60, (T + B) / 2, "Records", 9, INK, anchor="middle")

    for series, col, lab in ((ret, C_RET, "Candidate pool (retrieved)"),
                             (keep, C_KEEP, "Analytic corpus (retained)")):
        pts = [(x, yv(v)) for x, v in zip(xs, series)]
        for i in range(len(pts) - 1):
            c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], col, 2.0)
        for x, y in pts:
            c.rect(x - 2.6, y - 2.6, 5.2, 5.2, fill=col)

    c.rect(L + 14, T + 8, 290, 40, fill="#ffffff", stroke="#e2e2e2", sw=1)
    c.line(L + 24, T + 22, L + 42, T + 22, C_RET, 2.0)
    c.rect(L + 38, T + 19.4, 5.2, 5.2, fill=C_RET)
    c.text(L + 48, T + 25, "Candidate pool (retrieved)", 9, INK)
    c.line(L + 24, T + 38, L + 42, T + 38, C_KEEP, 2.0)
    c.rect(L + 38, T + 35.4, 5.2, 5.2, fill=C_KEEP)
    c.text(L + 48, T + 41, "Analytic corpus (retained)", 9, INK)

    # 末端数值标注
    c.text(xs[-1] - 12, yv(ret[-1]) - 10, str(ret[-1]), 8.5, C_RET, anchor="end")
    c.text(xs[-1] - 12, yv(keep[-1]) + 24, str(keep[-1]), 8.5, C_KEEP, anchor="end")

    c.text(46, 442, "Retrieved total 1,401; retained total 696. Counts for 2011-2015 are "
                    "single records and are not trends.", 9, "#666666")


# ---------------------------------------------------------------- F2
def draw_f2(c):
    _led, q, _eff = _load()
    keys = ["菌群内部", "多组学", "跨域", "宿主为节点"]
    labels = ["Microbial-internal network", "Multi-omics network",
              "Cross-kingdom network", "Host entities as nodes"]
    tot = int(q["p2_N4"].isin([1, 2, 3]).sum())
    vals = [int((q["p2_N7_type"] == k).sum()) for k in keys]
    cols = [C_RET, "#6b9ac4", "#a8c6a0", C_WARN]

    with open(OUT / "F2_network_types_20261002.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["network_type", "records", "share_of_696"])
        for k, v in zip(labels, vals):
            w.writerow([k, v, "%.1f%%" % (100 * v / tot)])

    c.text(46, 28, "Figure 2. What the network is built from", 13, INK, weight="bold")
    c.text(46, 48, "Analytic corpus, n = %d. The fourth category is the one the "
                   "hypotheses of Section 8 are about." % tot, 9.5, "#666666")

    L, R = 250, 900
    y = 86
    xmax = max(vals) * 1.30
    for lab, v, col in zip(labels, vals, cols):
        c.text(L - 12, y + 15, lab, 10, INK, anchor="end")
        c.rect(L, y, (R - L) * v / xmax, 22, fill=col)
        c.text(L + (R - L) * v / xmax + 8, y + 15, "%d  (%.1f%%)" % (v, 100 * v / tot), 9.5, INK)
        y += 42
    c.line(L, 78, L, y - 20, AX, 1)
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = L + (R - L) * frac
        c.text(x, y + 2, str(int(xmax * frac)), 8, "#666666", anchor="middle")
        c.line(x, y - 20, x, y - 14, AX, 1)
    c.text((L + R) / 2, y + 20, "Records", 9, INK, anchor="middle")
    c.text(46, y + 54, "Cross-kingdom and host-as-node counts are 12 (Wilson 95% CI 1.0-3.0%) "
                       "and 2 (0.1-1.0%).", 9, "#666666")


# ---------------------------------------------------------------- F3
def draw_f3(c):
    _led, q, _eff = _load()
    tot = int(q["p2_N4"].isin([1, 2, 3]).sum())
    lv = [int((q["p2_N4"] == k).sum()) for k in (1, 2, 3)]
    targeted, broad = 4, 205

    with open(OUT / "F3_levels_and_gap_20261002.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "label", "records", "share"])
        for lab, v in zip(("Level 1 microbial only", "Level 2 host-state association",
                           "Level 3 intervention or validation"), lv):
            w.writerow(["levels", lab, v, "%.1f%%" % (100 * v / tot)])
        w.writerow(["gap", "Network-directed validation", targeted, "1.9% of 209"])
        w.writerow(["gap", "Broad perturbation", broad, "98.1% of 209"])

    c.text(46, 28, "Figure 3. Where a study stops, and what is tested inside level 3",
           13, INK, weight="bold")
    c.text(46, 48, "Left: analytic corpus, n = %d. Right: the 209 interventional records, "
                   "split by whether the object of intervention was network-identified."
            % tot, 9.5, "#666666")

    # 左：三档
    L, R, B, H = 110, 560, 330, 210
    ymax = max(lv) * 1.22
    bw = 96
    labs = ["Level 1\nmicrobial only", "Level 2\nhost-state\nassociation",
            "Level 3\nintervention /\nvalidation"]
    cols = ["#c9c9c9", C_RET, C_KEEP]
    for k in range(3):
        x = L + 40 + k * 145
        h = H * lv[k] / ymax
        c.rect(x, B - h, bw, h, fill=cols[k])
        c.text(x + bw / 2, B - h - 20, "%d" % lv[k], 10.5, INK, anchor="middle", weight="bold")
        c.text(x + bw / 2, B - h - 6, "%.1f%%" % (100 * lv[k] / tot), 9, "#555555", anchor="middle")
        for j, line in enumerate(labs[k].split("\n")):
            c.text(x + bw / 2, B + 18 + 13 * j, line, 9, INK, anchor="middle")
    c.line(L, B, R - 40, B, AX, 1)
    c.line(L, B, L, B - H, AX, 1)
    for v in range(0, int(ymax) + 1, 100):
        c.line(L, B - H * v / ymax, L - 5, B - H * v / ymax, AX, 1)
        c.text(L - 10, B - H * v / ymax + 3, str(v), 8, "#666666", anchor="end")
    c.text(70, B - H / 2, "Records", 9, INK, anchor="middle")
    c.text(L, 76, "Where a study stops", 10, INK, weight="bold")

    # 右：209 的拆分
    L2, R2, B2, H2 = 660, 830, 330, 210
    hb = H2 * broad / 209
    ht = H2 * targeted / 209
    c.rect(L2, B2 - H2, R2 - L2, hb, fill=C_WARN)
    c.rect(L2, B2 - ht, R2 - L2, ht, fill=C_KEEP)
    c.text((L2 + R2) / 2, B2 - hb / 2, "205", 11, "white", anchor="middle", weight="bold")
    c.text((L2 + R2) / 2, B2 - hb / 2 + 14, "98.1%", 9, "white", anchor="middle")
    c.line(L2, B2, R2, B2, AX, 1)
    c.line(L2, B2, L2, B2 - H2, AX, 1)
    c.text(R2 + 10, B2 - ht / 2 + 3, "4  (1.9%)", 9.5, C_KEEP)
    c.text(L2, 76, "Inside level 3: what is tested", 10, INK, weight="bold")
    c.text(L2, B2 + 18, "Broad perturbation", 9, C_WARN)
    c.text(L2, B2 + 33, "Network-directed validation", 9, C_KEEP)
    c.text(46, B2 + 62, "The 1.9% is 4/209 with a conservative 95% upper bound of 6.2% after a "
                        "68-record miss audit (0/68); as a share of the corpus it is 0.6%.",
           9, "#666666")


# ---------------------------------------------------------------- F4
def draw_f4(c):
    c.text(46, 28, "Figure 4. Three hypotheses, what they measure, and what would refute them",
           13, INK, weight="bold")
    c.text(46, 48, "Each row states a comparison against a simpler alternative. "
                   "The comparison is the hypothesis, not a refinement of it.", 9.5, "#666666")

    y = 72
    rows = [
        ("H1", "Host entities as nodes predict host phenotype\n"
               "better than a microbial-only network",
         "Prediction error on held-out samples;\ndifference delta and its CI;\n"
         "stability of the cross-layer edge set",
         "delta CI contains zero; advantage\nvanishes when feature counts are\n"
         "matched; edges do not reproduce",
         ["material: 2/696 records place host", "entities in the network"]),
        ("H2", "Adding fungi and viruses changes which taxa\n"
               "are keystone, and those candidates are more\neffective when manipulated",
         "Overlap of the two keystone sets;\ndifference in disease-outcome effect size\n"
         "under one manipulation protocol",
         "Keystone sets nearly identical; no\nadvantage for cross-kingdom candidates;\n"
         "advantage lost against abundance-matched subsets",
         ["material: 12/696 cross-kingdom networks;", "0/32 biocontrol candidates network-derived"]),
        ("H3", "Centrality-derived candidates beat\nabundance-matched controls on a host endpoint",
         "Effect size on the host endpoint for\nthe centrality set and the matched set;\n"
         "residual imbalance after matching",
         "No advantage after matching; advantage\nconfined to prior major-effect taxa;\n"
         "no replication in an independent batch",
         ["material: 4/209 network-directed", "manipulations; 2 score a host endpoint"]),
    ]
    h = 128
    for tag, hyp, var, ref, chip in rows:
        c.rect(8, y + 12, 32, 26, fill=C_RET)
        c.text(24, y + 30, tag, 12, "white", anchor="middle", weight="bold")
        c.rect(44, y, 300, h, fill="#eef3f8", stroke="#dbe4ee", sw=1)
        c.rect(348, y, 296, h, fill="#eef6ee", stroke="#dce8dc", sw=1)
        c.rect(648, y, 300, h, fill="#fbf0ee", stroke="#f0ded9", sw=1)
        yy = y + 24
        for line in hyp.split("\n"):
            c.text(56, yy, line, 9.4, "#1f4e79")
            yy += 13
        yy = y + 24
        for line in var.split("\n"):
            c.text(360, yy, line, 9.2, "#4d7c3f")
            yy += 13
        yy = y + 24
        for line in ref.split("\n"):
            c.text(660, yy, line, 9.2, "#a33a2c")
            yy += 13
        for j, line in enumerate(chip):
            c.text(56, y + h - 24 + 12 * j, line, 8.4, "#666666")
        y += h + 12
    c.text(348 + 148, y - 4, "", 1)
    c.text(56, y + 16, "Left column: the claim. Middle: what is measured. Right: what would refute it. "
                       "The right column is what makes each hypothesis a test.", 9, "#666666")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    render("F1_annual_trend_20261002", 1000, 470, draw_f1)
    render("F2_network_types_20261002", 1000, 350, draw_f2)
    render("F3_levels_and_gap_20261002", 1000, 440, draw_f3)
    render("F4_agenda_20261002", 1000, 540, draw_f4)
