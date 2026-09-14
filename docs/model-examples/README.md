# Normalized model examples

These are complete **proposed documents**, converted locally from saved adapter
exports. They are not outputs of the running Harvest implementation and are not
members of the released schema collection. The authority for their shape is
[DATASET-MODEL.md](../../DATASET-MODEL.md).

| Document | Identity | Translations | Dimensions | Categories |
|---|---|---|---:|---:|
| [PXWeb v1](pxweb-v1-csn.json) | `csn:SULESVL11a.px` | sv | 5 | 48 |
| [PXWeb v2](pxweb-v2-scb.json) | `scb:TAB4707` | sv, en | 4 | 150 |
| [Kolada municipality](kolada-municipality.json) | `kolada:N01826` | sv | 3 | 343 |
| [Kolada OU](kolada-ou.json) | `kolada:N11730_OU` | sv | 2 | 5,889 |

[Kolada mapping sample](kolada-mapping.sample.json) holds the OU example's
municipality labels and OU membership outside Dataset. It is a subset recovered
from the saved example, not the complete `/ou` or `/municipality` resource.
Application construction will use those existing provider resources directly.

[Private retrieval binding samples](retrieval-bindings.sample.json) retain the
five original language-specific bindings separately. Their operational envelope
is illustrative, not an additional shared schema. The empty Kolada configuration
remains empty; identity and the retrieval implementation select the data kind.
No retrieval implementation or source request has been executed here.

## Provenance

Source: local `nordicintel-project/tmp/dataset_languages.csv`, modified
2026-09-14 09:06 UTC. Source snapshots remain ignored under this repository's
`tmp/dataset-value-audit/`: `pxweb_v1.source.json`, `bilingual_sv.source.json`,
`bilingual_en.source.json`, `kolada.source.json`, `kolada_ou.source.json`.
No hosted database was queried and no new provider requests were made.

The examples retain source attribution and upstream resource URLs. Their JSON
shape is a local design projection; it must not be described as provider-native
JSON or as an implemented NordicIntel API response.

## Field dispositions

This ledger describes transformations, not an inventory or corpus-frequency
report. Grouped entries explicitly cover the original nested fields.

| Original information | Treatment |
|---|---|
| Basic/metadata identity: provider_code, dataset_code, language | Shared identity once; language selects a translation entry |
| Basic label, description | Translation label/description, preserving original text |
| updated, next_release, first_period, last_period, discontinued | Shared values; absent values remain absent; CSV t/f decoded as booleans |
| time_unit | Lowercase spelling of the agreed enum |
| Basic source_url, doc_url; metadata_url | Named href objects; known fixed Kolada resources shared, language-specific PX URLs translated |
| Root id and dimension keys | Ordered Dimension objects; no sorting beyond source order |
| Role time/geo/metric assignments | One optional role on each referenced Dimension |
| Dimension label/note | DimensionText label/notes |
| Category index/label | Ordered Category code objects and original translated category labels |
| Category note | CategoryText notes, keeping the source list order |
| Unit label or extension.base | CategoryText unit string; no extra unit object |
| Unit decimals, symbol, position | Excluded |
| Root note | Translation notes, preserving source strings and order |
| Root source | Translation attribution text |
| Subject code/label | Shared subject code and translated subject label |
| Paths path[].code/label | Shared code chains and corresponding translated label chains |
| Path-node sortCode | Excluded source sorting hint; path/node sequence remains intact |
| official_statistics and px.official-statistics | One shared optional boolean; duplicate copy removed |
| Contact name, organization, mail, phone | Canonical shared contacts; mail renamed email; identical objects deduplicated |
| Contact raw/extension | Excluded; translated variants of canonical contact details are not separately copied |
| Dimension elimination/eliminationValueCode | Shared elimination/elimination_value; source category code retained |
| Dimension refperiod, basePeriod, measuringType, priceType, adjustment | Excluded, without inferring replacements |
| Dimension alternativeText | Excluded; original category label retained |
| Dataset/dimension noteMandatory and categoryNoteMandatory | Excluded completely; text notes remain |
| PX decimals, aggregallowed | Excluded; no precision or aggregation permission |
| PX contents, copyright, descriptiondefault, heading, stub | Excluded |
| PX matrix, tableid, language | Excluded source aliases/flags; shared identity and language-specific private retrieval binding retain addressing |
| PX subject-code, subject-area, description | Common/translated counterparts retain the information; no extension copies |
| PX infofile, dimension map | Excluded opaque lookup/display identifiers; not converted to fabricated URLs |
| Dimension show, position | Excluded display hints; root id/category indexes supply actual order |
| Dimension codelists; describedby/related links and their extension metadata | Excluded; no general code-list/reference system or related-link array |
| Category child/coordinates | Excluded; neither occurs in these examples |
| Root extension.links rel/href/hreflang | metadata/data targets represented by named links where applicable; upstream self/alternate API navigation links omitted; not NordicIntel self links |
| Root variable_names | Removed duplicate; derive names from translated dimension labels |
| Kolada operating_area, kpi_groups id/title | Existing subject/group paths retained; raw duplicate extras removed |
| Kolada perspective, auspice, municipality_type, has_ou_data, is_divided_by_gender | Excluded source extras; resulting dataset identity, categories and source description remain |
| Kolada publ_period, publication_date, prel_publication_date, discontinued_year | Excluded; no invented updated/coverage/next-release values |
| Kolada raw_description, source_origin | Excluded raw/provenance copies; common description and attribution retained |
| OU extension.category[].municipality_id/municipality_label | Removed from Dataset; moved to the separate shared mapping sample |
| Retrieval type/config/data_url/config.extension | Full original private bindings retained in a companion file; href alone is not the retrieval contract |
| Empty basic, subject, path, category and other extension containers | Removed; no replacement generic container |
| Database created_at/modified_at | Not source Dataset attributes; excluded |

Some listed source fields are absent from the selected examples. They are
included to make the model's exclusion rules explicit, not to imply those values
were found in these documents. Unknown newly encountered source fields require
an explicit disposition rather than silently entering the common model.

## Verification

The proposed documents passed the executable Pydantic class specification in
DATASET-MODEL.md and its generated structural JSON Schema. Direct source-to-result
comparisons checked identity, ordered dimensions/categories, original labels,
unit text, notes, attribution and official status for all five source documents.
The SCB translations share identical structural values in this saved pair;
contacts use its canonical Swedish source details.

Seventeen negative cases covered removed fields, invalid enums/languages, duplicate
codes, missing translation references, invalid elimination references, empty/raw
contacts, invalid hrefs, role arrays, mandatory-note objects, path mismatch,
timezone-less timestamps and numeric timestamps.
All seven time units with nullable official status and a complete English-only
translation also passed. The generated schema is structural: Python validation
remains responsible for cross-field relationships.

This is model/example verification, not a claim that live adapters or catalog
endpoints already implement this shape. Temporary conversion/check helpers stay
in ignored `tmp/`; the next implementation must turn these cases into maintained
package tests, as specified in the [handoff](../../DATASET-MODEL-HANDOFF.md).
