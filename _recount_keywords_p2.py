# -*- coding: utf-8 -*-
"""用「按台账 idx 的正确摘要表」重算正文里的全部摘要级关键词计数，并打印可比对表。

覆盖：① 角色词（keystone／hub／host genetic／host transcriptome／cross-kingdom）；② 报告标准六项；
③ §8.1 用到的 longitudinal／rewiring 两个量。所有正则逐条写在 REGEX 里，供写入 S2 时照抄。
"""
import csv
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ABS = r"D:\CodexWork\Com-Net\公共\题录\摘要_论文2_按台账idx_20261002.csv"
QUEUE = r"D:\CodexWork\Com-Net\公共\题录\第二遍B_队列_论文2_20261001.csv"

REGEX = [
    ("keystone", r"\bkeystones?\b"),
    ("hub", r"\bhubs?\b"),
    ("host genetic", r"host (?:gene|genes|genetic|genetics|genome|genomic|genotype)"),
    ("host transcriptome", r"host transcriptom"),
    ("cross-kingdom", r"cross-?kingdom|inter-?kingdom"),
    ("node resolution",
     r"\bASVs?\b|\bOTUs?\b|\bspecies[- ]level\b|\bgenus[- ]level\b|amplicon sequence variant|"
     r"\b97% similarity\b|operational taxonomic unit"),
    ("data availability",
     r"data (?:are|is|were) available|available (?:at|from|in) (?:the )?(?:GEO|SRA|ENA|Zenodo|figshare)|"
     r"\bGEO\b|\bSRA\b|\bENA\b|accession (?:number|no)|deposited in|BioProject|PRJNA|dryad"),
    ("compositional", r"sparcc|spiec-?easi|cclasso|gcoda|\bCLR\b|centered log-?ratio|compositional data"),
    ("threshold / edge weight / multiple comparison",
     r"\bthreshold\b|edge weight|spearman.{0,20}threshold|false discovery|\bFDR\b|"
     r"multiple (?:comparison|testing|test)|\bpermutation\b|Benjamini"),
    ("depth / sampling completeness",
     r"raref|sequencing depth|sampling (?:effort|completeness)|read depth|sequenc\w* coverage|"
     r"library size|subsampl"),
    ("code availability", r"\bcode\b.{0,30}(?:available|github|zenodo|figshare)|github\.com|zenodo\.org"),
    ("longitudinal / time series",
     r"longitudinal|time[- ]series|over time|repeated sampling|temporal dynamic"),
    ("rewiring rate",
     r"rewir|re-?wiring"),
]


def main():
    led = {int(r["idx"]): r for r in csv.DictReader(io.open(ABS, encoding="utf-8-sig", newline=""))}
    corpus = [int(r["idx"]) for r in csv.DictReader(io.open(QUEUE, encoding="utf-8-sig", newline=""))
              if str(r["p2_N4"]).strip() in ("1", "2", "3")]
    n = len(corpus)
    print("analytic corpus n = %d" % n)
    print("%-46s %6s %8s" % ("keyword", "count", "share"))
    for name, pat in REGEX:
        rx = re.compile(pat, re.I)
        c = sum(1 for i in corpus if rx.search(str(led[i]["abstract"] or "")))
        print("%-46s %6d %7.1f%%" % (name, c, 100 * c / n))
    print()
    print("对照正文现值：keystone 62 (8.9%) | hub 38 (5.5%) | host genetic 27 (3.9%) | host transcriptome 2 | "
          "cross-kingdom 11 (1.6%)")
    print("对照正文现值（报告标准）：node resolution 103 (14.8%) | data 46 (6.6%) | compositional 24 (3.4%) | "
          "threshold 22 (3.2%) | depth 13 (1.9%) | code 0 (0.0%)")


if __name__ == "__main__":
    main()
