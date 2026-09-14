# Dataset model: working decisions and field ledger

Updated 2026-09-14. **Design in progress; no model implementation authorized here.**
This is the working reference for the redesign. Update it as decisions change;
do not leave decisions only in chat. Agreed decisions, proposals, and unresolved
field mappings are distinguished below.

The comparison baseline is the model currently used by `nordicintel-harvest`
(`schemas/datasets.py`, `schemas/dimensions.py`) and catalog schema collection
**1.0.0**. The unpublished 2.0.0 schemas on this branch are not the active model
and are not the baseline for deciding what existing information to discard.

## Agreed direction

- NordicIntel is a cross-provider statistical hub: discover the right statistics,
  then retrieve observations repeatedly through one interface.
- Focus on Swedish providers initially. Provider selection belongs in Harvest;
  Swedish providers and Swedish-only metadata are different decisions.
- Use one common dataset model. No adapter-specific dataset schemas or objects.
- No generic `extension` containers. Useful shared attributes receive explicit
  definitions, types, and validation. Raw source payloads are separate material.
- A dimension has **one optional role**, limited to `time`, `geo`, or `metric`.
  Do not introduce arrays of roles per dimension.
- `official_statistics` is a first-class dataset field and important for discovery.
  The latest proposal treats absence as unknown rather than defaulting to false;
  requiring its presence for publication has not been agreed.
- Define a `time_unit` enum. Period coverage remains part of the model. Normalized
  time-category values are the next standardization target, not an adapter extension.
- All URL-bearing resources use link objects with `href`.
- Public IDs are `provider_code:dataset_code`; Swedish is the default language.
- The agreed publication policy requires actual `updated`, `first_period`,
  `last_period`, and `time_unit`, plus usable metadata. PostgreSQL maintains
  eligibility and blocking reasons. Revisit only through an explicit decision.
- Existing development documents are disposable. No migration/backfill or
  compatibility rollout for preserving those documents is needed.
- Exact PxWeb UI compatibility no longer drives the core model. JSON-stat
  concepts remain useful; public encodings can be derived.

## Verified local corpus: child/hierarchy support

Source: `C:\Users\ruben\Github\nordicintel-project\tmp\dataset_languages.csv`.
Use this local export for further corpus investigation; do not use the hosted
paid service when the local export answers the question.

| Evidence | Result |
|---|---:|
| File size | 920,922,425 bytes |
| File modified (UTC) | 2026-09-14 09:06:00 |
| Audit completed (UTC) | 2026-09-14 14:57:09 |
| Parsed language records | 36,791 |
| Distinct `(provider_code, dataset_code)` pairs | 28,199 |
| Dimensions inspected, including language variants | 140,671 |
| Dimensions containing a `category.child` key | **0** |
| Nonempty child maps | **0** |
| Distinct datasets with child maps | **0** |

All rows were read, all metadata documents parsed, and their identities checked
against the CSV identity columns. There were no skipped or failed rows. The CSV
has no header, 17 columns, comma delimiter, double-quote quote character and
**apostrophe escape character**; metadata is column 15 (zero-based 14). A default
CSV reader without that escape setting splits documents incorrectly.

**Revised proposal: omit category `children`/`child` and hierarchy validation from
the initial model.** The previous inclusion had no evidence in this corpus. This
does not remove thematic dataset paths or the OU-to-municipality relationship;
those are different information.

The audit spans the export's 20 providers, including non-Swedish providers. These
counts describe the file, not a claim about the current live database. The audit
script and full field-count output are local, ignored files:
`tmp/audit_dataset_model.py` and `tmp/dataset-model-audit.json`.

## Proposed representation: not yet accepted

- One `Dataset` document instead of independently identified basic and metadata
  documents; listing summaries remain possible.
- Identity contains provider and dataset codes. Translated descriptive fields
  contain `sv` and optional `en`; statistical structure is shared. Language
  representation and translation update rules still need agreement.
