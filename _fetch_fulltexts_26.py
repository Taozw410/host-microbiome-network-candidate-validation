# -*- coding: utf-8 -*-
"""抓取 26 篇全文：优先 Europe PMC fullTextXML（PMC OA），否则用 EPMC 记录里的全文链接/摘要。
落盘到 公共\\题录\\全文核对_20261117\\idx-NNN.txt，并写抓取日志。需联网（已获作者批准）。
"""
import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
Q = r"D:\CodexWork\Com-Net\公共\题录"
SAMPLE = os.path.join(Q, "全文核对_26_20261117.csv")
OUTDIR = os.path.join(Q, "全文核对_20261117")
LOG = os.path.join(Q, "全文核对_20261117_日志.json")
API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = "ComNet-paper2-fulltext/1.0 (research verification)"


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_xml(raw):
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?is)</(p|sec|title|abstract|caption|table-wrap|tr)>", "\n", t)
    t = re.sub(r"(?is)<[^>]+>", " ", t)
    t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t.strip()


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = list(csv.DictReader(io.open(SAMPLE, encoding="utf-8-sig", newline="")))
    log = []
    for r in rows:
        rid, pmcid, doi = r["record_id"], r["pmcid"].strip(), r["doi"].strip()
        path = os.path.join(OUTDIR, rid + ".txt")
        status, chars = "missing", 0
        try:
            if pmcid:
                raw = get("%s/%s/fullTextXML" % (API, pmcid))
                txt = strip_xml(raw)
                status, chars = "pmc_fulltext", len(txt)
            else:
                q = urllib.parse.quote_plus('DOI:"%s"' % doi) if doi else ""
                raw = get("%s/search?query=%s&format=json&resultType=core&pageSize=1" % (API, q))
                d = json.loads(raw.decode("utf-8"))
                res = (d.get("resultList") or {}).get("result") or []
                rec = res[0] if res else {}
                ids = ((rec.get("fullTextIdList") or {}).get("fullTextId") or [])
                pmc2 = next((x for x in ids if x.startswith("PMC")), "")
                if pmc2:
                    raw = get("%s/%s/fullTextXML" % (API, pmc2))
                    txt = strip_xml(raw)
                    status, chars = "pmc_fulltext_lookup", len(txt)
                else:
                    txt = strip_xml(json.dumps(rec, ensure_ascii=False).encode())
                    status, chars = "record_only", len(txt)
            io.open(path, "w", encoding="utf-8", newline="\n").write(txt)
        except Exception as exc:
            status = "error:%s" % type(exc).__name__
            if not os.path.exists(path):
                io.open(path, "w", encoding="utf-8", newline="\n").write("")
        log.append({"record_id": rid, "group": r["group"], "pmcid": pmcid, "doi": doi,
                    "status": status, "chars": chars})
        print("  %-9s %-8s %-20s %7d" % (rid, r["group"], status, chars))
        time.sleep(0.4)
    io.open(LOG, "w", encoding="utf-8").write(json.dumps(log, ensure_ascii=False, indent=1))
    ok = sum(1 for x in log if x["status"].startswith("pmc"))
    print("\n全文 %d/%d | 日志 %s" % (ok, len(log), LOG))


if __name__ == "__main__":
    main()
