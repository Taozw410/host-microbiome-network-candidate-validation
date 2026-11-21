# Host-microbiome network candidate validation

Reproducibility code and record-level data for:

> **From network nomination to biological test in host-associated microbiome research: a structured review for infection and vector studies**

This repository supports the article's defined corpus of 696 host-linked microbiome association-network records. The central descriptive count is:

- 84 records remained at microbial-internal description (level 1);
- 403 records related network structure to a host variable (level 2);
- 209 records reported a broad perturbation or independent validation (level 3);
- 4 of those 209 records tested a candidate nominated by the study's own network.

The repository was prepared from the frozen analysis artifacts used for the manuscript. Creating this repository did not involve a new literature search, rescreening, reclassification, or recalculation of the published counts.

## Contents

- `Supplementary_Data_S3_Record_Ledger_Acta_Tropica_20261121.csv`: public copy of the record-level screening and coding ledger. It contains 1,401 candidate records, of which 696 are marked `in_analytic_corpus=Y`. Internal citation-conversion keys were omitted; DOI and PMID identifiers remain.

- `Figure_1.pdf`: evidence-loss and host-system/network-complexity figure used in the manuscript.

- `Figure_2.pdf`: network-type figure used in the manuscript.

- `Graphical_Abstract.pdf`: graphical abstract accompanying the manuscript.

- `_verify_S3_p2.py`: recomputes the principal corpus-level counts from the record ledger.

- `_p2_verify_counts.py`: verifies text-level anchors and manuscript counts against the frozen source tables.

- `_p2_structural_analysis.py` and `_host_level_crosstab.py`: descriptive structural analysis of validation by host category and network complexity.

- `_make_figs_p2.py`, `_make_f5_p2.py`, and `_figlib2.py`: figure-generation utilities and code for the main figures.

- `_build_fulltext_sample.py`, `_fetch_fulltexts_26.py`, `_fulltext_evidence.py`, and `_revise_fulltext_blocks.py`: selection, retrieval, extraction, and audit utilities for the 26-record full-text check of the central count.

- `_n5_audit_p2.py`, `_recount_keywords_p2.py`, and `_softword_scan_p2.py`: auxiliary audits for intervention labels, keyword categories, and softened claims.

## Environment

The analysis used Python 3.12. Install the listed packages with:

```bash
python -m pip install -r requirements.txt
```

The original scripts were executed in the authors' project workspace and retain explicit source-path arguments where applicable. The included frozen ledger and figure PDFs are the authoritative outputs for the deposited version. If adapting the scripts to another directory layout, update only the input/output path variables; the coding rules and analysis definitions should not be changed.

## Data and code scope

- No new experimental data were generated.
- The corpus is a defined Europe PMC source set, not a claim of exhaustive systematic-review coverage.
- Network edges in source studies represent statistical associations, not confirmed interactions.
- Level 1-3 are analysis-design categories, not a study-quality scale.
- Sex and gender subgroup analyses were not possible because the corpus was coded at title-and-abstract depth.

## Manuscript availability

The manuscript, supplementary search strategy, screening note, and declarations are submitted with the article. This repository provides the analysis code, public record ledger, and figure outputs needed to inspect and reproduce the reported descriptive counts. Manuscript-specific typesetting and internal build utilities are intentionally excluded.
