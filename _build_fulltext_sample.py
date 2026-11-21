# -*- coding: utf-8 -*-
"""建 26 篇全文核对样本：6 条网络驱动正例 + 20 条随机广谱扰动负例（seed 20261117）。
输出 CSV（record_id, doi, pmid, pmcid, title, group），供抓取与逐条核对。
"""
import csv
import io
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")
Q = r"D:\CodexWork\Com-Net\公共\题录"
S3 = r"D:\CodexWork\Com-Net\论文2_生物学\输出\S3_逐条筛选台账_20261002.csv"
POOL = os.path.join(Q, "语料_论文2_方案B_候选池_20261001.csv")
LED = os.path.join(Q, "判读台账_论文2_方案B_20261001.csv")
OUT = os.path.join(Q, "全文核对_26_20261117.csv")

POS = ["idx-101", "idx-477", "idx-597", "idx-727", "idx-917", "idx-1364"]


def main():
    rows = [r for r in csv.DictReader(io.open(S3, encoding="utf-8-sig", newline=""))
            if r["in_analytic_corpus"] == "Y"]
    neg = [r["record_id"] for r in rows if r["level"] == "3" and r["record_id"] not in POS]
    rnd = random.Random(20261117)
    sample = POS + sorted(rnd.sample(neg, 20), key=lambda s: int(s.split("-")[1]))
    pool = list(csv.DictReader(io.open(POOL, encoding="utf-8-sig", newline="")))
    seen, uniq = set(), []
    for r in pool:
        k = (r.get("doi") or "").strip().lower() or (r.get("pmid") or "").strip() or r["title"].strip().lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    by_idx = {str(i): uniq[i - 1] for i in range(1, len(uniq) + 1)}
    led = {r["idx"]: r for r in csv.DictReader(io.open(LED, encoding="utf-8-sig", newline=""))}
    out = []
    for rid in sample:
        i = rid.replace("idx-", "")
        p = by_idx.get(i, {})
        out.append({"record_id": rid, "group": "positive" if rid in POS else "negative",
                    "doi": p.get("doi", ""), "pmid": p.get("pmid", ""),
                    "pmcid": p.get("pmcid", ""), "title": p.get("title", "") or led[i]["title"],
                    "journal": p.get("journal", ""), "year": p.get("year", "")})
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    pmc = sum(1 for r in out if r["pmcid"])
    print("[落盘]", OUT)
    print("样本 %d | 有 PMCID 的 %d | 正例 %d | 负例 %d" % (len(out), pmc, len(POS), len(out) - len(POS)))
    for r in out:
        print("  %-9s %-8s pmcid=%-12s %s" % (r["record_id"], r["group"], r["pmcid"] or "-", r["title"][:70]))


if __name__ == "__main__":
    main()
