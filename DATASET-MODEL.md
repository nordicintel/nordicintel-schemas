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

## Work status

**Latest decisions and corrections:**

- Keep `contents`.
- Use `municipality: {code, label}` for the OU-to-municipality relationship.
- Use ordered arrays for dimensions and categories, with explicit codes.
- Language representation remains undecided. The earlier recommendation for
  separate language documents based on mismatch counts is withdrawn: inspection
  of all 30 Swedish-provider code mismatches found 29 whitespace-only cases and
  one membership difference (SCB TAB1226). These exceptions do not determine the
  core model. Do not silently trim upstream request codes without a mapping.
- The proposal to retain five separate category qualifier fields is withdrawn
  pending a cross-field redundancy audit. Presence and nonconstant values alone
  do not establish additional information. Compare labels, alternative labels,
  descriptions, notes, time fields and units before recommending retention.
- Concrete corrections: TAB3840 already states the fixed-price basis in its
  category label; TAB3815 labels contain the 2008/2009 reference years; TAB6406
  labels identify seasonal adjustment. TAB2462 already states 31 December in a
  dataset note. Conversely, inspection of TAB4012 found that date only in its
  reference-period value within the stored document.
- Audit reference periods at their owning dimension/category and against the
  actual time categories, not merely the title's coverage. TAB3815's `2008`
  belongs to the metric labelled "Totalt taxeringsvärde 2008" although its time
  category is `2009`. TAB3257's May/November summary agrees with historical
  categories; the note and actual categories explain May-only from 2023. Calling
  that a contradiction without checking temporal scope was incorrect.

The source inventory is recorded below. The purported nonredundant shortlist
is withdrawn: its method did not establish semantic redundancy. Model retention
decisions remain open.
The field set below is an older **recommendation for
review**, not an approved contract. No Python model, schema or application rewrite
has started. Full converted examples and the implementation handoff follow the
remaining model decisions; do not label that later work complete prematurely.

## Qualifier audit correction — previous shortlist withdrawn

**The reported 3,195 datasets / 10,022 nonredundant entries are withdrawn.**
The scripts promoted failed text/pattern matches into findings of additional
information. That is not semantic analysis. Do not use that list or its counts
to justify fields in the model. The extracted source inventory remains useful;
the classification and claimed completion do not.

The actual question is: **what would someone misunderstand or be unable to
interpret if this attribute disappeared, while the title, categories, units,
notes and time information remained?** Different spelling and the absence of an
enum's literal name are not additional information. Ordinary statistical meaning
must be read and understood; it need not be redundantly stated in technical terms.

Concrete reading of the local documents:

| Case | Meaning and correction |
|---|---|
| TAB4012, `Stock` on “Antal” of foreign citizens | The title and measure already describe a count of people. A separate Stock classification provides no useful clarification of that count. This is separate from whether its December 31 reference adds a date. |
| TAB1729, `Stock` on counts, means and totals | The category labels distinguish “Antal personer”, two explicitly defined means, and “Totalsumma”. Category notes explain the populations used for the means. Stock does not improve those descriptions and must not be presented as missing information about which operation the measure represents. |
| TAB4697, `Stock` on gas prices and taxes in öre/kWh | The measures already describe prices/taxes per energy unit. The absence of the word Stock from their labels is not a meaningful information gap. |
| TAB6516 | Read the complete combination of dimensions: `Arbetskraftstillh` distinguishes population counts and percentages, while `TypData` distinguishes adjustments and changes. Interpreting the lone metric label in isolation loses the actual definition of a selected measure. |
| EN0102_11.px | Unlike an ordinary repeated coverage year, this local document has no time dimension, empty first/last periods and no 2024 in its title, notes or category labels. Its reference year needs separate consideration as coverage information, not an automatic category-qualifier field. |

**Current recommendation:** do not add `measuring_type` to the common model on
the strength of this audit. No need for that field has been demonstrated. This
is not a claim that Stock/Flow/Average can never convey information; it rejects
the unsupported proposal and its inflated evidence. Nor does it justify replacing
these codes with boilerplate notes.

For the other qualifiers, establish the specific missing fact (a reference date,
an otherwise unstated price basis, an adjustment or an index base) in the full
measure context before calling it a finding. Review groups of similar measures,
not records one at a time and not repeated regex passes. Discard obvious semantic
repetition as a group. Keep source interpretation issues separate.

Raw local extraction: 19,046 `sv` records; 5,297 candidate datasets; 64,548
attribute entries including empty/default-like values. Those inventory counts
are not counts of useful or unique information. Existing files under
`tmp/qualifier-audit-sv/final/` are **withdrawn investigation output**.

## Local evidence and limitations

Source: `C:/Users/ruben/Github/nordicintel-project/tmp/dataset_languages.csv`;
920,922,425 bytes, modified 2026-09-14 09:06 UTC. All 36,791 records were read;
there were no skipped rows. This is an export audit, not a live-database query.

