# -*- coding: utf-8 -*-
"""论文 2 升级分析：验证漏斗、复杂度梯度、logit 模型（宿主/复杂度/年份/报告项）、P3 检验。
只读；结果用于 §5.5 与 Figure 5。
"""
import csv
import io
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _host_level_crosstab import kw as host_kw  # noqa: E402

Q = r"D:\CodexWork\Com-Net\公共\题录"
S3 = r"D:\CodexWork\Com-Net\论文2_生物学\输出\S3_逐条筛选台账_20261002.csv"
LED = os.path.join(Q, "判读台账_论文2_方案B_20261001.csv")
ABS = os.path.join(Q, "摘要_论文2_按台账idx_20261002.csv")

HOST = {"人": "human", "动": "animal", "植": "plant"}
COMP = {"microbial_internal": 1, "multi_omics": 2, "cross_kingdom": 3, "host_as_nodes": 4}
REP = [
    r"\bASVs?\b|\bOTUs?\b|\bspecies[- ]level\b|\bgenus[- ]level\b|amplicon sequence variant",
    r"data (?:are|is|were) available|available (?:at|from|in) (?:the )?(?:GEO|SRA|ENA|Zenodo|figshare)|\bGEO\b|\bSRA\b|\bENA\b|accession (?:number|no)|deposited in|BioProject|PRJNA|dryad",
    r"sparcc|spiec-?easi|cclasso|gcoda|\bCLR\b|centered log-?ratio|compositional data",
    r"\bthreshold\b|edge weight|false discovery|\bFDR\b|multiple (?:comparison|testing|test)|\bpermutation\b|Benjamini",
    r"raref|sequencing depth|sampling (?:effort|completeness)|read depth|sequenc\w* coverage|library size|subsampl",
    r"\bcode\b.{0,30}(?:available|github|zenodo|figshare)|github\.com|zenodo\.org",
]


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def logit(X, y, iters=80):
    X = np.column_stack([np.ones(len(X)), X])
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ b)))
        W = np.clip(p * (1 - p), 1e-8, None)
        b += np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (y - p))
    p = 1 / (1 + np.exp(-(X @ b)))
    W = np.clip(p * (1 - p), 1e-8, None)
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ (X * W[:, None]))))
    return b, se


def main():
    led = {r["idx"]: r for r in csv.DictReader(io.open(LED, encoding="utf-8-sig", newline=""))}
    ab = {r["idx"]: (r.get("abstract") or "") for r in csv.DictReader(
        io.open(ABS, encoding="utf-8-sig", newline=""))}
    rows = [r for r in csv.DictReader(io.open(S3, encoding="utf-8-sig", newline=""))
            if r["in_analytic_corpus"] == "Y"]
    for r in rows:
        i = r["record_id"].replace("idx-", "")
        target = (led[i].get("N3_host_type") or "").strip()
        r["host"] = HOST.get(target) or host_kw(
            (led[i].get("title") or "") + " " + ab.get(i, "")
        )[0]
        if r["host"] not in ("human", "animal", "plant"):
            r["host"] = "undetermined"
        r["comp"] = COMP.get(r["network_type"], 1)
        text = ab.get(i, "")
        r["reporting"] = sum(1 for p in REP if re.search(p, text, re.I))
        r["nrep"] = 1 if r["reporting"] > 0 else 0
        r["y3"] = 1.0 if r["level"] == "3" else 0.0

    n = len(rows)
    print("corpus", n)
    # 漏斗
    l2 = sum(1 for r in rows if r["level"] == "2")
    l3 = sum(1 for r in rows if r["level"] == "3")
    nd = sum(1 for r in rows if r["intervention_target_network_directed"] == "Y")
    print("\nFUNNEL: 696 -> level2 %d (%.1f%%) -> level3 %d (%.1f%%) -> network-directed %d (%.2f%%)"
          % (l2, 100 * l2 / n, l3, 100 * l3 / n, nd, 100 * nd / n))
    # 复杂度 × 宿主
    print("\nlevel-3 by host x complexity (internal/multi/cross/host-node)")
    for h in ("human", "animal", "plant"):
        cells = []
        for c in (1, 2, 3, 4):
            s = [r for r in rows if r["host"] == h and r["comp"] == c]
            if s:
                k = sum(1 for r in s if r["y3"] > 0)
                lo, hi = wilson(k, len(s))
                cells.append("%d: %d/%d (%.0f%%, %.0f-%.0f)" % (c, k, len(s), 100 * k / len(s),
                                                                100 * lo, 100 * hi))
        print("  %-7s %s" % (h, " | ".join(cells)))
    # 模型仅在宿主类别确定的 695 条记录上拟合；1 条 undetermined 记录保留在语料，但不用于模型。
    model_rows = [r for r in rows if r["host"] in ("human", "animal", "plant")]
    print("\nMODEL N:", len(model_rows), "of", len(rows))
    # 模型 1：宿主 + 复杂度 + 年份
    y = np.array([r["y3"] for r in model_rows])
    X1 = np.array([[(int(r["year"]) - 2018) / 5.0,
                    1.0 if r["host"] == "animal" else 0.0,
                    1.0 if r["host"] == "plant" else 0.0,
                    r["comp"] - 1] for r in model_rows])
    b1, s1 = logit(X1, y)
    print("\nMODEL 1  logit P(level3) ~ year + host + complexity")
    for nm, bb, ss in zip(["intercept", "year/5y", "animal", "plant", "complexity-1"], b1, s1):
        print("  %-14s b=%+.3f SE=%.3f OR=%.2f z=%+.1f" % (nm, bb, ss, math.exp(bb), bb / ss))
    # 模型 2：加报告项
    X2 = np.column_stack([X1, [r["nrep"] for r in model_rows]])
    b2, s2 = logit(X2, y)
    print("\nMODEL 2  + any reporting item")
    for nm, bb, ss in zip(["intercept", "year/5y", "animal", "plant", "complexity-1", "any-report"],
                          b2, s2):
        print("  %-14s b=%+.3f SE=%.3f OR=%.2f z=%+.1f" % (nm, bb, ss, math.exp(bb), bb / ss))
    # 报告项分层
    print("\nlevel-3 by any reporting item (crude):")
    for v in (0, 1):
        s = [r for r in rows if r["nrep"] == v]
        k = sum(1 for r in s if r["y3"] > 0)
        lo, hi = wilson(k, len(s))
        print("  nrep=%d  %d/%d = %.1f%% (%.1f-%.1f)" % (v, k, len(s), 100 * k / len(s),
                                                          100 * lo, 100 * hi))


if __name__ == "__main__":
    main()
