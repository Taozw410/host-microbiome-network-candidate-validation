# -*- coding: utf-8 -*-
"""从 26 篇全文（或记录级文本）中抽取"网络候选 × 干预"的证据窗口，供逐条判定。"""
import csv
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
Q = r"D:\CodexWork\Com-Net\公共\题录"
SAMPLE = os.path.join(Q, "全文核对_26_20261117.csv")
D = os.path.join(Q, "全文核对_20261117")

NET = r"keystone|hub|network|node|predicted interaction|co-?occurrence|centralit|module"
ACT = (r"manipulat|inoculat|remov|ablat|knockout|knock-out|delet|co-?cultur|cultur|vaccin|challeng|"
       r"transplant|coloniz|colonis|gnotobiotic|supplement|intervention|treat")


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "positive"
    rows = [r for r in csv.DictReader(io.open(SAMPLE, encoding="utf-8-sig", newline=""))
            if r["group"] == group]
    for r in rows:
        rid = r["record_id"]
        p = os.path.join(D, rid + ".txt")
        t = io.open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else ""
        flat = re.sub(r"\s+", " ", t)
        print("=" * 96)
        print("%s | %s | %s" % (rid, r["group"], r["title"][:110]))
        print("  chars=%d | pmcid=%s" % (len(t), r["pmcid"] or "-"))
        sents = re.split(r"(?<=[.!?])\s+", flat)
        hits = []
        for s in sents:
            if re.search(NET, s, re.I) and re.search(ACT, s, re.I):
                hits.append(s.strip())
        seen = set()
        shown = 0
        for s in hits:
            k = s[:60]
            if k in seen:
                continue
            seen.add(k)
            print("   •", s[:520])
            shown += 1
            if shown >= 4:
                break
        if not hits:
            # 退化：只给含 network 的首句
            for s in sents:
                if re.search(NET, s, re.I):
                    print("   (无干预共现句) •", s[:420])
                    break


if __name__ == "__main__":
    main()