| Scope | Language records | Distinct provider/dataset identities |
|---|---:|---:|
| Entire export | 36,791 | 28,199 |
| Swedish providers | 19,478 | 14,814 |

Swedish means `country_code=SE` in the local Harvest `providers/initial.json` at
commit `0ed2277e142bcb51da31d267465d9246dc722014`: csn, domstol,
energimyndigheten, fohm, kolada, konj, lansstyrelsen, msb, riksskog, scb, sjv,
skogsstyrelsen. This is an explicit audit grouping, not the final launch roster.

The CSV has no header and 17 columns; metadata JSON is column 15. Its quoted
fields use apostrophe escaping, but ordinary apostrophes in unquoted text must
be preserved. The audit reader handles both. Merely setting csv.reader's
escapechar would remove apostrophes from some ordinary titles/descriptions.
The final audit uses the corrected reader; those parsing differences are not
reported as source defects.

The initial scan found **zero `category.child` and zero category coordinates**
across 140,671 dimensions. Dense category positions, matching category label
keys, matching dimension IDs and matching basic/metadata identities passed for
every record. This does not prove the additional source extras are consistent.

Audit/support files and full source samples remain ignored under
`tmp/dataset-value-audit/`. Reproduce with `uv run --no-sync python` and the
local scripts `tmp/audit_dataset_values.py`, `tmp/audit_dataset_relationships.py`
and `tmp/audit_dataset_languages.py`; all use `tmp/local_dataset_csv.py`.
These scripts are local investigation helpers, not a new model package.

### Findings that change the recommendation

- **Statistical qualifications are used.** There are 23,602 Stock, 32,700 Flow
  and 8,361 Average category-value occurrences; 3,332 Current and 1,026 Fixed
  price occurrences; 191 seasonal-only, 333 working-day-only and 348 combined
  adjustment occurrences. These include language variants. These presence counts
  do not establish additional information; the earlier recommendation to retain
  five typed category fields is withdrawn pending the redundancy audit.
- **Unit text is in `unit.extension.base`.** Examples include `1000 ha`, `%`,
  `antal`, `number` and `index`. Map this to unit `label`. Category precision
  overrides dataset precision in 12,759 unit occurrences across 3,653 datasets;
  keep both levels, with the category value taking precedence for formatting.
- **Alternative category labels are not all duplicates.** 17,912 occurrences
  differ from the main category label, across 3,856 datasets. Keep distinct
  alternative labels; omit identical copies.
- **Code lists are not simply empty scaffolding.** 4,516 distinct datasets have
  populated references, including 1,655 Swedish-provider datasets. Preserve
  the references without implementing code-list operations in this model.
- **`infofile` is not a URL.** Values include `BE0101`,
  `2_Skogarnas_aldersfordelning`, and the literal string `None` (7,700 records).
  Never put these strings in `href` or fabricate documentation URLs from them.
- **Source identities are not interchangeable.** `px.tableid` can be `111e`
  while dataset code is `111e.px`. Keep dataset identity unchanged; source
  aliases do not replace it. The current PX retrieval binding already has an
  absolute endpoint, so it does not require reconstructing it from matrix IDs.
- **Source language flags cannot override document language.** 8,673 records
  have a different `px.language` from the harvested document language.
  This alone does not establish which language the text is actually in.
- **Some source references are inconsistent.** 56 reference-period entries
  across 28 datasets point at a category absent from the actual category map;
  examples use `ContentsCode/EliminatedValue`. Record these as explicit adapter
  normalization cases. Never silently attach the text to an arbitrary category.
- **OU geography is real information.** 629 datasets carry OU-to-municipality
  mappings. Retain this relationship independently of category hierarchy.

The official-status copy agrees with the first-class field in all 28,089
records where it occurs. Subject code/label copies also agree wherever present.
All 24,484 `dimension.link.describedby` entries have no `href`; examples contain
an opaque classification reference such as `urn:ssb:classification:klass:2` or
the text `  Region`. They cannot be blindly converted into HTTP links.

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
| Category | `code`, `label` | `alternative_label`, `unit`, `municipality`, `notes`, `links`; five statistical qualifier fields below remain withdrawn/pending |
| Unit | At least one supplied unit/precision attribute | `label`, `symbol`, `decimals` |
| Note | Nonblank `text` | `mandatory` boolean; absent does not invent a source declaration |
| Contact | At least one populated contact attribute | `name`, `organization`, `email`, `phone`, `raw` |
| Subject | At least one of `code`, `label` | No extension object |
| Thematic node | `code`, `label` | Source sort hints proposed for exclusion |
| Municipality reference | `code` | `label`; an OU location relationship, not a category parent |
| Code-list reference | `code` | `label`, `type` (`valueset` or `aggregation`), `links` |
| Link | Nonblank `rel`, `href` | `language`, media `type`, `label` |