- Ordered dimension/category arrays with explicit codes. Array positions define
  order; codes define selection identity. Existing JSON-stat maps are the alternative.
- Python/Pydantic classes as authority, with generated, versioned JSON Schema and
  an optionally published Python package. This has been proposed, not approved.
- Shared helpers construct, parse, normalize and semantically validate our model.
  Provider-response parsing stays in Harvest; HTTP and persistence stay outside
  the model package. Generated JSON Schema cannot replace every semantic check.
- Dataset JSONB plus identity columns, timestamps and DB-maintained publication
  fields; selected query indexes/derived columns. No per-category SQL tables yet.
  Exact PostgreSQL layout remains undecided.

## Candidate core attributes

This is a proposal, not a complete approved field set. The unresolved statistical
fields in the next section must be addressed before calling it complete.

| Object | Candidate fields |
|---|---|
| Dataset | `identity`, `label`, `description`, `official_statistics`, `updated`, `next_release`, `time_unit`, `first_period`, `last_period`, `discontinued`, `source`, `paths`, `dimensions`, `notes`, `contacts`, `links` |
| Identity | `provider_code`, `dataset_code` |
| Dimension | `code`, `label`, single optional `role`, `categories`, `elimination`, `elimination_value`, `notes`, `links` |
| Category | `code`, `label`, `unit`, `notes`, `links`; **no children** |
| Unit | `label`, `symbol`, `decimals`; source unit-text mapping still needs definition |
| Note | `text`, optional source-declared `mandatory` |
| Contact | `name`, `organization`, `email`, `phone`, `raw`; at least one populated value |
| Thematic node | `code`, `label`; path is a nonempty ordered node sequence |
| Link | `rel`, `href`, optional `language`, media `type`, and `label` |

Candidate link relations: `source`, `documentation`, `metadata`, `data`, `related`.
Whether that is a closed set is **not decided**; existing links need inspection
before narrowing relationships or dropping their attributes.

Candidate `time_unit` values: `annual`, `semiannual`, `quarterly`, `monthly`,
`weekly`, `daily`, `other`. Enum requirement is agreed; exact members are proposed.
The observed export values are Annual (29,034 language rows), Other (4,228),
Monthly (1,810), Quarterly (1,669), Weekly (50). No value is missing in this export.
Period granularity is distinct from publication frequency. Missing/unknown must
not silently become `other`.

Future normalized category periods should retain source category codes and order,
adding explicit standardized period information. No generic extension mechanism
or silent code replacement is needed. Exact period type is future design work.

## Fields the previous proposal failed to account for

Do not treat an omission from the candidate table as approved deletion. Counts
below are **key occurrences**, including empty/default values and language
variants, not proof of meaningful use or distinct-dataset counts.

### Declared active-model fields

| Field | Corpus evidence / current disposition |
|---|---|
| `subject.code`, `subject.label` | Subject object occurs in all 36,791 rows. Omitting explicit subject in favor of paths is unresolved; do not assume equivalence. |
| Category `coordinates` | Zero category-coordinate keys observed. Candidate exclusion, not a schema-derived assumption of use. |
| Unit `position` | Zero observed. Candidate exclusion. |
| Category `child` | Zero observed. Revised proposal excludes it. |
| `retrieval.type` / implementation config | Present in all 36,791 documents. Common public model should not contain adapter objects, but necessary private retrieval binding has no completed replacement design yet. |
| Open extension containers | Removal agreed for the new common model. Contents require explicit mapping, deliberate exclusion, or retention outside the document. |

### Actual PX and shared extras

