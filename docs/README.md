# System decisions and dataset contracts

The system decisions below are agreed architectural direction, not a claim that
the applications already implement them. Provider, dataset, harvest-input, and
adapter config contracts form version 1.0.0. See the [schema index](../schemas/README.md) for their locations.

## Agreed system decisions

### Hosting and responsibilities

A hosted PostgreSQL catalog is managed through an authenticated API. Harvest
workers access that API rather than connecting directly to the database. The
catalog API and Harvest worker are separate repositories and applications.
Initially, Harvests are manually requested through the API, queued durably, and
executed one at a time globally. Observation storage is outside the current scope.

| Information | Responsibility |
| --- | --- |
| Provider descriptions | Catalog-managed identity and descriptive records |
| Harvesting configuration | Inputs required to initialize a harvest adapter |
| Dataset-specific retrieval configuration | Information needed to retrieve observations for a particular dataset |

Shared contracts live here as versioned JSON Schemas. The current adapter input
contracts are also defined here under `schemas/adapters/`, for consumption by
their implementations. The intended catalog stores configuration values alongside provider
descriptions in the provider's dedicated `harvest` object. Database migrations
belong to the catalog. Release and
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
or relying on provider descriptions. Retrieval implementations own request/response
logic and consume their config contracts from this repository. Credentials remain
deployment concerns. Harvest inputs require `rate_limit`, a nonnegative number
of seconds between request starts; zero means no added delay. Enforcement belongs
to the request mechanism, including concurrent requests within one execution.
Coordinating limits across separate retrieval/harvest processes is an application
concern, not behavior enforced by JSON Schema.

Stored `harvest` requires `adapter`, `languages`, `rate_limit`, and `config`.
Resolved harvest input uses `provider_code` from the provider's `code`, a selected
`language`, and the same `adapter`, `rate_limit`, and `config`. The application
checks that the selected language belongs to the configured list. Kolada accepts
only `sv`; PXWeb accepts `sv` or `en`, subject to actual upstream support.

PXWeb v1 harvest config requires `base_api_url` and a nonempty `database_ids`
string array. PXWeb v2 requires `base_api_url`. Kolada needs no adapter-specific
settings. Extra inputs go in config `extension`. Small provider-specific behavior,
such as marking a particular database discontinued, may be implemented directly
in adapter code; no generic configuration machinery is required.

Both PXWeb retrieval configs require an absolute `data_url`. Kolada's can be empty;
it uses dataset code to determine KPI and municipality/OU kind. Municipality datasets retain the KPI code; OU datasets append `_OU`.
Implementing the provider merge belongs to the worker project.

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
- **Retrieval:** required `type` (`pxweb_v1`, `pxweb_v2`, or `kolada`) and
  object-valued `config`, validated against the corresponding adapter contract.

Dimension-level behavior such as `elimination` can live in `extension` without
becoming mandatory for every source.

Category `child` maps parent codes to child-code arrays; `coordinates` maps codes
to longitude/latitude pairs; `unit` and `note` map codes to unit objects and note
arrays. Dimension `link` is an open link-relation map. Other defined objects
allow extra fields only in `extension`; retrieval `config` uses its adapter contract.

## Validation approach

Require essential identity, language, and dimension structure. Keep descriptive
fields optional; omit unavailable values instead of inventing defaults. Reject
unknown fields on defined objects while allowing arbitrary JSON inside
`extension`. Retrieval `config` follows its adapter-specific schema.

Ordering must be explicit and internally consistent: dimension codes correspond
to `id`, category positions are unique and contiguous, and associated category
maps reference existing codes.

JSON Schema can enforce types, required fields, language enums, nonempty
collections, unique dimension IDs in an array, and nonnegative integer category
positions. Equality between dimension keys and `id`, unique/contiguous position
values across a category mapping, category-map correspondence, role references,
and identity agreement between the two documents require application validation.
These application-level relationships are not checked by the repository's
structural schema/example validator. Actual text language, upstream URL meaning,
and upstream language support require implementation validation.

The validation command enforces URI, date, and date-time formats. Update/release
dates accept a calendar date or a timestamp with timezone; period strings retain
their original notation. Versioning and publication remain separate steps.

## How the documents connect

1. Store descriptive provider fields and optional `harvest` together. A provider
   without `harvest` is still a valid descriptive record, but has no configured
   harvest execution.
2. For an execution, copy provider `code` to input `provider_code`; select one
   configured language; copy `adapter`, `rate_limit`, and `config` from `harvest`.
   Check that the language is configured and supported by the upstream source.
3. The adapter produces Dataset and Dataset metadata documents with matching
   `identity`. Persist them consistently; changing provider settings must not
   silently change the inputs of an already-running Harvest.
4. Later, retrieval loads metadata identity, dimensions, and `retrieval`. It
   dispatches on `retrieval.type` using `retrieval.config` without reconstructing
   the original harvest configuration. Missing retrieval means observation
   fetching is not configured for that metadata document.

The stored configuration and resolved input contracts exist. The catalog API owns
CRUD routes, atomic pair persistence, retry semantics, and the initial Harvest job
requests, progress/outcomes, and submission envelopes in its OpenAPI contract.
It reuses these shared document schemas. Separate lifecycle JSON Schemas can be
added here when a demonstrated need arises; they are not prerequisites for 1.0.0.

## Remaining work

The database/API decision record now lives in `DATABASE.md` in the separate
`nordicintel-catalog-api` repository, alongside its implementation planning.

The [roadmap](ROADMAP.md) separates publication of the foundational contracts from
parallel catalog API and worker implementation. End-to-end application readiness
is not a prerequisite for releasing this collection.

## Real-data check, 2026-09-12

107 real Dataset/metadata pairs were projected from 104 successful rerun outputs
and three additional database samples. All passed the current schemas after
encoding 22 source-page URLs; no schemas were loosened. Explicit dimension/category
consistency checks passed for all pairs, with ordering preserved. Ten PXWeb v2
metadata URLs were replaced with the upstream-advertised language-specific links.

Coverage includes PXWeb v1, SCB and SSB on v2, both Kolada data kinds, both ASUB
databases, and all three configured Konjunkturinstitutet databases. The StatFin
archive supplement encountered unavailable branches/rate limiting and timed out;
it is not covered. Kolada OU N01967 still has no successful source metadata.

Five small observation requests built from projected metadata returned HTTP 200
(CSN, SCB, SSB, Kolada municipality, Kolada OU). CSN's response contains a synthetic
ContentsCode outside its dimension order, demonstrating that retrieval also needs
provider-aware normalization. This is sample evidence, not a complete retrieval
implementation or an automatic check of the text's actual language.

Local projections, source hashes, exact URL edits, errors, and request/response
files are saved under ignored `tmp/contract-check/20260912-live-examples/`.
The scripts are temporary; no backend code or source harvest files were changed.