`municipality` is a common geographic concept, not a Kolada object. Whether this
specific relation or a broader typed geographic reference is preferable remains
a focused decision; do not introduce a generic relationships bag.

**Withdrawn field proposal, retained here only as audit vocabulary:** the five
qualifiers below are not an accepted part of Category or Unit. Their source maps
are keyed by category, not one scalar per dimension:

- `measuring_type`: `stock`, `flow`, `average`, `other`.
- `price_type`: `not_applicable`, `current`, `fixed`.
- `adjustment`: `none`, `seasonal`, `working_day`, `seasonal_and_working_day`.
- `reference_period`: original descriptive period text, e.g. `Månad`.
- `base_period`: original base-period notation, e.g. `2008M01`.

Explicit `none`, `not_applicable`, false and zero retain their meanings; do not
collapse them into missing values. Source meanings follow the locally vendored
PxWeb specification, `tests/reference/pxweb/PxAPI-2.yml` at upstream commit
`8689b18c2d44d43e03e6e48cea7e95536869be18`; its definitions are evidence about
source fields, not the authority over our new model.

The remaining vocabulary question is whether `contents` deserves its own field
and which Kolada classification/publication information to normalize. The ledger
below makes these explicit instead of silently pretending the proposal covers
them already.

## Language and ordering: recommendation and real comparison

**Previous recommendation, now withdrawn as a conclusion from the audit:**
retain one complete document per language, using the
same Dataset class for both. Keep provider/dataset identity language-independent
and `language` alongside it. Updating Swedish replaces only the Swedish document;
English remains untouched. This is still one common model and one document per
language, not today's independent basic/metadata pair.

An inline `{sv, en}` text design remains possible, but a Swedish refresh would
also need rules for shared category additions/removals, ordering, roles and stale
English translations. Do not conceal those decisions in a generic merge helper.

Across 8,592 bilingual dataset pairs, 7,547 have identical ordered codes/roles and
1,045 differ. Detailed causes overlap: 770 role differences, 244 category-order
differences and 33 category-code differences. No dimension-code or dimension-order
differences were found. These are differences between saved harvests, not proof
that a provider intentionally has different structures per language; capture time
and adapter inference may contribute. In particular, all 244 order differences
are SCB, and 30 of the 33 category-code differences are SCB.

Representative matching source pair: `scb:TAB4707`, saved in both `sv` and `en`,
under `tmp/dataset-value-audit/bilingual_{sv,en}.source.json`.
The two alternative shapes will be shown from that exact pair below; neither
shape authorizes rewriting adapters before the language decision.

Ordered arrays are agreed for dimensions/categories: array position is
order, `code` is identity. Conversion must sort categories by the existing index,
never alphabetically. Root `id` remains the authority for dimension order;
source UI positioning hints are not a second ordering mechanism.

### Concrete shape comparison (category excerpts, not complete datasets)

These values come from category `0000070M`, the first metric category of
`scb:TAB4707`. The first option stores each category in its language's document:

```json
{
  "sv": {
    "code": "0000070M",
    "label": "Antal pågående anställningar",
    "unit": {
      "label": "antal",
      "decimals": 0
    },
    "measuring_type": "stock",
    "price_type": "not_applicable",
    "adjustment": "none",
    "reference_period": "Månad"
  },
  "en": {
    "code": "0000070M",
    "label": "Number of ongoing employments",
    "unit": {
      "label": "number",
      "decimals": 0
    },
    "measuring_type": "stock",
    "price_type": "not_applicable",
    "adjustment": "none",
    "reference_period": "Month"
  }
}
```

The inline-translation alternative represents the same category as:

```json
{
  "code": "0000070M",
  "label": {
    "sv": "Antal pågående anställningar",
    "en": "Number of ongoing employments"
  },
  "unit": {
    "label": {
      "sv": "antal",
      "en": "number"
    },
    "decimals": 0
  },
  "measuring_type": "stock",
  "price_type": "not_applicable",
  "adjustment": "none",
  "reference_period": {
    "sv": "Månad",
    "en": "Month"
  }
}
```

The `sv`/`en` wrapper in the first excerpt compares two documents; it is not a
proposed extra Dataset field. In both options the source category code and
position zero remain unchanged. A Swedish-only label correction is independent
in the first option; in the second it replaces only the sv text. A Swedish
category deletion requires a shared-structure/English-staleness rule only in
the second option. That is the actual tradeoff to decide.

## Resource links and private retrieval — pending model decisions

Recommend a `links` array with `href`, open nonblank relation strings, and optional
language, media type and label. Reserve clear meanings for `source`,
`documentation`, `metadata`, `data`, `related`, and `alternate`. Upstream `self`
links must not masquerade as NordicIntel self links. Preserve the actual target
and describe it as a source resource. External link language is not necessarily
restricted to our stored sv/en text languages; the corpus includes Norwegian links.

