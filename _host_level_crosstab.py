# -*- coding: utf-8 -*-
"""B4：宿主类别（人／动物／植物）× 三档 分层表。
宿主类别优先用判读台账 N3_host_type（筛选者判定），缺失处用可复算的关键词规则补；
同时报告两种来源的一致率，产出 `公共\\题录\\宿主类别×三档_论文2_20261002.md`。
"""
import csv
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
QD = os.path.join(ROOT, "公共", "题录")
LED = os.path.join(QD, "判读台账_论文2_方案B_20261001.csv")
QUE = os.path.join(QD, "第二遍B_队列_论文2_20261001.csv")
ABS = os.path.join(QD, "摘要_论文2_按台账idx_20261002.csv")
OUT = os.path.join(QD, "宿主类别×三档_论文2_20261002.md")

HUMAN = (r"patient|patients|human|volunteer|infant|infants|children|child|adults?|clinical|cohort|"
         r"IBD|inflammatory bowel|obesity|diabet|schizophren|depress|autis|allerg|asthma|cirrhos|"
         r"periodont|dental|caries|breast milk|mother|women|men\b|elderly|colorectal|kidney stone")
ANIMAL = (r"mice|mouse|murine|rat\b|rats\b|pig\b|pigs|swine|porcine|cattle|cow|cows|bovine|dairy|sheep|goat|"
          r"chicken|broiler|poultry|duck|goose|fish|zebrafish|salmon|shrimp|prawn|crab|oyster|mussel|coral|tick|"
          r"mosquito|honeybee|bee\b|silkworm|nematode|Caenorhabditis|Drosophila|monkey|macaque|panda|hamster|"
          r"loach|canid|dog|cat\b|rabbit|horse|buffalo|yak|frog|snake|lizard|sea cucumber|abalone|scallop|"
          r"gastropod|snail|Tenebrio|Hymenoptera|Ixodes|Anaplasma|canaries|minnow|Gobiocypris")
PLANT = (r"plant|plants|root\b|roots|rhizosphere|rhizoplane|phyllosphere|leaf|leaves|endophyt|seed\b|seedling|"
         r"tomato|rice|wheat|maize|corn|soybean|apple|grape|vine\b|tea plant|Coffea|citrus|banana|potato|barley|"
         r"sorghum|millet|peanut|cotton|cucumber|pepper|strawberry|blueberry|canola|rapeseed|moss|Arabidopsis|"
         r"Miscanthus|Astragalus|Panax|halophyte|mangrove|Pinus|buckwheat|Platycodon|crop|agroforestry")


def kw(text):
    t = text.lower()
    h = len(re.findall(HUMAN, t))
    a = len(re.findall(ANIMAL, t))
    p = len(re.findall(PLANT, t))
    m = max(h, a, p)
    if m == 0:
        return "undetermined", (h, a, p)
    winners = [k for k, v in (("human", h), ("animal", a), ("plant", p)) if v == m]
    return (winners[0] if len(winners) == 1 else "mixed"), (h, a, p)


def main():
    led = {r["idx"]: r for r in csv.DictReader(io.open(LED, encoding="utf-8-sig", newline=""))}
    ab = {r["idx"]: (r.get("title", "") + " " + (r.get("abstract") or ""))
          for r in csv.DictReader(io.open(ABS, encoding="utf-8-sig", newline=""))}
    corpus = [(r["idx"], str(r["p2_N4"]).strip()) for r in csv.DictReader(
        io.open(QUE, encoding="utf-8-sig", newline="")) if str(r["p2_N4"]).strip() in ("1", "2", "3")]
    n3map = {"人": "human", "动": "animal", "植": "plant"}

    rows, agree, both = [], 0, 0
    for idx, lvl in corpus:
        n3 = n3map.get(str(led[idx].get("N3_host_type") or "").strip())
        k, scores = kw(ab.get(idx, ""))
        final = n3 or k
        if n3 and k in ("human", "animal", "plant"):
            both += 1
            agree += (n3 == k)
        rows.append((idx, lvl, n3 or "", k, final, scores))

    tab = {}
    for _, lvl, _, _, final, _ in rows:
        tab.setdefault(final, {}).setdefault(lvl, 0)
        tab[final][lvl] += 1
    order = ["human", "animal", "plant", "mixed", "undetermined"]
    lines = ["# 宿主类别 × 三档（B4，2026-10-02）", "",
             "内部｜来源：判读台账 `N3_host_type`（筛选者判定，优先）＋ 缺失处由可复算关键词规则补齐",
             "内部｜（关键词表见脚本 `论文2_生物学\\脚本\\_host_level_crosstab.py`）；",
             "内部｜两种来源同时在场的 %d 条中一致 %d 条（%.1f%%）。" % (both, agree, 100.0 * agree / both if both else 0),
             "内部｜**该表目前只落在补充材料；正文引用待作者确认。**", "",
             "| Host category | Level 1 (no host variable) | Level 2 (host-state association) | Level 3 (intervention or validation) | Total | Level 3 share |",
             "| --- | --- | --- | --- | --- | --- |"]
    tot_all = sum(sum(v.values()) for v in tab.values())
    for k in order:
        if k not in tab:
            continue
        v = tab[k]
        t = sum(v.values())
        lines.append("| %s | %d | %d | %d | %d | %.1f%% |" % (
            k, v.get("1", 0), v.get("2", 0), v.get("3", 0), t, 100.0 * v.get("3", 0) / t))
    lines.append("| **All** | %d | %d | %d | %d | %.1f%% |" % (
        sum(1 for x in rows if x[1] == "1"), sum(1 for x in rows if x[1] == "2"),
        sum(1 for x in rows if x[1] == "3"), tot_all,
        100.0 * sum(1 for x in rows if x[1] == "3") / tot_all))
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\n[落盘]", OUT, "| 两种来源一致率: %d/%d" % (agree, both))


if __name__ == "__main__":
    main()
