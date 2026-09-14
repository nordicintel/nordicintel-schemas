# Dataset model: working decisions

Design in progress. This document records model decisions and clearly marked
proposals only. Investigation results, source inventories and audit scripts do
not belong here. No model or application rewrite is authorized at this stage.

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
  **Agreed:** `bool | None`; unknown is allowed. Model optionality is separate
  from publication policy.
- **Agreed `time_unit` enum:** `annual`, `semiannual`, `quarterly`, `monthly`,
  `weekly`, `daily`, `other`. Period coverage remains part of the model. Normalized
  time-category values are the next standardization target, not an adapter extension.
- All URL-bearing resources use link objects with `href`.
- Public IDs are `provider_code:dataset_code`; Swedish is the default language.
- Earlier publication-policy discussions are separate from this model exercise.
  Do not turn optional-field questions into database/publication questions.
- Existing development documents are disposable. No migration/backfill or
  compatibility rollout for preserving those documents is needed.
- Exact PxWeb UI compatibility no longer drives the core model. JSON-stat
  concepts remain useful; public encodings can be derived.

- Keep `contents`.
- Use `municipality: {code, label}` for the OU-to-municipality relationship.
- Use ordered arrays for dimensions and categories, with explicit codes.
- Language representation remains undecided.

## Open decisions

- Final required and optional statistical fields, units and measurement qualifications.
- Language-specific documents versus translated fields, including independent refreshes.
- Treatment of classifications and publication-calendar information.
- Link relations, URI policy and private retrieval binding.
- Python model authority and helpers; storage and API design follow the model.

The proposed field set below is not an approved contract. No decision to retain
or discard the five source qualifiers (`refperiod`, `basePeriod`, `measuringType`,
`priceType`, `adjustment`) has been approved.

## Recommended common model — pending approval

One dataset document replaces the basic/metadata pair. Required means required
for a structurally usable stored/harvested document, not publication eligibility.
Optional attributes default to None in Python; no invented dates, false flags,
units or descriptive text. The agreed nullable official status accepts None.
The omission-versus-null wire policy for other optional fields is still open.

### Dataset

| Field | Type / requiredness | Meaning |
|---|---|---|
| `identity` | Required object | `provider_code`, `dataset_code`; unchanged identity rules |
| `language` | Required `sv` or `en`, if language-specific documents are chosen | Language of all descriptive text in this document |
| `label` | Required nonblank text | Dataset title |
| `dimensions` | Required nonempty ordered array | Dimension definitions; codes remain selection keys |
| `description` | Optional text | Longer explanation |
| `contents` | Optional nonblank text | Short statistical contents description; not automatically equivalent to title/description |
| `official_statistics` | **Agreed optional bool or None** | Source-declared official status; unknown is valid |
| `updated`, `next_release` | Optional date or timezone-aware timestamp | Source update and announced next release; never ingestion time |
| `time_unit` | Optional agreed seven-value enum | Period granularity, not publication frequency |
| `first_period`, `last_period` | Optional nonblank text | Original coverage notation; normalized periods are future work |
| `discontinued` | Optional bool | Source-declared publication status |
| `source` | Optional text | Attribution |
| `subject` | Optional `{code?, label?}`, at least one | Primary source subject; retain separately from multiple thematic paths |
| `paths` | Optional ordered thematic chains | Typed code/label nodes; never retrieval routes |
| `decimals` | Optional nonnegative integer | Dataset default display precision; does not round stored/retrieved observations |
| `aggregation_allowed` | Optional bool | Preserve source-declared aggregation permission; not proof that every category is additive |
| `notes` | Optional Note array | Dataset notes |
| `contacts` | Optional Contact array | Contact details |
| `links` | Optional Link array | Human/source/metadata/data/documentation resources |

### Dimension, category and helper objects

| Object | Required | Optional |
|---|---|---|
| Dimension | `code`, `label`, nonempty ordered `categories` | `role`, `elimination`, `elimination_value`, `notes`, `links`, `codelists` |
| Category | `code`, `label` | `alternative_label`, `unit`, `municipality`, `notes`, `links` |
| Unit | At least one supplied unit/precision attribute | `label`, `symbol`, `decimals` |
| Note | Nonblank `text` | `mandatory` boolean; absent does not invent a source declaration |
| Contact | At least one populated contact attribute | `name`, `organization`, `email`, `phone`, `raw` |
| Subject | At least one of `code`, `label` | No extension object |
| Thematic node | `code`, `label` | Source sort hints proposed for exclusion |
| Municipality reference | `code` | `label`; an OU location relationship, not a category parent |
| Code-list reference | `code` | `label`, `type` (`valueset` or `aggregation`), `links` |
| Link | Nonblank `rel`, `href` | `language`, media `type`, `label` |


## Resource links and private retrieval — pending model decisions

Recommend a `links` array with `href`, open nonblank relation strings, and optional
language, media type and label. Reserve clear meanings for `source`,
`documentation`, `metadata`, `data`, `related`, and `alternate`. Upstream `self`
links must not masquerade as NordicIntel self links. Preserve the actual target
and describe it as a source resource. External link language is not necessarily
restricted to our stored sv/en text languages.

Only actual resource references belong in href. Opaque `infofile` and map names
are not URLs. Genuine URNs require an explicit URI policy; do not turn every
classification string into a fake URL.

Recommend keeping a **private retrieval binding outside Dataset**, keyed by
provider/dataset/language, containing implementation `type` and its validated
configuration. A PX data link describes a resource, not an entire POST request.
The retrieval module resolves the binding and uses dataset dimension/category
codes. No adapter config objects belong in the common Dataset class. Exact
private storage and submission interfaces are later implementation decisions.

## Model package and storage: later decisions, not new implementation

Recommended package shape: Python/Pydantic Dataset and nested types generate
JSON Schema. One public construction/validation path handles identity, enums,
ordering and semantic references. Helpers may normalize known enum spellings,
units and notes; provider-specific extraction stays in Harvest. No HTTP, SQL,
queues or mutable application state belongs in the model package.

Structural JSON Schema checks cover required fields, types, enums and link
shape. Python semantic checks cover unique codes, valid references and category
ordering. Future normalized time values should be typed additional category
fields that preserve source code/order; do not add them before their rules are
designed. Distribution as a PyPI package versus bundled classes remains open.

PostgreSQL layout and publication logic are deferred until the model is settled.
The earlier proposal was JSONB documents with relational identities and selected
query columns, not category-per-row normalization. Existing development data is
disposable; there is no data-preservation migration project here.

## Remaining decisions and completion sequence

1. Agree statistical fields and deliberate exclusions; finish Kolada
   classification/publication semantics. Official status nullable and the
   seven-value time enum are already settled.
2. Choose language-specific documents versus inline translations and finish
   link/reference policy. Ordered dimension/category arrays are already agreed.
3. Convert complete representative PXWeb v1/v2, bilingual and both Kolada-kind
   documents to the accepted shape. Verify identity/order/units/notes/qualifiers
   and account for every dropped source value. Add rare-field cases.
4. Settle Python authority/helpers, private retrieval interface and then storage.
5. Write the implementation handoff only after those decisions. It must cover
   model regression cases, adapter conversion, catalog replacement and an
   end-to-end harvest/store/read verification. No application rewrite yet.

Work remains on `public-contract-direction`; no merge, push, tag or publication.
Published 1.0.0 and the running applications remain untouched.