| Location / key | Occurrences | Disposition needing agreement |
|---|---:|---|
| `extension.px.aggregallowed` | 28,089 | Aggregation permission: define shared field/behavior; not mere presentation. |
| `extension.px.copyright` | 16,268 | Copyright flag: assess meaning and define treatment. |
| `extension.px.decimals` | 30,760 | Dataset precision/default versus per-unit precision. |
| `extension.px.contents` | 26,417 | Statistical contents text: do not assume dataset description replaces it. |
| `extension.px.infofile` | 17,283 | Inspect references and map meaningful resources into links. |
| `extension.px.matrix` | 28,089 | Source matrix identity; determine whether retrieval needs it. |
| `extension.px.descriptiondefault` | 26,417 | Presentation behavior; candidate exclusion. |
| `extension.px.heading`, `stub` | 16,268 each | Presentation placement; candidate exclusion. |
| Dimension `refperiod` | 16,356 | Reference-period information: define typed location if meaningful. |
| Dimension `measuringType`, `priceType`, `adjustment` | 16,268 each | Measurement/price/adjustment semantics: previous proposal wrongly omitted them without assessment. |
| Dimension `basePeriod` | 923 | Base-period information: define common location if meaningful. |
| Dimension `alternativeText` | 16,268 | Inspect nonempty values before deciding. |
| Dimension `codelists` | 69,766 | Inspect populated lists and their fields; do not equate presence with implemented codelist operations. |
| Dimension `map` | 1,258 | Previously missed entirely; inspect values before deciding. |
| Dimension `show` | 118,604 | Code/label presentation; candidate exclusion. |
| Path-node `sortCode` | 97,209 | Source thematic ordering; previous proposal dropped it without a decision. |
| Unit `extension.base` | 75,518 | Source unit text. Must receive a defined common mapping. |

All 76,629 observed unit objects contain `decimals` and `extension`; none contains
a direct `label`, `symbol`, or `position`. Therefore making unit `label` required
without first mapping source `base` text would reject current data. Unit text and
reference/base periods must not be conflated just because both use the word base.

The following observed extras have candidate equivalents, requiring explicit
mapping rather than deletion: dimension `position` -> array order; `elimination`
and `eliminationValueCode` -> direct dimension fields; root/dimension
`noteMandatory` and dimension `categoryNoteMandatory` -> note flags;
`variable_names` -> derived labels; root `links` -> link objects; PX `tableid`,
`language`, `official-statistics`, `description`, `subject-code`, `subject-area`
-> common identity/text/status/classification, with conflicts handled explicitly.

### Actual Kolada extras

| Field | Occurrences in language documents |
|---|---:|
| `operating_area` | 6,031 |
| `perspective` | 6,024 |
| `auspice` | 5,946 |
| `municipality_type` | 6,031 |
| `has_ou_data` | 6,031 |
| `is_divided_by_gender` | 6,031 |
| `publ_period` | 5,389 |
| `publication_date` | 5,359 |
| `prel_publication_date` | 871 |
| `raw_description` | 937 |
| `source_origin` | 6,031 |
| `kpi_groups` (`id`, `title` entries) | 6,031 |
| `discontinued_year` | 415 |

The OU dimension also stores category-level `municipality_id` and
`municipality_label` inside its extension's `category` mapping (629 dimensions
have that mapping). This is an organizational-unit-to-municipality relationship,
**not category.child**, and must not disappear as a side effect of dropping
hierarchy support.

For these fields, decide what is shared statistical meaning, classification,
retrieval information or raw provenance. Then give useful information proper
typed fields or an explicit home outside the document. No `extension.kolada`
replacement under another vague name. No blanket deletion is agreed.

## Next decisions and evidence

1. Inspect values (not just key presence) for unresolved fields above, using the
   local CSV. Finish the keep/map/drop ledger against real stored information.
2. Agree the full common attributes, including official status and measurement
   qualifications, before writing classes or schemas.
3. Settle ordered arrays versus existing maps, language representation, and exact
   time enum; then decide model-package ownership and PostgreSQL representation.
4. Define the retrieval binding needed outside the common dataset model.

No model code, application changes, merge, push, tag or release is part of this
document update. Existing 1.0.0 remains the active contract.
