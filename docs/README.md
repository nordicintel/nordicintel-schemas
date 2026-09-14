# Contracts for 2.0.0

Prepared on `public-contract-direction`; not published or adopted by applications.

## Ownership and identity

Shared contracts describe provider information and statistical meaning. Provider
records contain no Harvest settings. Harvest owns controls, adapter input models,
registration and one authoritative configuration JSON file keyed by provider code.
Configuration changes follow normal commits/deployment. Existing queued input
storage can remain; no new snapshot system is introduced here.

Provider identity is `code`; references use `provider_code`. Both dataset documents
require `identity: {provider_code, dataset_code, language}`. Dataset codes are
nonblank, opaque, case-sensitive and provider-scoped. Language is `sv` or `en`;
unsupported Harvest language requests must fail without silent fallback. A Swedish
provider focus does not remove English from the contract.

## Basic information

Required: `identity`, `label`.

Optional: `description`, `updated`, `next_release`, `time_unit`, `first_period`,
`last_period`, `discontinued`, `source`, `subject`, `paths`, `tags`, `sort_code`,
`source_url`, `doc_url`, `extension`.

`subject` has optional `code` and `label`, at least one required. Each thematic
path has a nonempty `path` array; nodes require `code` and `label`, with optional
`sort_code`. Subject, paths and nodes allow structured extensions. These describe
thematic membership, never dataset access routes.

Dates retain date-or-timezone-aware-timestamp notation. Periods retain source
notation and `time_unit` remains a nonblank string. Missing dates, periods or
publication status remain absent, never invented. Public response completeness
and publication eligibility belong to the API.

## Detailed metadata

Required: `identity`, `id`, `dimension`.

Optional: `role`, `note`, `link`, `metadata_url`, `retrieval`, `extension`.

JSON-stat structure is normalized: dimension order is explicit; every dimension
has a nonblank label and category; categories have nonempty index maps and label
maps. Category index values are nonnegative integers. The structure also supports
notes, child relationships, coordinates, units and links. Core units support
`label`, `symbol`, `position`, `decimals`, and structured extensions. The PX unit
profile additionally supports optional string `base` directly.

Role assignments use `time`, `geo`, and `metric`; their array order need not follow
dimension order. Link relations map to arrays of link objects; their vocabulary
remains open. Sorting policy is application logic.

`retrieval` requires nonblank `type` and object `config`. Both new implementation
names and arbitrary config contents are structurally accepted. Implementations
validate settings; `data_url` is not a generic metadata field. Retrieval must work
with dataset identity and dimensions without reconstructing Harvest initialization.

Stored documents omit `class`, `version`, `size` and observation `value`. Public
metadata responses add `class: dataset`, `version: 2.0`, derived `size`, and empty
`value`. Actual observation retrieval remains application work.

## PX extensions and source extras

PX extension definitions derive from the pinned PxTools specification credited
in [reference provenance](../tests/reference/README.md). They are semantic contracts,
not adapter configuration. Any adapter can populate them when their meaning fits.

Root extension fields are `noteMandatory`, `px`, `firstPeriod`, `lastPeriod`,
`tags`, `discontinued`, and `contact`. The `px` object defines the documented
publication, identity, formatting, subject, heading/stub and next-update fields.
Contact's `name`, `organization`, `phone`, `mail`, and `raw` remain optional.

Dimension extension fields are `elimination`, `eliminationValueCode`,
`noteMandatory`, `categoryNoteMandatory`, `refperiod`, `show`, `codelists`,
`measuringType`, `priceType`, `adjustment`, `basePeriod`, and `alternativeText`.
Types/enums follow PX; category-specific maps stay in their native PX locations.
Code-list references require id, label, type and links when provided. No code-list
endpoint behavior is implied.

All these root/dimension attributes are optional. Known fields are validated.
Unknown extension keys must hold **objects**, for example `extension.kolada` or
`extension.upstream`. Inside such named objects, arbitrary nested JSON, arrays,
scalars and nulls are allowed. The rule is not recursively imposed on their contents.
Defined document objects reject unknown fields and null for defined properties.
No Kolada-specific schema or closed adapter list is maintained.

NordicIntel normalization deliberately differs from upstream: omit unavailable
fields instead of nulls/defaults; contact does not require `raw`; PX nextUpdate
accepts valid dates/timestamps rather than the upstream date-only regex; units
retain JSON-stat properties alongside PX `base`. These exceptions are documented,
not applied to the vendored upstream reference.

## Application consistency responsibilities

Ordinary validation enforces structure, not cross-field relationships. Applications
must check matching pair identities; equality of dimension keys and `id`; unique,
contiguous category positions; category-label correspondence; role, child, unit,
coordinate, note, elimination and PX category-map references; and valid note indexes.
Heading/stub dimensions must exist. Actual language and URL meaning are not schema checks.

Basic information is authoritative. When both copies exist, check:

| Basic information | Detailed metadata copy |
| --- | --- |
| first_period / last_period | extension.firstPeriod / lastPeriod |
| discontinued / tags | extension.discontinued / tags |
| subject.code / subject.label | extension.px.subject-code / subject-area |
| next_release | extension.px.nextUpdate |

Compare date/timestamp values by their represented meaning, retaining original
notation in storage. Public projection uses basic values when present. Conflicting
stored copies are an application validation error, not two independent facts.

## Migration from 1.0.0

| Previous location | 2.0.0 location / owner |
| --- | --- |
| provider.harvest; Harvest and adapter input schemas | Harvest project and its single configuration JSON file |
| metadata.source, subject, paths | Basic document source, subject, paths |
| metadata.contact | metadata.extension.contact |
| metadata.official_statistics | metadata.extension.px["official-statistics"] |
| unit.extension.base | unit.base in the PX profile |
| path-node extension.sortCode | path-node sort_code |
| Closed retrieval types and config schemas | Open type/config envelope; implementation validates |
| Loose extension scalars/arrays | Named object such as extension.upstream |

Root table tags/sort codes are now first-class optional basic fields. Public
`variableNames` is derived from ordered dimension labels; public links/access
categories are API-owned. Upstream links retained under extension.upstream are
source references, not NordicIntel public routes.

See [public example results](../tests/public/README.md) for the checked response
mapping and limitations. Application migration, endpoints, queue ownership changes
and publication of this release are separate work.
