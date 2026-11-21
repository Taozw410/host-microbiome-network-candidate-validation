# -*- coding: utf-8 -*-
"""把核心计数从 6/209（2.9%，上界 8.6%）改为 4/209（1.9%，上界 6.1%），并同步全文核对后的叙述。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
O = r"D:\CodexWork\Com-Net\论文2_生物学\输出"

# (文件名, 旧串, 新串) —— 空白宽松匹配
REPL = [
    ("第0章_摘要_v1_20261002.md",
     "Among the 209 interventional records, only **6 (2.9%; 95% upper bound 8.6%)** intervene on a candidate that the study's own network identified, while **203 (97.1%)** apply a broad perturbation",
     "Among the 209 interventional records, only **4 (1.9%; 95% upper bound 6.1%)** test a candidate that the study's own network identified in the biological system, while **205 (98.1%)** apply a broad perturbation"),
    ("第1章_引言_v1_20261002.md",
     "Among the 209 interventional records, only **6 (2.9%; 95% upper bound 8.6%)** intervene on a candidate that the network itself identified, while **203 (97.1%)**",
     "Among the 209 interventional records, only **4 (1.9%; 95% upper bound 6.1%)** test a candidate that the network itself identified in the biological system, while **205 (98.1%)**"),
    ("第11章_结论_v1_20261002.md",
     "Among the 209 interventional records, only **6 (2.9%; 95% upper bound 8.6%)** intervene on a candidate that the network itself identified, while 203 (97.1%)",
     "Among the 209 interventional records, only **4 (1.9%; 95% upper bound 6.1%)** test a candidate that the network itself identified in the biological system, while 205 (98.1%)"),
    ("第5章_缺口_v1_20261002.md",
     "**6 of 209 = 2.9%** (95% upper bound 8.6%; see Section 5.4). The other **203 records (97.1%)**",
     "**4 of 209 = 1.9%** (95% upper bound 6.1%; see Section 5.4). The other **205 records (98.1%)**"),
    ("第7章_争议_v2_20261002.md",
     "Among those 209, only **6 (2.9%; 95% upper bound 8.6%)** use a candidate that the network itself identified",
     "Among those 209, only **4 (1.9%; 95% upper bound 6.1%)** test a candidate that the network itself identified in the biological system"),
    ("第8章_可证伪研究议程_v2_20261002.md",
     "Network-directed manipulation appears in **6 of 209 interventional records (2.9%; 95% upper bound 8.6%)**",
     "Network-directed manipulation appears in **4 of 209 interventional records (1.9%; 95% upper bound 6.1%)**"),
    ("表T4_研究议程_20261002.md",
     "H3 — network-directed manipulation is 6 of 209 interventional records (2.9%; 95% upper bound 8.6%), and only 2 of those 6 score a host endpoint",
     "H3 — network-directed manipulation is 4 of 209 interventional records (1.9%; 95% upper bound 6.1%), and 2 of those 4 score a host endpoint"),
    ("第10章_限制与范围_v1_20261002.md",
     "For the central quantity of Section 5, 6 of 209 interventional records, the sampling interval alone is 1.3–6.1%, and the miss-audit raises the upper bound to 8.6% because a random re-check of 50 records found no additional case.",
     "For the central quantity of Section 5, 4 of 209 interventional records, the sampling interval alone is 0.8–4.8%, and the miss-audit raises the upper bound to 6.1% because random re-checks of 70 records (50 plus 20) found no additional case."),
    ("第6章_与既有综述的边界_v1_20261002.md",
     "the field tests what its networks propose\" (2.9%, 95% upper bound 8.6%)",
     "the field tests what its networks propose\" (1.9%, 95% upper bound 6.1%)"),
    ("第3章_网络被用来问什么_v1_20261002.md",
     "appear at 2.9%, 1.7% and 0.3% respectively",
     "appear at 1.9%, 1.7% and 0.3% respectively"),
    ("第9章_检验需求_v1_20261002.md",
     "in 6 of 209 interventional records (2.9%), and only **two of those six score a host endpoint**",
     "in 4 of 209 interventional records (1.9%), and only **two of those four score a host endpoint**"),
]


def flex(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))


def main():
    ok = miss = 0
    for fn, old, new in REPL:
        p = os.path.join(O, fn)
        t = io.open(p, encoding="utf-8").read()
        t2, n = flex(old).subn(lambda m: new, t)
        if n:
            io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
            ok += 1
            print("OK  %-30s x%d" % (fn[:28], n))
        else:
            miss += 1
            print("MISS %-30s | %s" % (fn[:28], old[:60]))
    print("成功 %d / 失败 %d" % (ok, miss))


if __name__ == "__main__":
    main()