Only actual resource references belong in href. Opaque `infofile` and map names
are not URLs. Genuine URNs require an explicit URI policy; do not turn every
classification string into a fake URL.

Recommend keeping a **private retrieval binding outside Dataset**, keyed by
provider/dataset/language, containing implementation `type` and its validated
configuration. A PX data link describes a resource, not an entire POST request.
The retrieval module resolves the binding and uses dataset dimension/category
codes. No adapter config objects belong in the common Dataset class. Exact
private storage and submission interfaces are later implementation decisions.

## Complete current-field disposition ledger

All dispositions below are recommendations, except already agreed identity,
role, enum, official-status and extension-container decisions. **No omission
from the proposed field list silently authorizes deletion.**

Counts: `R/D` = populated language records / distinct datasets across the full
export; `SE R/D` uses the Swedish-provider subset. Empty/null/blank values are
excluded; explicit false and zero count as populated. `present R` also includes
empty containers. Samples are shortened. Low-cardinality enums are counted
exactly; long-text samples are illustrative, not a global frequency ranking.

| Source field | present R | populated R/D | SE populated R/D | Representative value | Recommendation / reason |
|---|---:|---:|---:|---|---|
| `basic.provider_code` | 36,791 | 36,791/28,199 | 19,478/14,814 | "csn" | Keep in identity; provider-scoped dataset identity. |
| `basic.dataset_code` | 36,791 | 36,791/28,199 | 19,478/14,814 | "SULESVL11a.px" | Keep in identity unchanged, including case and suffixes. |
| `basic.language` | 36,791 | 36,791/28,199 | 19,478/14,814 | "sv" | Keep as document language (recommended shape); never source PX flag override. |
| `basic.label` | 36,791 | 36,791/28,199 | 19,478/14,814 | "Lärlingsersättning efter Ålder, Folkbokföring län, Läsår, Kön och Antal personer, Utbe… | Keep title; nonblank. |
| `basic.description` | 17,323 | 17,323/13,029 | 8,979/8,113 | "Antal invånare 9 år den 31/12. Källa: SCB." | Keep description; preserve prose. |
| `basic.updated` | 30,760 | 30,760/22,168 | 13,447/8,783 | "2026-08-26T15:54:51Z" | Keep source update; missing allowed by model. |
| `basic.next_release` | 0 | 0/0 | 0/0 | — | Keep optional announced date/time; absent in this export. |
| `basic.time_unit` | 36,791 | 36,791/28,199 | 19,478/14,814 | "Other" | Normalize case into the agreed seven-value enum. |
| `basic.first_period` | 35,154 | 35,154/26,898 | 18,903/14,332 | "2001M01" | Keep original coverage notation. |
| `basic.last_period` | 35,154 | 35,154/26,898 | 18,903/14,332 | "2026M07" | Keep original coverage notation. |
| `basic.discontinued` | 11,496 | 11,496/10,968 | 7,529/7,001 | "f" | Keep nullable bool; CSV t/f is export encoding only. |
| `basic.source_url` | 36,791 | 36,791/28,199 | 19,478/14,814 | "https://statistik.csn.se/PxWeb/pxweb/sv/CSNstat/CSNstat__SU__L__LE/SULESVL11a.px/" | Map to links with rel=source and href. |
| `basic.doc_url` | 0 | 0/0 | 0/0 | — | Map to links with rel=documentation; absent in export. |
| `basic.extension` | 36,791 | 0/0 | 0/0 | — | Remove container; no populated contents in corpus. |
| `metadata.identity` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"language": "sv", "dataset_code": "SULESVL11a.px", "provider_code": "csn"} | Combine with basic identity; copies checked equal. |
| `metadata.id` | 36,791 | 36,791/28,199 | 19,478/14,814 | ["Ålder", "Folkbokföring län", "Läsår"] | Map to dimension array order without sorting. |
| `metadata.dimension` | 36,791 | 36,791/28,199 | 19,478/14,814 | ["Ålder", "Folkbokföring län", "Läsår"] | Map definitions into ordered dimensions; nested fields listed below. |
| `metadata.role` | 35,572 | 35,572/27,264 | 19,198/14,582 | {"time": ["månad"]} | Map each assignment to its dimension.role; max one role per dimension. |
| `metadata.subject` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"code": "Studiestöd", "label": "Lärlingsersättning", "extension": {}} | Keep explicit subject code/label; not assumed equivalent to paths. |
| `metadata.paths` | 36,791 | 36,791/28,199 | 19,478/14,814 | [{"path": [{"code": "SU", "label": "Utbetalning av studiestöd", "extension": {}}, {"cod… | Keep thematic chains and node codes/labels; drop empty wrappers/extensions. |
| `metadata.official_statistics` | 28,089 | 28,089/20,343 | 12,045/7,727 | true | Keep first-class bool or None; agreed. |
| `metadata.source` | 36,727 | 36,721/28,154 | 19,415/14,772 | "Centrala studiestödsnämnden, CSN." | Keep attribution. |
| `metadata.note` | 22,236 | 22,234/15,590 | 9,354/5,912 | ["Fotnoter med tabellförklaringar visas längst ned under rubriken 'Fotnoter'.", "Kostna… | Map strings to notes[].text; attach matched mandatory flags. |
| `metadata.contact` | 16,268 | 16,268/12,953 | 8,568/5,253 | [{"raw": " Statistikservice, SCB# +46 010-479 50 00#information@scb.se", "mail": "infor… | Map to contacts; mail -> email; retain name, organization, phone, raw. |
| `metadata.metadata_url` | 36,791 | 36,791/28,199 | 19,478/14,814 | "https://statistik.csn.se/PXWeb/api/v1/sv/CSNstat/SU/L/LE/SULESVL11a.px" | Map to links rel=metadata, href. |
| `metadata.retrieval` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"type": "pxweb_v1", "config": {"data_url": "https://statistik.csn.se/PXWeb/api/v1/sv/C… | Move operational binding outside Dataset; never delete required retrieval context. |
| `metadata.extension` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"px": {"matrix": "SULESVL11a", "decimals": 0, "language": "sv"}} | Remove container; every observed child handled below. |
| `metadata.extension.links` | 16,268 | 16,268/12,953 | 8,568/5,253 | [{"rel": "self", "href": "https://statistikdatabasen.scb.se/api/v2/tables/TAB4707?lang=… | Map rel/href/hreflang into Link; upstream self remains upstream resource. |
| `metadata.extension.variable_names` | 16,268 | 16,268/12,953 | 8,568/5,253 | ["sektor", "kön", "tabellinnehåll"] | Derive from dimension labels; no separately stored copy. |
| `metadata.extension.noteMandatory` | 5,974 | 5,974/3,610 | 5,717/3,353 | {"0": true, "1": true} | Map indexed flags to corresponding dataset notes; validate references. |
| `metadata.extension.px` | 30,760 | 30,760/22,168 | 13,447/8,783 | {"matrix": "SULESVL11a", "decimals": 0, "language": "sv"} | Remove container; child dispositions below. |
| `metadata.extension.kolada` | 6,031 | 6,031/6,031 | 6,031/6,031 | {"auspice": "X", "kpi_groups": [], "has_ou_data": false} | Remove container; child dispositions below. |
| `metadata.extension.px.aggregallowed` | 28,089 | 28,089/20,343 | 12,045/7,727 | true | Keep as aggregation_allowed; permission is not proof of additivity. |
| `metadata.extension.px.copyright` | 16,268 | 16,268/12,953 | 8,568/5,253 | false | Propose omit legacy flag (all false); this does not declare a licence or remove attribution. |
| `metadata.extension.px.decimals` | 30,760 | 30,760/22,168 | 13,447/8,783 | 0 | Keep dataset default decimals; category unit precision overrides. |
| `metadata.extension.px.contents` | 26,417 | 26,417/19,378 | 11,596/7,375 | "01. Avgjorda mål med ändrad utgång vid hovrätt per målkategori" | Recommend keep contents; concise statistical description can differ from title. |
| `metadata.extension.px.infofile` | 17,283 | 17,283/13,717 | 9,415/5,878 | "BE0101" | Do not treat as URL. Resolve to documentation link only with known source mapping; otherwise exclude opaque lookup ID from Dataset, record source mapping in Harvest. |
| `metadata.extension.px.matrix` | 28,089 | 28,089/20,343 | 12,045/7,727 | "SULESVL11a" | Exclude source matrix alias; identity and absolute retrieval binding already serve access. Explicit loss of source alias, not claimed duplicate. |
| `metadata.extension.px.tableid` | 21,173 | 21,173/15,552 | 8,648/5,294 | "A10" | Exclude source table alias from common document; it may differ from dataset_code. Preserve binding endpoint. |
| `metadata.extension.px.language` | 28,089 | 28,089/20,343 | 12,045/7,727 | "sv" | Exclude source flag; use requested/validated document language. Copies can disagree. |
| `metadata.extension.px.official-statistics` | 28,089 | 28,089/20,343 | 12,045/7,727 | true | Map into official_statistics; identical copies in audit. |
| `metadata.extension.px.subject-code` | 28,089 | 28,089/20,343 | 12,045/7,727 | "Studiestöd" | Combine into subject.code; identical copies in audit. |
| `metadata.extension.px.subject-area` | 26,417 | 26,417/19,378 | 11,596/7,375 | "Överklagande- och ändringsfrekvens" | Combine into subject.label; identical copies in audit. |
| `metadata.extension.px.description` | 11,292 | 11,292/6,998 | 2,948/2,082 | "01. Avgjorda mål med ändrad utgång vid hovrätt per målkategori. År 2006-2025." | Combine with description; compare after correct CSV decoding, not assumed duplicate. |
| `metadata.extension.px.descriptiondefault` | 26,417 | 26,417/19,378 | 11,596/7,375 | true | Omit source display preference; own display policy. |
| `metadata.extension.px.heading` | 16,268 | 16,268/12,953 | 8,568/5,253 | ["ContentsCode", "Tid"] | Omit source pivot columns; does not determine observation ordering. |
| `metadata.extension.px.stub` | 16,268 | 15,817/12,574 | 8,417/5,174 | ["Sektor", "Kon"] | Omit source pivot rows; dimensions retain their actual order. |
| `dimension.label` | 36,791 | 36,791/28,199 | 19,478/14,814 | "Kön" | Keep dimension label. |
| `dimension.category` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"index": {"0": 0, "1": 1, "2": 2}, "label": {"0": "Kvinnor", "1": "Män", "2": "Totalt"… | Map each code/index to an ordered Category object. |
| `dimension.note` | 6,384 | 6,384/4,526 | 1,886/1,244 | ["Med kön avses det juridiska könet. Personer som har bytt juridiskt kön under tidsperi… | Map to dimension notes[].text. |
| `dimension.link` | 11,480 | 11,480/9,120 | 788/481 | {"describedby": [{"extension": {"Region": "  Region"}}]} | Map genuine links; describedby entries need separate reference treatment below. |
| `dimension.link.related` | 6,405 | 6,405/6,405 | 0/0 | [{"href": "https://www.ssb.no/en/klass/klassifikasjoner/2", "type": "text/html", "label… | Map href/type/label to common links; retain definition relation and move category-scoped links to that Category. |
| `dimension.link.related[].extension.relation` | 6,405 | 6,405/6,405 | 0/0 | "definitions" | Map definitions to Link.rel; do not retain an extension object. |
| `dimension.link.related[].extension.category` | 2,656 | 2,656/2,656 | 0/0 | "Arbeidsstyrken" | Move the link to the matching category; validate code membership rather than keeping a loose reference. |
| `dimension.link.related[].extension.metaid` | 6,405 | 6,405/6,405 | 0/0 | "urn:ssb:classification:klass:2" | Retain genuine URI as reference href if URI policy permits, alongside HTTP link; otherwise explicitly exclude source alias. Pending link policy. |
| `dimension.link.describedby` | 11,480 | 11,480/9,120 | 788/481 | [{"extension": {"Region": "  Region"}}] | Interpret dimension-code/reference mapping; real URNs are distinct from bare source lookup strings. No fabricated URL. |
| `dimension.extension` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"show": "value", "position": 3, "elimination": true} | Remove container; child dispositions below. |
| `dimension.extension.elimination` | 36,791 | 36,791/28,199 | 19,478/14,814 | true | Keep optional bool; preserve source value. |
| `dimension.extension.eliminationValueCode` | 5,516 | 5,516/3,316 | 1,261/1,031 | "0" | Keep elimination_value category code; validate membership. |
| `dimension.extension.position` | 14,492 | 14,492/9,215 | 4,879/3,530 | 3 | Remove redundant source position; use checked root id order. |
| `dimension.extension.noteMandatory` | 894 | 894/518 | 890/515 | {"0": true} | Attach mandatory flag to the indexed dimension note. |
| `dimension.extension.categoryNoteMandatory` | 2,874 | 2,874/1,805 | 2,871/1,802 | {"0": {"0": true}} | Attach mandatory flag to the indexed category note; validate both references. |
| `dimension.extension.refperiod` | 16,356 | 12,573/10,580 | 5,180/3,187 | {"0000070M": "Månad", "0000070N": "Månad", "0000070U": "Månad"} | Pending cross-field and category/time-scope audit; earlier direct Category-field mapping withdrawn. Preserve source evidence until decided. |
| `dimension.extension.basePeriod` | 923 | 923/638 | 634/349 | {"AM0301AC": "2008M01", "AM0301AD": "2008M01"} | Pending cross-field and category/time-scope audit; earlier direct Category-field mapping withdrawn. Preserve source evidence until decided. |
| `dimension.extension.measuringType` | 16,268 | 16,268/12,953 | 8,568/5,253 | {"0000070M": "Stock", "0000070N": "Stock", "0000070U": "Stock"} | Pending cross-field and category/time-scope audit; earlier direct Category-field mapping withdrawn. Preserve source evidence until decided. |
| `dimension.extension.priceType` | 16,268 | 16,268/12,953 | 8,568/5,253 | {"0000070M": "NotApplicable", "0000070N": "NotApplicable", "0000070U": "NotApplicable"} | Pending cross-field and category/time-scope audit; earlier direct Category-field mapping withdrawn. Preserve source evidence until decided. |
| `dimension.extension.adjustment` | 16,268 | 16,268/12,953 | 8,568/5,253 | {"0000070M": "None", "0000070N": "None", "0000070U": "None"} | Pending cross-field and category/time-scope audit; earlier direct Category-field mapping withdrawn. Preserve source evidence until decided. |
| `dimension.extension.alternativeText` | 16,268 | 16,268/12,953 | 8,568/5,253 | {"0000070M": "Antal pågående anställningar", "0000070N": "Antal pågående anställningar … | Keep different values as Category.alternative_label; derive/omit exact duplicates. |
| `dimension.extension.codelists` | 16,268 | 5,839/4,516 | 2,978/1,655 | [{"id": "vs_Region99LanGU", "type": "Valueset", "label": "County"}, {"id": "vs_RegionRi… | Keep typed references: id->code, label, type->valueset/aggregation, links. Omit empty lists. |
| `dimension.extension.show` | 28,418 | 28,418/20,672 | 12,136/7,818 | "value" | Omit code/label display preference; code and label both retained. |
| `dimension.extension.map` | 1,206 | 1,206/654 | 6/6 | "Sweden_municipality" | Omit opaque source map name initially; it is not geometry or a portable geographic standard. Explicit loss of map hint. |
| `dimension.extension.category` | 629 | 629/629 | 629/629 | {"V11E100171": {"municipality_id": "1463", "municipality_label": "Mark"}, "V11E100217":… | Move municipality_id/municipality_label into Category.municipality.code/label; no category hierarchy. |
| `dimension.category.index` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"0": 0, "1": 1, "2": 2} | Derive order from positions; category keys become code. |
| `dimension.category.label` | 36,791 | 36,791/28,199 | 19,478/14,814 | {"0": "Kvinnor", "1": "Män", "2": "Totalt"} | Move each value to Category.label matched by code. |
| `dimension.category.unit` | 22,212 | 22,212/16,184 | 9,129/5,644 | {"KUL_YKS": {"decimals": 0, "extension": {}}, "SIS_GWH": {"decimals": 0, "extension": {}}} | Keep category units; nested decimals and base mapping below. |
| `dimension.category.note` | 9,396 | 9,396/7,021 | 3,524/2,244 | {"0": ["Om 'Totalt' väljs redovisas nettototalen för alla, vilket innebär att varje per… | Move into category notes[].text by code. |
| `dimension.category.child` | 0 | 0/0 | 0/0 | — | Omit initially: zero observed keys. |
| `dimension.category.coordinates` | 0 | 0/0 | 0/0 | — | Omit initially: zero observed keys; future geographic normalization is separate. |
| `dimension.category.extension` | 36,791 | 0/0 | 0/0 | — | Remove empty container; no observed contents. |
| `dimension.category.unit.{code}.decimals` | 22,212 | 22,212/16,184 | 9,129/5,644 | 0 | Keep Unit.decimals, including zero. |
| `dimension.category.unit.{code}.label` | 0 | 0/0 | 0/0 | — | Keep optional unit label; absent directly, source base supplies it. |
| `dimension.category.unit.{code}.symbol` | 0 | 0/0 | 0/0 | — | Keep optional symbol; do not guess it from arbitrary prose. |
| `dimension.category.unit.{code}.position` | 0 | 0/0 | 0/0 | — | Omit unused source display preference. |
| `dimension.category.unit.{code}.extension` | 22,212 | 21,511/15,832 | 8,980/5,569 | {"base": "1000 ha"} | Remove container after mapping base. |
| `dimension.category.unit.{code}.extension.base` | 21,511 | 21,511/15,832 | 8,980/5,569 | "1000 ha" | Rename to Unit.label preserving text; not numeric base-period information. |
| `metadata.paths[].path[].extension.sortCode` | 16,268 | 16,268/12,953 | 8,568/5,253 | "Arbetsmarknad" | Propose omit source thematic sort preference; preserve path/node sequence and labels. Explicit loss of sibling sorting hint. |
| `metadata.extension.kolada.operating_area` | 6,031 | 6,031/6,031 | 6,031/6,031 | "Befolkning" | Combine into existing subject/thematic path; no duplicated source property. |
| `metadata.extension.kolada.kpi_groups` | 6,031 | 2,762/2,762 | 2,762/2,762 | [{"id": "G2KPI92539", "title": "Kultur/Fritid"}] | Combine id/title into existing thematic paths; preserve every membership, omit empty groups. |
| `metadata.extension.kolada.perspective` | 6,024 | 6,024/6,024 | 6,024/6,024 | "Volymer" | Recommend an explicit thematic classification chain (e.g. perspective -> Resurser), not a Kolada object. |
| `metadata.extension.kolada.auspice` | 5,946 | 5,946/5,946 | 5,946/5,946 | "X" | Keep meaning as a typed classification; X/T/E/P/A/O codes are observed but labels must be verified before normalization. Unresolved mapping, not approved deletion. |
| `metadata.extension.kolada.municipality_type` | 6,031 | 6,031/6,031 | 6,031/6,031 | "A" | K/L/A affects geographic scope/probing; retain operationally and decide typed municipality/region coverage representation before dropping source information. |
| `metadata.extension.kolada.has_ou_data` | 6,031 | 6,031/6,031 | 6,031/6,031 | false | Keep for discovery/retrieval configuration if used; exclude capability duplicate from public Dataset. Municipality and OU datasets remain separately identified. |
| `metadata.extension.kolada.is_divided_by_gender` | 6,031 | 6,031/6,031 | 6,031/6,031 | true | Use source flag during construction; resulting category structure is the dataset truth. Do not add a sex role or infer meaning from category count alone. |
| `metadata.extension.kolada.publ_period` | 5,389 | 5,389/5,389 | 5,389/5,389 | "2026" | Publication-calendar year is not automatically coverage or time_unit. Preserve in private source mapping pending schedule semantics; no fabricated model date. |
| `metadata.extension.kolada.publication_date` | 5,359 | 5,359/5,359 | 5,359/5,359 | "2027-02-24" | Values include future dates; never copy into updated. Candidate announced next_release only after confirming source schedule meaning. |
| `metadata.extension.kolada.prel_publication_date` | 871 | 871/871 | 871/871 | "2026-09-28" | Provisional publication date needs explicit meaning/qualifier; do not silently replace a firm next_release date. Unresolved model treatment. |
| `metadata.extension.kolada.raw_description` | 937 | 937/937 | 937/937 | "Skattekraft, kr/inv. 1 nov fg år. Används som variabel i det kommunala utjämningssyste… | Keep cleaned description once normalization is verified; exclude original whitespace/markup copy from common Dataset. Raw examples remain audit material. |
| `metadata.extension.kolada.source_origin` | 6,031 | 6,031/6,031 | 6,031/6,031 | "description" | Exclude parsing provenance (description/fallback); keep resulting source attribution. |
| `metadata.extension.kolada.discontinued_year` | 415 | 415/415 | 415/415 | 2024 | Recommend retain as discontinued_year (optional integer) if precise cessation year matters; separate decision from bool and last_period. |

### Nested fields and empty containers

The ledger groups structural maps/arrays rather than listing every source code as
a schema field. The remaining defined nested fields are accounted for as follows:

- Identity `provider_code`, `dataset_code`, `language`: as above; language moves
  alongside identity only if the recommended document shape is accepted.
- Role `time`, `geo`, `metric`: same three single-role values; no role arrays on
  individual dimensions.
- Subject `code`, `label`, `extension`: retain code/label; extension empty, remove.
- Path wrapper `path`, `extension`: retain the chain; wrapper extension empty.
  Node `code`, `label`, `extension.sortCode`: covered above.
- Contact `name`, `organization`, `mail`, `phone`, `raw`, `extension`: retain
  descriptive fields, rename mail to email; extension empty.
- Retrieval `type`, `config.data_url`, `config.extension`: private binding;
  extension empty. Kolada config itself is empty; dataset identity remains needed.
- Code-list `id`, `label`, `type`, `links[].rel/href/hreflang`: typed code-list
  reference and common Link; preserve external resource language.
- Dimension `link.describedby[].extension`: source dimension-code-to-reference
  strings. A genuine classification URI can become a reference link if the link
  policy accepts URNs; strings such as `Region` stay source lookup information.
- Note flags: numeric note indexes and category-code keys are references, not
  arbitrary user-defined properties. Notes retain their order.
- Kolada group `id`, `title`: existing thematic code/label membership.
- OU `municipality_id`, `municipality_label`: typed municipality reference.
- Unobserved declared category child/coordinates and unit position: proposed
  exclusions, not claims that the source data contains them.
- Database `created_at`, `modified_at` (CSV columns 16/17) are ingestion/storage
  bookkeeping and remain outside the source Dataset model.

### Explicit exclusion list

Proposed removal from the common Dataset: category child/coordinates; unit
position; generic extension containers; source PX language/tableid/matrix copies;
heading/stub/show/descriptiondefault; dimension position duplicate; path sortCode;
opaque map hints; legacy all-false copyright flag; raw-description/source-origin
copies; variable_names duplicate; raw provider-specific config/capability objects.

This does **not** approve losing meaningful contents hidden inside those objects.
The unresolved Kolada classification/calendar fields, opaque classification
references, and source-document lookup IDs are explicitly listed above. Their
final mappings must be settled before calling the model decision-complete.

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
