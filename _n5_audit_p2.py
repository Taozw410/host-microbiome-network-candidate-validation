# -*- coding: utf-8 -*-
"""N5 逐条指派质量抽验（第一批：抽样 + 打印待判批次）。

做法：从 211 条带有干预描述的记录里按固定种子抽 50 条，打印
「指派类别 / 记录当时的描述 / 摘要窗口」，供逐条判断两件事：
  (a) 描述 → 类别 的映射是否合理（映射层）；
  (b) 描述 → 摘要所述干预 是否一致（判读层）。
输出：`公共\\题录\\_n5_audit_batch_20261002.txt`（UTF-8）。
"""
import csv
import io
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
Q = os.path.join(ROOT, "公共", "题录", "第二遍B_队列_论文2_20261001.csv")
POOL = os.path.join(ROOT, "公共", "题录", "语料_论文2_方案B_候选池_20261001.csv")
LED = os.path.join(ROOT, "公共", "题录", "判读台账_论文2_方案B_20261001.csv")
OUT = os.path.join(ROOT, "公共", "题录", "_n5_audit_batch_20261002.txt")
SEED = 20261002
N = 50

BUCKETS = [
    ("dietary_feed", r"膳食|饲料|多糖|纤维|蛋白|饮食|生酮|低热量|茶饮|AGEs|组胺|薄荷醇|多酚|营养处理|母体营养|喂养"),
    ("probiotic_inoculation", r"益生菌|后生元|接种|定植|外源菌|菌群移植|FMT|移植"),
    ("antibiotic_antimicrobial", r"抗生素|抗微生物|克林霉素|药物联用|抗结核"),
    ("drug_compound_tcm", r"药物|中药|黄酮|小檗碱|姜黄素|葛根素|蛇床子|奥利司他|替米沙坦|化学|化合物|草药|提取物|针刺|电针|漱口水|氟化物|局部外用|核酸|纳米材料|纳米酶|光疗|疫苗"),
    ("exposure_toxicant", r"暴露|毒性|污染|塑料|微塑料|纳米塑料|重金属|铅|铊|汞|稀土|农药|除草剂|杀虫剂|PBDE|PCB|PFAS|氟|镉|砷|化合物暴露|毒物|油污|微囊藻|蓝藻"),
    ("host_genetic_manipulation", r"基因敲除|突变体|转基因|遗传模型|宿主代谢物|宿主基因型|杂交"),
    ("model_infection", r"造模|感染|寄生虫|疟原虫|沙门|病毒|结扎|肿瘤造模|VPA|EAE|睡眠剥夺"),
    ("management_husbandry", r"养殖密度|圈养|温度处理|缺氧|渗透压|盐度|饥饿|限时|放牧|空间|轮作"),
    ("clinical_treatment", r"治疗|放疗|正畸|抗精神病|乳果糖|奥美拉唑|免疫抑制|RCT|随机对照|园艺"),
    ("process_handling", r"无菌处理|体外|发酵|培养|底物|节点操控|激素|疫苗|无"),
]


def bucket(s):
    for k, p in BUCKETS:
        if re.search(p, s):
            return k
    return "other"


def clip(t, n=900):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t[:n]


def main():
    q = list(csv.DictReader(io.open(Q, encoding="utf-8-sig", newline="")))
    # 台账 idx = **去重后**的池内位置；候选池文件自带的 idx 列是**去重前**的位置，
    # 两者在第 1001 行（重复条）之后相差 1。必须用位置查表，不能用池的 idx 列。
    raw = list(csv.DictReader(io.open(POOL, encoding="utf-8-sig", newline="")))
    seen, uniq = set(), []
    for r in raw:
        k = (r.get("doi") or "").strip().lower() or (r.get("pmid") or "").strip() or r["title"].strip().lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    assert len(uniq) == 1401, len(uniq)
    pool = {str(i): uniq[i - 1] for i in range(1, len(uniq) + 1)}
    led = {r["idx"]: r for r in csv.DictReader(io.open(LED, encoding="utf-8-sig", newline=""))}

    withdesc = [r for r in q if (r.get("p2_N5_intervention") or "").strip()]
    lv3 = [r for r in q if str(r.get("p2_N4")) == "3"]
    lv3_no_desc = [r for r in lv3 if not (r.get("p2_N5_intervention") or "").strip()]
    print("level-3 records:", len(lv3), "| with description:", len(lv3) - len(lv3_no_desc),
          "| level-3 WITHOUT description:", len(lv3_no_desc),
          [r["idx"] for r in lv3_no_desc])
    print("records with description (incl. reclassified):", len(withdesc))

    ids = sorted(int(r["idx"]) for r in withdesc)
    sample = sorted(random.Random(SEED).sample(ids, N))
    byidx = {int(r["idx"]): r for r in q}

    lines = ["N5 per-record assignment audit - batch (seed=%d, n=%d)" % (SEED, N), ""]
    for k, i in enumerate(sample, 1):
        r = byidx[i]
        raw = r["p2_N5_intervention"].strip()
        cat = bucket(raw)
        ab = clip((pool.get(str(i), {}) or {}).get("abstract", ""))
        lines.append("[%02d] idx=%d | level=%s | assigned=%s | phrase=%s" % (k, i, r["p2_N4"], cat, raw))
        lines.append("     journal=%s (%s)" % (led.get(str(i), {}).get("journal", ""), r.get("year", "")))
        lines.append("     title=%s" % clip(r.get("title", ""), 160))
        lines.append("     abstract=%s" % ab)
        lines.append("")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("[落盘]", OUT)
    print("sample idx:", sample)


if __name__ == "__main__":
    main()
