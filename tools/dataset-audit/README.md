# Local Swedish qualifier audit

**WITHDRAWN CLASSIFICATION:** `finish.py` and the `nonredundant-*` outputs do
not establish additional information. They label failed matches as findings.
Use only the extraction as evidence; see `DATASET-MODEL.md` for the correction.
Do not rerun this classifier as a substitute for reading the measures.

Design evidence, not a model validator or production normalizer. Reads the local
`dataset_languages.csv` only; never calls the catalog, an upstream API, or a paid
service. Dependencies: Python standard library. Run from the repository root.

```powershell
uv run --no-sync python tools/dataset-audit/audit.py extract
uv run --no-sync python tools/dataset-audit/audit.py run --through 1
uv run --no-sync python tools/dataset-audit/audit.py inspect --through 1 --field refperiod
# Inspect survivors between rule groups; increase --through up to 10.
uv run --no-sync python tools/dataset-audit/audit.py run --through 10
uv run --no-sync python tools/dataset-audit/audit.py verify --through 10
uv run --no-sync python tools/dataset-audit/audit.py show --dataset TAB3815
uv run --no-sync python -m unittest discover -s tools/dataset-audit -p "test_*.py"
```

`--source` and `--output` override defaults. Output stays in ignored
`tmp/qualifier-audit-sv/`; source records, including notes and full category maps,
are retained. The CSV has no header; column mapping and its unusual apostrophe
escaping are explicit in `extract`/`csv_rows`. Extraction checks row width,
identity agreement, duplicate identities and source stability. `source.json`
records the source SHA-256, byte size and counts. Each run records the script hash.

## Final grouped pass — use this result

The final working lists are in `tmp/qualifier-audit-sv/final/`. Use
`nonredundant-datasets.csv` for identities and `nonredundant-attributes.csv` for
specific values. `scope-questions.csv` keeps ambiguous ownership/base comparisons
separate. `decisions.jsonl` retains the complete classification ledger.

```powershell
uv run --no-sync python tools/dataset-audit/finish.py
```

This reuses saved `09-rules/decisions.jsonl` and `records.jsonl`, applying grouped
semantic deductions only to survivors. It takes seconds; **do not replay all
stages** when refining these deductions. To recreate inputs from scratch, run
`extract` once, `run --through 9` once, then `finish.py`.

`nonredundant` is the rule-based working classification: no equivalent was
recognized after the grouped comparisons. It is not a claim of individually
certified semantic uniqueness. Stock/Flow and price-source classifications can
also be inaccurate upstream. The output informs the model discussion; it does
not automatically approve fields or delete source values.

## Scope and files

Extract **every `sv` record containing any** dimension extension `refperiod`,
`basePeriod`, `measuringType`, `priceType`, or `adjustment`, including empty values.
This is a language filter, not a provider-country filter. The Swedish-provider
subset is identified separately using the country grouping documented in
`DATASET-MODEL.md`.

- `records.jsonl`: complete candidate documents with CSV row numbers.
- `00-candidates.jsonl`: every attribute occurrence, with stable IDs including
  provider, dataset, language, owning dimension/category and field.
- `NN-rules/decisions.jsonl`: one decision per occurrence, including exclusion
  rule and evidence location/value; no silent deletion.
- `NN-rules/datasets.csv`: all candidate dataset identities and status counts.
  Each row is one distinct dataset because only `sv` is selected.
- `NN-rules/remaining.jsonl`: unresolved occurrences, **not a proven unique set**.
- `NN-rules/inspection.json`: groups by field/value/status, with three examples,
  primary text context, owning category and actual time categories/notes.
- `NN-rules/summary.json`: occurrence counts and distinct-dataset counts. Dataset
  status groups overlap: one dataset can contain both repeated and unclear values.
- `NN-rules/verification.json`: reconciles all candidate IDs/values exactly,
  verifies extraction hashes and records the decision-file hash.
- `NN-rules/additional-explicit.csv`: the conservative positive date findings
  produced by verification. This is a subset, not the complete semantic answer
  for all five fields.

## Rule groups and inspection trail

| Through | Inspection that motivated the next rule group |
|---|---|
| 1 | Separate empty values and enum defaults. `Other`, `NotApplicable`, `None` are **not** declared meaningless; keep them separately visible. |
| 2 | `År`/`Kalenderår` repeat Annual; analogous exact grain names repeat the corresponding time unit. This does not remove December 31 or a measurement month from annual data. |
| 3 | Compare full phrases and metric-specific index bases, not any year appearing in a coverage range. |
| 4 | Inspect election/mandate/school-year wording, numeric date spelling and price-base labels. Date matches elsewhere remain review candidates because their scope can differ. |
| 5 | TAB3840 and TAB6406 show price/adjustment in the metric label. AKU tables can have adjustment alternatives in a separate dimension; those are scope questions. |
| 6 | Broader prose searches and Stock/Flow/Average wording identify review candidates. A salary average is not automatically the same thing as temporal MeasuringType=Average. |
| 7 | Annual salary tables can already say monthly salary in their metric labels. This is a unit-period comparison, not an inferred observation date. |
| 8 | TAB3815 proves reference years must be compared to their **own** metric label. TAB3257's historical May/November and later May-only categories agree with its notes. Training-survey notes explicitly explain June/December and covered half-years. |
| 9 | Compare remaining numeric reference periods with actual time categories. A match to one of several periods or a mismatch is a **scope review**, not automatically an error. |
| 10 | For simple day/month references on annual, year-coded tables, search every other string/key in the document, including time codes and links. Alternative date encodings, month wording and possible year-boundary paraphrases block a positive finding. Remaining matches establish an additional **explicit date statement** in the local document, not external correctness. |

During inspection, TAB69 also exposed a limitation of literal matching: its
`1994K1` base period accompanies alternative labels stating `feb 1994=100`.
Do not call it confirmed additional information just because the exact code
is absent from the labels. `säsongrensad` and `säsongsrensad` are both recognized.

## Interpretation boundaries

`represented` means the enabled explicit rule found corresponding information;
its evidence remains inspectable. `text_match` and `semantic_match` are **not**
automatic exclusions: a note can refer to another measure, a historical period
or an exception. `scope_issue` and `unresolved` must not be called source errors
or unique information without reviewing their scope. `remaining` means only
that enabled rules did not resolve the occurrence.

`additional_explicit` is deliberately narrower than semantic uniqueness. It
currently covers only simple annual day/month statements; it does not promote
unmatched Stock/Flow/price/adjustment codes into confirmed useful information.
The exact comparison hash and number of checked strings accompany each finding.

The audit never infers observation availability for a metric/year combination
from the cartesian product of category maps. No observations are in this export.
References attached to metric categories do not become time-category attributes.
Likewise, `basePeriod` need not fall inside the observation coverage.

**This pipeline provides an exhaustive inventory and reproducible narrowing;
it does not turn unmatched strings into a complete semantically verified list.**
Field-retention decisions remain open until the residual scope questions are
resolved. No automatic deletions or model changes follow from these rules.
