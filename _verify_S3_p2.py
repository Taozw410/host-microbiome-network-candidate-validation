# -*- coding: utf-8 -*-
"""用 S3 这份对外台账复算正文的全部语料级数字（自足性检查）。"""
import csv
import io
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
OUT = "论文2_生物学/输出/S3_逐条筛选台账_20261002.csv"
TARGET = {
    "rows": 1401, "in_corpus": 696,
    "level1": 84, "level2": 403, "level3": 209,
    "net_internal": 578, "net_multiomics": 104, "net_crosskingdom": 12, "net_hostnodes": 2,
    "excl_no_host": 631, "excl_methods": 47, "excl_review": 18, "excl_nonresearch": 9,
    "interv_diet": 56, "interv_drug": 39, "interv_probiotic": 32, "interv_exposure": 21,
    "interv_model": 18, "interv_other": 11, "interv_antibiotic": 12, "interv_management": 9,
    "interv_hostgenetic": 7, "interv_process": 3, "interv_clinical": 3,
    "cited": 53,
    "net_directed": 4, "miss_audit": 68,
    "mo_coupled": 19, "mo_border": 3, "mo_parallel": 82,
    "title_only": 1, "human": 304, "animal": 305, "plant": 86, "undetermined": 1,
    "verification_fulltext": 18, "verification_record": 8,
    "audit_confirmed": 192, "audit_eligible": 2, "audit_unresolved": 6,
    "reassessment_pass": 705,
}


def main():
    rows = list(csv.DictReader(io.open(OUT, encoding="utf-8-sig", newline="")))
    g = {}
    g["rows"] = len(rows)
    g["in_corpus"] = sum(1 for r in rows if r["in_analytic_corpus"] == "Y")
    for k, v in (("level1", "1"), ("level2", "2"), ("level3", "3")):
        g[k] = sum(1 for r in rows if r["level"] == v)
    for k, v in (("net_internal", "microbial_internal"), ("net_multiomics", "multi_omics"),
                 ("net_crosskingdom", "cross_kingdom"), ("net_hostnodes", "host_as_nodes")):
        g[k] = sum(1 for r in rows if r["network_type"] == v)
    for k, v in (("excl_no_host", "excluded_no_host_variable"),
                 ("excl_methods", "excluded_methods_paper"),
                 ("excl_review", "excluded_review_background"),
                 ("excl_nonresearch", "excluded_non_research")):
        g[k] = sum(1 for r in rows if r["screening_verdict"] == v)
    c = Counter(r["intervention_category"] for r in rows if r["intervention_category"])
    for k, v in (("interv_diet", "dietary_feed"), ("interv_drug", "drug_compound_tcm"),
                 ("interv_probiotic", "probiotic_inoculation"), ("interv_exposure", "exposure_toxicant"),
                 ("interv_model", "model_infection"), ("interv_other", "other"),
                 ("interv_antibiotic", "antibiotic_antimicrobial"),
                 ("interv_management", "management_husbandry"),
                 ("interv_hostgenetic", "host_genetic_manipulation"),
                 ("interv_process", "process_handling"), ("interv_clinical", "clinical_treatment")):
        g[k] = c.get(v, 0)
    g["cited"] = len({r["record_id"] for r in rows if r["cited_in_manuscript"] == "Y"})
    g["net_directed"] = sum(1 for r in rows if r["intervention_target_network_directed"] == "Y")
    g["miss_audit"] = sum(1 for r in rows if r["miss_audit_sample"] == "Y")
    g["mo_coupled"] = sum(1 for r in rows if r["multiomics_design"] == "coupled")
    g["mo_border"] = sum(1 for r in rows if r["multiomics_design"] == "borderline")
    g["mo_parallel"] = sum(1 for r in rows if r["multiomics_design"] == "parallel")
    g["title_only"] = sum(1 for r in rows if r["coding_depth"] == "title_only")
    for k in ("human", "animal", "plant", "undetermined"):
        g[k] = sum(1 for r in rows if r["in_analytic_corpus"] == "Y" and r["host_category"] == k)
    g["verification_fulltext"] = sum(1 for r in rows if r["targeted_verification_depth"] == "full_text")
    g["verification_record"] = sum(1 for r in rows if r["targeted_verification_depth"] == "record_level")
    g["audit_confirmed"] = sum(1 for r in rows if r["exclusion_audit_result"] == "confirmed_exclusion")
    g["audit_eligible"] = sum(1 for r in rows if r["exclusion_audit_result"] == "eligible")
    g["audit_unresolved"] = sum(1 for r in rows if r["exclusion_audit_result"] == "unresolved")
    g["reassessment_pass"] = sum(1 for r in rows if r["reassessment_pass"] == "Y")
    ok = True
    for k, t in TARGET.items():
        same = g[k] == t
        ok &= same
        print("%-20s %6s %6s %s" % (k, g[k], t, "OK" if same else "MISMATCH"))
    print("\nALL MATCH:", ok)
    print("no-DOI rows:", sum(1 for r in rows if not r["doi"].strip()),
          "| cited rows carrying citation_key:",
          sum(1 for r in rows if r["cited_in_manuscript"] == "Y" and r["citation_key"]))


if __name__ == "__main__":
    main()
