"""论文 2 计数与锚点核验脚本（只读）。

用途：
  1. 从判读台账复算 N1 判定分布、方法类条数、年度分布、N3 宿主类别分布；
  2. 从第二遍 B 队列复算 N4 / N7；
  3. 抽取 §7 / §8 初稿里的 [[idx-NNN]] 锚点，回候选池核对标题与 DOI。

输出：公共\题录\_p2_verify_out.txt（UTF-8），供人工回读。
运行：以仓库根为当前工作目录。
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # 仓库根；脚本从任意 cwd 运行都可复算
LEDGER = ROOT / "公共" / "题录" / "判读台账_论文2_方案B_20261001.csv"
QUEUE = ROOT / "公共" / "题录" / "第二遍B_队列_论文2_20261001.csv"
POOL = ROOT / "公共" / "题录" / "语料_论文2_方案B_候选池_20261001.csv"
OUT = ROOT / "公共" / "题录" / "_p2_verify_out.txt"
CH_DIR = ROOT / "论文2_生物学" / "输出"


def main() -> None:
    lines: list[str] = []
    w = lines.append

    d = pd.read_csv(LEDGER, encoding="utf-8-sig")
    q = pd.read_csv(QUEUE, encoding="utf-8-sig")
    pool = pd.read_csv(POOL, encoding="utf-8-sig")

    w("## 1. 判读台账 N1 判定分布（候选池 %d 行）" % len(d))
    for k, v in d["verdict"].value_counts(dropna=False).items():
        w("  %-12s %5d  (%.2f%%)" % (k, v, 100 * v / len(d)))

    w("")
    w("## 2. 方法类记录（verdict=方法-疑论文1）")
    m = d[d["verdict"] == "方法-疑论文1"]
    w("  条数 %d / %d = %.2f%%" % (len(m), len(d), 100 * len(m) / len(d)))
    w("  刊物分布：")
    for k, v in m["journal"].value_counts().items():
        w("    %-45s %d" % (k, v))
    w("  idx 清单：%s" % ", ".join(str(i) for i in sorted(m["idx"])))

    w("")
    w("## 3. 年度分布")
    yc = d["year"].value_counts().sort_index()
    w("  候选池全量：")
    for y, c in yc.items():
        w("    %d  %4d" % (y, c))

    w("")
    w("## 4. N3 宿主类别分布（候选池全量）")
    for k, v in d["N3_host_type"].value_counts(dropna=False).items():
        w("    %-6s %5d" % (k, v))

    w("")
    w("## 5. 第二遍 B 队列 N4 / N7")
    w("  队列行数 %d" % len(q))
    w("  N4：")
    for k, v in q["p2_N4"].value_counts(dropna=False).items():
        w("    %-6s %5d" % (k, v))
    w("  N7：")
    for k, v in q["p2_N7_type"].value_counts(dropna=False).items():
        w("    %-10s %5d" % (k, v))

    w("")
    w("## 6. 逐条锚点核验（§7 / §8 初稿）")
    idx2row = {int(r.idx): r for r in pool.itertuples()}
    seen: dict[int, list[str]] = {}
    for f in sorted(CH_DIR.glob("第*章_*_v1_20261002.md")):
        txt = f.read_text(encoding="utf-8")
        for mm in re.finditer(r"\[\[idx-(\d+)\]\]", txt):
            seen.setdefault(int(mm.group(1)), []).append(f.name)
    w("  共 %d 个不同 idx 锚点" % len(seen))
    missing = [i for i in sorted(seen) if i not in idx2row]
    w("  缺失（候选池中找不到）：%s" % (missing or "无"))
    for i in sorted(seen):
        if i not in idx2row:
            continue
        r = idx2row[i]
        w("    idx=%-5d doi=%-38s year=%s j=%s" % (i, str(r.doi), r.year, str(r.journal)[:40]))
        w("             title=%s" % str(r.title)[:110])

    w("")
    w("## 7. 队列与台账交叉核对")
    for i in (129, 33, 85, 155, 219, 381, 1215, 413, 1272):
        row = d[d["idx"] == i]
        if len(row):
            r = row.iloc[0]
            w("  idx=%-5d verdict=%-12s note=%s" % (i, r["verdict"], str(r["note"])[:60]))

    OUT.write_text("\n".join(lines), encoding="utf-8")
    sys.stdout.write("written: %s (%d lines)\n" % (OUT, len(lines)))


if __name__ == "__main__":
    main()
