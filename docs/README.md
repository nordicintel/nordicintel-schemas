# System decisions and dataset contracts

The system decisions below are agreed architectural direction, not a claim that
the applications already implement them. The provider, [Dataset](../schemas/dataset.schema.json),
and [Dataset metadata](../schemas/dataset-metadata.schema.json) contracts are
implemented locally at version 0.1.0 and remain unpublished.

## Agreed system decisions

### Hosting and responsibilities

A hosted PostgreSQL catalog is managed through an authenticated API. Harvest
workers access that API rather than connecting directly to the database.
Initially, Harvests are manually requested through the API, queued durably, and
executed one at a time globally. Observation storage is outside the current scope.

| Information | Responsibility |
| --- | --- |
| Provider descriptions | Catalog-managed identity and descriptive records |
| Harvesting configuration | Inputs required to initialize a harvest adapter |
| Dataset-specific retrieval configuration | Information needed to retrieve observations for a particular dataset |

Shared contracts live here as versioned JSON Schemas. Implementation-specific
input schemas live alongside their implementations; the catalog stores the
configuration values. Database migrations belong to the catalog. Release and
direct schema URL conventions are documented in the [root README](../README.md#versioned-schemas).

### Identity and language

- A provider's own identity field is `code`; other documents use `provider_code`
  to reference it. Display-name or adapter changes do not change that identity.
- Dataset identity is the combination of provider and dataset code. Language
  identifies a metadata version of that dataset, not a different dataset.
- Only `sv` and `en` are supported. Every harvest adapter input requires
  `provider_code` and `language`; outputs preserve both and actually contain
  metadata in the requested language. Unsupported requests fail without silent
  fallback. An adapter need not support both languages.
- Basic Dataset information and detailed Dataset metadata are separate documents
  linked by provider, dataset code, and language. Dataset text is in the declared
  language; provider display text uses language-keyed translations.

### Dimensions, extensions, and retrieval

Dimensions and categories have explicit ordering so future observation values
can be interpreted consistently. Adapters or other application logic decide how
to establish that order; the contracts do not prescribe a sorting algorithm.
Our documents omit `class`, `version`, `size`, and observation `value`.

Detailed metadata can contain optional `retrieval`, produced by harvesting and
interpreted by a separate retrieval implementation. Together with dimension
metadata, it must describe retrieval without reconstructing harvest initialization
or relying on provider descriptions. Retrieval implementations own their config
schemas and request/response logic. Credentials and operational request limits
remain deployment concerns.

A future public API will resolve a dataset identifier and dimension selections,
load the metadata, delegate retrieval, and format a PxWeb API 2-compatible
response. Harvesting and retrieval may share implementation code while exposing
separate callable interfaces. This public API remains future work.

Additional information belongs in structured `extension` objects. Initial
validation should focus on usable structure and essential identity rules.

## Dataset attributes

One document describes the basic catalog information for one language.

Both documents require the same `identity` object, containing required
`provider_code`, `dataset_code`, and `language` (`sv` or `en`). The dataset code
is nonblank, opaque, case-sensitive, unique within the provider, and preserved
across languages. The definition is shared through a schema reference.

| Attribute | Required | Meaning |
| --- | --- | --- |
| `identity` | Yes | Provider code, dataset code, and language |
| `label` | Yes | Nonblank title in that language |
| `description` | No | Longer descriptive text |
| `updated` | No | Provider-reported update date or timestamp |
| `next_release` | No | Provider-announced next release date or timestamp |
| `time_unit` | No | Time granularity; initially a nonblank string without an enum |
| `first_period` | No | First covered period, preserving period notation |
| `last_period` | No | Last covered period, preserving period notation |
| `discontinued` | No | Explicit publication status; omission means unknown |
| `source_url` | No | Human-facing dataset page |
| `doc_url` | No | Documentation or methodology page |
| `extension` | No | Additional structured information |

## Dataset metadata attributes

| Attribute | Required | Meaning |
| --- | --- | --- |
| `identity` | Yes | Same identity as the basic document |
| `id` | Yes | Nonempty, ordered list of unique dimension codes |
| `dimension` | Yes | Nonempty mapping from dimension codes to their definitions |
| `role` | No | JSON-stat-style `time`, `geo`, and `metric` dimension assignments |
| `subject` | No | Subject classification object |
| `paths` | No | Multiple thematic classification chains |
| `official_statistics` | No | Whether the source identifies the dataset as official statistics |
| `source` | No | Attribution text |
| `note` | No | Dataset-level notes as an array of strings |
| `contact` | No | Array of contact objects |
| `metadata_url` | No | Upstream metadata resource |
| `retrieval` | No | Retrieval implementation identifier and dataset-specific configuration |
| `extension` | No | Additional structured information |

`data_url` is not a generic top-level field. It may appear inside a retrieval
implementation's configuration. `metadata_url` is an upstream resource reference,
not automatically an input to observation retrieval.

## Nested structures

- **Dimension:** required `label` and `category`; optional `note`, `link`, and
  `extension`.
- **Category:** required `index` mapping category codes to zero-based positions
  and `label` mapping codes to text; optional `child`, `coordinates`, `unit`,
  `note`, and `extension`.
- **Unit:** optional `label`, `symbol`, `position`, `decimals`, and `extension`.
- **Subject:** optional `code` and `label`, requiring at least one; optional
  `extension`.
- **Paths:** array of objects containing a nonempty `path` array and optional
  `extension`. Each category node has `code`, `label`, and optional `extension`.
  These describe thematic membership, never access routes or dataset access keys.
- **Contact:** optional `name`, `organization`, `mail`, `phone`, `raw`, and
  `extension`.
- **Retrieval:** required `type` and object-valued `config`. The implementation
  defines and validates the contents of `config`.

Dimension-level behavior such as `elimination` can live in `extension` without
becoming mandatory for every source.

Category `child` maps parent codes to child-code arrays; `coordinates` maps codes
to longitude/latitude pairs; `unit` and `note` map codes to unit objects and note
arrays. Dimension `link` is an open link-relation map. Other defined objects
allow extra fields only in `extension`; retrieval `config` is implementation-owned.

## Validation approach

Require essential identity, language, and dimension structure. Keep descriptive
fields optional; omit unavailable values instead of inventing defaults. Reject
unknown fields on defined objects while allowing arbitrary JSON inside
`extension`. Retrieval `config` follows its implementation-owned schema.

Ordering must be explicit and internally consistent: dimension codes correspond
to `id`, category positions are unique and contiguous, and associated category
maps reference existing codes.

JSON Schema can enforce types, required fields, language enums, nonempty
collections, unique dimension IDs in an array, and nonnegative integer category
positions. Equality between dimension keys and `id`, unique/contiguous position
values across a category mapping, category-map correspondence, role references,
and identity agreement between the two documents require application validation.
These application-level relationships are not checked by the repository's
structural schema/example validator. Retrieval config contents and actual text
language also require implementation validation.

The validation command enforces URI, date, and date-time formats. Update/release
dates accept a calendar date or a timestamp with timezone; period strings retain
their original notation. Versioning and publication remain separate steps.
