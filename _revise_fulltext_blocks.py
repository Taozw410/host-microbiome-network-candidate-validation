# -*- coding: utf-8 -*-
"""第二轮修订：全局数字 + §5.2／§7.3 叙述 + Table 3 + S3/S2 更新。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
O = r"D:\CodexWork\Com-Net\论文2_生物学\输出"
SCR = r"D:\CodexWork\Com-Net\论文2_生物学\脚本"

FILES = [os.path.join(O, f) for f in os.listdir(O)
         if (f.startswith("第") or f.startswith("表T")) and f.endswith(".md")]


def flex(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))


def main():
    # 1) 全局数字
    for p in FILES:
        t = io.open(p, encoding="utf-8").read()
        o = t
        t = t.replace("2.9%", "1.9%").replace("8.6%", "6.1%").replace("97.1%", "98.1%")
        if t != o:
            io.open(p, "w", encoding="utf-8", newline="\n").write(t)
            print("num ", os.path.basename(p))

    # 2) 结构性块
    ops = [
        ("第5章_缺口_v1_20261002.md",
         "left **6 that actually target a network-identified candidate**: The six records and the endpoint each one scores are listed in Table 3",
         "left **4 that actually test a network-identified candidate in the biological system**: The four records and the endpoint each one scores are listed in Table 3"),
        ("第5章_缺口_v1_20261002.md",
         "Two features of the six are worth stating rather than smoothing over. First, they are not all the same kind of test: two validate microbial attributes (colonisation resistance), two validate microbial interactions (predicted partners), and only two score a host endpoint. Second, four of the six come from two research groups working on tick and colonisation-resistance systems; the practice is real but is not yet a general habit. Third, one of the six [[idx-101]] is a protocol article: it specifies and demonstrates the network-node manipulation and scores colonisation resistance rather than reporting a completed host outcome. It is retained because the manipulation is performed within that protocol and its endpoint is measured there; a reader who required a completed host-outcome study would count five, which is why this case is stated explicitly instead of being folded into the number.",
         "Two features of the four are worth stating rather than smoothing over. First, they are not all the same kind of test: two validate microbial interactions (predicted partners) and two score a host endpoint (tick feeding and performance). Second, two of the four are anti-tick vaccines from one research group; the other two come from independent laboratories. The count changed when the six candidates were read in full. Two of the original six, a protocol article that only simulates node removal [[idx-101]] and a study that applies node removal to a published network [[idx-597]], do not test the candidate in the biological system and are excluded here; of the remaining four, three are confirmed from the full text and one [[idx-477]] from the abstract alone because no full text was retrievable."),
        ("第7章_争议_v2_20261002.md",
         "One of the six is a protocol article that specifies the node manipulation rather than reporting a completed host outcome (Section 5.2); it is counted here, and the effect of dropping it is stated in Section 5.2.",
         "Two of the original six candidates did not test the candidate in the biological system and were excluded after full-text reading (Section 5.2); the count reported here is four."),
        ("第11章_结论_v1_20261002.md",
         "only two of the six network-directed interventions score a host endpoint at all",
         "only two of the four network-directed interventions score a host endpoint at all"),
        ("第8章_可证伪研究议程_v2_20261002.md",
         "but only **6 records (1.9%)** in which a candidate identified by a network is the object of",
         "but only **4 records (1.9%)** in which a candidate identified by a network is the object of"),
        ("第8章_可证伪研究议程_v2_20261002.md",
         "rises above the current 1.9%** (upper bound 6.1%)",
         "rises above the current 1.9%** (upper bound 6.1%)"),
        ("第10章_限制与范围_v1_20261002.md",
         "For the central quantity of Section 5, 6 of 209 interventional records, the sampling interval alone is 1.3–6.1%, and the miss-audit raises the upper bound to 6.1% because a random re-check of 50 records found no additional case.",
         "For the central quantity of Section 5, 4 of 209 interventional records, the sampling interval alone is 0.8–4.8%, and the miss-audit raises the upper bound to 6.1% because random re-checks of 70 records found no additional case."),
        ("表T3_三档与靶向验证_20261002.md",
         "| A candidate the study's own network identified (hub, keystone, driver, predicted interaction) | **6** | **1.9%** | abstract-level, plus a 50-record miss audit |",
         "| A candidate the study's own network identified and tested in the biological system | **4** | **1.9%** | full text for 3 of 4; a 70-record miss audit |"),
        ("表T3_三档与靶向验证_20261002.md",
         "| A broad perturbation (antibiotics, faecal transfer, diet, drugs, toxicants, host gene knockout), outcome observed afterwards | 203 | 98.1% | abstract-level, plus a 50-record miss audit |",
         "| A broad perturbation, or in-silico node removal without a biological test (antibiotics, faecal transfer, diet, drugs, toxicants, host knockout) | 205 | 98.1% | full text for 18 of 26 sampled; a 70-record miss audit |"),
        ("表T3_三档与靶向验证_20261002.md",
         "**95% upper bound on the network-directed share: 6.1%.** The sampling interval on 6/209 alone is 1.3–6.1%; a random re-read of 50 records from the broad-perturbation set found no additional targeted validation (0/50), and under a rule-of-three bound the miss rate is at most about 6%, which raises the upper bound to 6.1%. As a share of the analytic corpus, network-directed validation is 0.9% (6/696).",
         "**95% upper bound on the network-directed share: 6.1%.** The sampling interval on 4/209 alone is 0.8–4.8%; random re-reads of 70 records from the broad-perturbation set found no additional biological test (0/70), and under a rule-of-three bound the miss rate is at most about 4.3%, which raises the upper bound to 6.1%. As a share of the analytic corpus, network-directed validation is 0.6% (4/696)."),
        ("表T3_三档与靶向验证_20261002.md",
         "### 3c. The six network-directed records, by endpoint",
         "### 3c. The four network-directed records, by endpoint"),
        ("表T3_三档与靶向验证_20261002.md",
         "| Microbial attribute (colonisation resistance) | 2 | `[[idx-101]]`, `[[idx-597]]` |\n",
         ""),
        ("表T3_三档与靶向验证_20261002.md",
         "That makes 1.9% a lower bound on practice. The intervention-type composition of the 203 records",
         "That makes 1.9% a lower bound on practice. The intervention-type composition of the 205 records"),
    ]
    for fn, old, new in ops:
        p = os.path.join(O, fn)
        t = io.open(p, encoding="utf-8").read()
        pat = flex(old)
        t2, n = pat.subn(lambda m: new, t)
        io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
        print(("OK  " if n else "MISS"), fn[:26], n)

    # 3) 5.4 比值与 696 分母
    p = os.path.join(O, "第5章_缺口_v1_20261002.md")
    t = io.open(p, encoding="utf-8").read()
    t = t.replace("as a share of the analytic corpus it is 0.9%", "as a share of the analytic corpus it is 0.6%")
    t = t.replace("**403 of 696 records (57.9%) produce a candidate or a network property that is related to a host state; 6 of 696 (0.9%) test a candidate the network proposed.** The ratio is roughly one test for every sixty-seven host-associated network results.",
                  "**403 of 696 records (57.9%) produce a candidate or a network property that is related to a host state; 4 of 696 (0.6%) test a candidate the network proposed.** The ratio is roughly one test for every hundred host-associated network results.")
    t = t.replace("2.9% is too low", "1.9% is too low")
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

    # 4) S3 与 S2：NETWORK_DIRECTED 去掉 101/597；S2.5 段改写
    pb = os.path.join(SCR, "_build_SP_p2.py")
    b = io.open(pb, encoding="utf-8").read()
    b = b.replace('NETWORK_DIRECTED = {"idx-101", "idx-597", "idx-727", "idx-917", "idx-477", "idx-1364"}',
                  'NETWORK_DIRECTED = {"idx-727", "idx-917", "idx-477", "idx-1364"}')
    b = re.sub(r'    w\("\*\*A note on protocol articles\.\*\*.*?w\(""\)',
               '    w("**A note on full-text verification.** The six candidates identified at abstract level were read in full '
               'where a full text was available. Two of them, a protocol article that only simulates node removal and a study '
               'that applies node removal to a published network, do not test the candidate in the biological system and are '
               'excluded from the count; three of the remaining four were confirmed from the full text and one from the '
               'abstract alone. The Twenty-record negative sample was checked the same way and added no case, so the '
               'miss audit is 0 of 70.")\n    w("")', b, flags=re.S)
    io.open(pb, "w", encoding="utf-8", newline="\n").write(b)
    print("S3 集合与 S2.5 段已改")

    pv = os.path.join(SCR, "_verify_S3_p2.py")
    v = io.open(pv, encoding="utf-8").read().replace('"net_directed": 6', '"net_directed": 4')
    io.open(pv, "w", encoding="utf-8", newline="\n").write(v)
    print("verify 目标 6→4")


if __name__ == "__main__":
    main()
