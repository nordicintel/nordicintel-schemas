# Normalized Dataset model

Agreed direction, updated 2026-09-15: **one complete Dataset document per
language**. This supersedes the combined multilingual model and its Python class
specification previously in this file. No `translations` container or separate
basic-information/metadata document pair is proposed.

The authoritative contract is [schemas/dataset.schema.json](schemas/dataset.schema.json),
using JSON Schema Draft 2020-12. Python/Pydantic model development and schema
generation are shelved until further notice. Python in this repo is validation
tooling only. The corrected sibling-project draft was the input to this revision;
it is no longer the contract consumers should reference.

Swedish providers are the initial focus. Metadata supports `sv` and `en`.
Statistical discovery and repeatable retrieval are the product goals; exact
PxWeb UI compatibility does not dictate the model.

## Identity and language

`provider_code`, `dataset_code`, `dataset_id` and `language` are top-level fields.
Dataset identity is provider plus source dataset code; `dataset_id` is exactly
`provider_code + ":" + dataset_code`, without slugifying the source code.
Language distinguishes documents, not the dataset's public identifier.

Each language document contains its own structure and text. A Swedish refresh
can replace the Swedish document without merging or replacing English content.
No cross-language structural merge is required. Preserve source identities and
ordering during adapter normalization; do not invent translations or silently
substitute another language. Swedish remains the default requested language.

## Dataset fields

Only the seven fields marked required below are required. Requiredness here is a
model rule, not publication eligibility.

| Field | Required | Shape and meaning |
|---|---|---|
| `provider_code` | Yes | Lowercase letters/digits with underscore-separated segments, starting with a letter |
| `dataset_code` | Yes | Nonblank, opaque, case-sensitive source code, shared across language versions |
| `dataset_id` | Yes | Combined provider and dataset code, e.g. `scb:TAB335` |
| `language` | Yes | `sv` or `en` |
| `label` | Yes | Nonblank original dataset title in this document's language |
| `source` | No | Attribution string or null; placed immediately after `label` in the schema |
| `description` | No | Longer description string or null |
| `discontinued` | No | Boolean or null; unknown is not false |
| `updated` | No | Source update date, timezone-aware timestamp, or null |
| `official_statistics` | No | First-class boolean or null; unknown is valid |
| `time_unit` | No | `annual`, `semiannual`, `quarterly`, `monthly`, `weekly`, `daily`, `other`, or null; time granularity, not release frequency |
| `first_period`, `last_period` | No | Nonblank source period notation or null; not necessarily category labels |
| `next_release` | No | Announced source release date, timezone-aware timestamp, or null |
| `notes` | No | Array of strings or null |
| `subject` | No | Object with nonblank `code`, `label`, or both |
| `role` | No | Object with optional `time`, `geo`, `metric` arrays of unique dimension codes |
| `dimension_ids` | Yes | Nonempty ordered array of unique dimension codes |
| `dimension` | Yes | Nonempty mapping from dimension codes to Dimension objects |
| `links` | No | Array of Link objects or null |
| `paths` | No | Array of nonempty thematic node chains or null |
| `contacts` | No | Array of Contact objects or null |

Optional does not universally mean nullable: `subject` and `role`, for example,
are omitted when absent and do not accept null. The schema annotates nullable
Dataset fields with a null default. JSON Schema defaults do not insert values;
consumers apply construction defaults where needed. Object property order is
for readability, not semantic ordering.

## Dimensions and categories

Each Dimension requires a nonblank `label` and a `category` object. Optional fields:

- `note`: nonempty array of nonblank strings.
- `elimination`: boolean, defaults to **false**; whether the dimension can be
  omitted from a data selection. Null is not accepted.
- `elimination_value`: nonblank category code or null, defaults to **null**.
  Always optional, including when elimination is true. A supplied code must exist.
- `extension`: object with arbitrary additional JSON contents.

Roles remain in the Dataset's `role` mapping. A dimension has at most one role;
role arrays need not follow dimension order.

Category contains required nonempty `index` and `label` maps. `index` maps category
codes to nonnegative integer positions; these positions establish category order.
`label` maps codes to original nonblank labels. Dictionary iteration order is not
statistical order.

Optional Category fields:

- `note`: category-code map to nonempty arrays of nonblank notes.
- `unit`: category-code map to Unit objects.
- `extension`: object with arbitrary additional JSON contents.

A Unit has optional `label` (nonblank string), `decimals` (nonnegative integer),
and `position` (`start` or `end`), with at least one supplied field. Unit objects,
precision/presentation fields, generic dimension/category extensions and link
arrays are **intentional reintroductions**, not unresolved mistakes. There is no
new adapter-specific schema or top-level Dataset extension in this contract.

## Links, themes and contacts

A Link requires `rel` and `href`, with optional `hreflang` (`sv` or `en`). `href`
is an absolute HTTP(S) resource URL. Relations such as `source`, `documentation`,
`metadata`, `data`, `alternate` and `license` are examples; custom nonblank relation
names without whitespace are allowed. Links are an array, not four named slots.

Each thematic path is a nonempty ordered array of nodes. A node requires nonblank
`id` and `label`, with optional `link` using the Link structure. Paths describe
thematic membership, never dataset access routes.

Contact allows `name`, `email`, `phone`, `organization`, `address` and `url`, with
at least one populated field. Fields are nonblank strings; email and URL have
format checks. The Contact `url` is a direct HTTP(S) string, rather than
a Link object. No raw contact field is defined.

Private retrieval configuration remains outside Dataset. A data link identifies
a resource; it does not replace implementation settings or a POST request body.
Kolada's municipality labels and OU-to-municipality mapping remain one separate
supporting resource, not repeated on dataset categories or a general code-list
framework. Do not interpret Kolada publication-calendar dates as update dates or
period coverage.

## Validation and normalization

Defined objects reject unknown properties, except the explicitly open extension
contents and code-keyed maps. Structural validation checks required fields, types,
enums, formats and local references. Date/time and URL format checking must be
enabled explicitly.

Consumer-side semantic validation must check:

- Exact construction of `dataset_id` from the identity fields.
- Correspondence between `dimension_ids` and `dimension` keys.
- Unique, contiguous category positions starting at zero.
- Category labels cover the indexed codes; note and unit keys reference existing
  categories.
- Role references exist and no dimension is assigned more than one role.
- Any non-null `elimination_value` references an existing category.

Adapters own source parsing, code cleanup and mapping into these common fields.
Preserve original labels, meaningful units, notes, attribution, official status,
identities and order. Do not derive statistical ordering from display labels.
Actual text language cannot be proven by JSON Schema. Future standardized time
category values must preserve the source category codes; their shape is not
introduced by this documentation update.

## Revision and adoption status

The unpublished 2.0.0 collection now contains Provider and this complete Dataset.
It replaces the previous basic/detail split and the superseded combined-language
proposal. The old metadata/helper/PX schemas and multilingual projections have
been removed. Published 1.0.0 remains unchanged.

See [the three illustrative examples](examples/README.md). They demonstrate the
current shape, not live exports or full source datasets. Normal validation checks
the structural schema, examples, inline examples and defaults; the relationship
checks above remain consumer responsibilities. No runtime model package is added.

Next work belongs in the consuming projects: map Harvest output to this contract,
then implement catalog storage/read behavior for independent language documents.
Private retrieval configuration remains external. No preservation migration for
development documents, database publication rules, application changes or
deployment are part of this revision.
