# -*- coding: utf-8 -*-
"""软化词／绝对量词扫查（论文 2 合并稿）：逐条给出所在节与整句，供人工判定是否带计数。

输出：公共\\题录\\_softword_hits_20261002.txt（UTF-8），控制台同步打印。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"D:\CodexWork\Com-Net\论文2_生物学\输出\正文_合并稿_20261002.md"
OUT = r"D:\CodexWork\Com-Net\公共\题录\_softword_hits_20261002.txt"

PATTERNS = [
    ("most/mostly", r"\b(most|mostly)\b"),
    ("majority", r"\bmajority\b"),
    ("many/numerous", r"\b(many|numerous|a number of)\b"),
    ("generally/commonly/typically/usually/often/frequently",
     r"\b(generally|commonly|typically|usually|often|frequently)\b"),
    ("widely", r"\bwidely\b"),
    ("largely/predominantly", r"\b(largely|predominantly)\b"),
    ("almost all/nearly all", r"\b(almost all|nearly all)\b"),
    ("all/every", r"\b(all|every)\b"),
    ("always/never/universally", r"\b(always|never|universally)\b"),
    ("few/rarely/seldom", r"\b(few|rarely|seldom)\b"),
    ("tend to", r"\btend(s)? to\b"),
    ("significant(ly)", r"\bsignificant(ly)?\b"),
    ("prove/establish/demonstrate/show that",
     r"\b(proves?|establishes?|demonstrates?|shows? that)\b"),
    ("it is known/accepted/clear", r"\b(it is (well[- ])?(known|accepted|clear|established))\b"),
    ("broadly/in general", r"\b(broadly|in general)\b"),
]


def main():
    t = io.open(SRC, encoding="utf-8").read()
    if "## Tables" in t:
        t = t.split("## Tables")[0]
    lines = t.split("\n")
    sec = "front"
    hits = []
    for i, raw in enumerate(lines):
        if raw.startswith("#"):
            sec = raw.lstrip("# ").strip()[:52]
            continue
        if not raw.strip() or raw.strip().startswith("|"):
            continue
        # 拼出包含该行的整句（跨行）
        para = []
        j = i
        while j > 0 and lines[j - 1].strip() and not lines[j - 1].startswith("#"):
            j -= 1
        k = i
        while k + 1 < len(lines) and lines[k + 1].strip() and not lines[k + 1].startswith("#"):
            k += 1
        blob = " ".join(x.strip() for x in lines[j:k + 1])
        for s in re.split(r"(?<=[.!?])\s+", blob):
            for name, pat in PATTERNS:
                if re.search(pat, s, re.I):
                    hits.append((i + 1, sec, name, re.sub(r"\s+", " ", s).strip(), pat))
    seen = set()
    out = ["# 软化词命中清单（论文 2 合并稿，2026-10-02）", ""]
    n = 0
    for ln, sec, name, s, pat in hits:
        key = (sec, s)
        if key in seen:
            continue
        seen.add(key)
        # 只保留真正命中的模式名
        names = [nm for nm, p in PATTERNS if re.search(p, s, re.I)]
        n += 1
        out.append("[%02d] §%s | L%d | %s" % (n, sec, ln, "/".join(names)))
        out.append("     %s" % s)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("\n".join(out))
    print("\n[落盘] %s | 去重后 %d 条" % (OUT, n))


if __name__ == "__main__":
    main()
