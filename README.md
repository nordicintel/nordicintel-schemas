# NordicIntel schemas

Shared JSON contracts for the NordicIntel catalog and harvesting system.

Version **1.0.0** defines eight foundational contracts for independently developed
catalog API and Harvest worker projects. Consume the exact versioned JSON URLs
below; `main` is development content.

## Structure

- `schemas/`: shared JSON Schema definitions.
- `examples/`: representative JSON documents for the contracts.
- `docs/`: contract explanations and decisions.

See [system decisions and dataset contracts](docs/README.md) for the agreed
architecture, ownership and identity rules, and dataset fields.
The [roadmap](docs/ROADMAP.md) tracks completed work, integration, and the path to 1.0.

## Intended scope

Define provider records, basic dataset information, detailed metadata, and shared
harvest and retrieval configuration. The catalog API owns CRUD, persistence, and
initial Harvest job/submission interfaces through its OpenAPI contract.
The current adapter input contracts live in `schemas/adapters/`; their
implementations consume those contracts and define their behavior.
Database migrations and HTTP routes/OpenAPI definitions remain with their applications.

Resolved harvest inputs require `provider_code`, `language`, and `rate_limit`.
Harvest output must preserve provider/language identity in both dataset documents
and contain metadata in the requested language. Structural contracts exist;
actual language and cross-document consistency remain application responsibilities.

## Working approach

Keep contracts small and validate examples before adopting them in applications.
JSON Schemas are the source of truth; language-specific models can consume them.
See the [roadmap](docs/ROADMAP.md) for the next integration steps.

## Provider contract

[Provider schema](schemas/provider.schema.json) defines a provider's identity and
descriptive information. `code` and `label` are required; `description`,
`country_code`, `website`, `harvest`, and `extension` are optional. Omit absent optional
fields rather than setting them to `null`.

`code` is stable across display-name and adapter changes; other documents refer
to it as `provider_code`. Labels and descriptions contain nonblank `sv` and/or
`en` translations, independently of adapter language support. The optional
country identifies the provider's home country, not its dataset coverage.

Unknown top-level fields are rejected. Additional descriptive information can
go inside `extension`, including nested objects and arbitrary JSON values.
Adapter selection, endpoints, and request settings live in the dedicated
`harvest` object alongside public information, not in descriptive `extension`.
Public-facing provider responses can omit `harvest`.

Websites must be absolute HTTP(S) URIs with a host. Validation enables URI format
checking explicitly; consumers must do the same. See the
[provider examples](examples/provider) for valid and invalid documents.

## Harvest and retrieval inputs

[Stored harvest configuration](schemas/harvest-config.schema.json) contains
`adapter`, `languages`, `rate_limit`, and adapter-specific `config`.
[Resolved harvest input](schemas/harvest-input.schema.json) contains `adapter`,
`provider_code`, one `language`, `rate_limit`, and `config`; all are required.
`rate_limit` is minimum seconds between request starts, not requests per second.
It accepts a nonnegative number; zero means no added delay.

| Adapter | Harvest `config` | Metadata `retrieval.config` |
| --- | --- | --- |
| `pxweb_v1` | `base_api_url`, nonempty `database_ids` string array | Absolute `data_url` |
| `pxweb_v2` | `base_api_url` | Absolute `data_url` |
| `kolada` | `{}` | `{}` |

These contracts are in [schemas/adapters](schemas/adapters). Optional `extension`
objects allow extra adapter inputs. Provider-specific branches in adapter code
are fine; these schemas do not require a declarative rule system. Kolada uses
Swedish only; the contract is designed for municipality and OU datasets under one provider.

Retrieval uses metadata identity and dimensions plus its own config, without
reconstructing harvest initialization. PXWeb URLs preserve the complete endpoint,
including database/path/language where applicable. Kolada resolves KPI and data
kind from dataset code; municipality codes retain the KPI code and OU codes append `_OU`. These contracts
do not implement retrieval or the adapter merge.

## Dataset contracts

- [Dataset](schemas/dataset.schema.json): required `identity` and `label`, plus
  optional catalog information.
- [Dataset metadata](schemas/dataset-metadata.schema.json): required `identity`,
  `id` (dimension order), and `dimension`, plus optional details and retrieval config.

Both use `identity: {provider_code, dataset_code, language}` with all three fields
required. Language is `sv` or `en`. The metadata schema references the Dataset
schema's identity definition directly. See the [contract reference](docs/README.md)
for nested fields and application-level consistency requirements.

## Validation

Use Python 3.12 and [uv](https://docs.astral.sh/uv/). Dependencies are locked in
`uv.lock`; this is development tooling, not a Python distribution.

```sh
uv run --locked python scripts/validate.py
uv run --locked python -m unittest discover -s tests
```

The same commands run on pushes to `main`. An empty scaffold passes ordinary
validation but cannot be released. See [examples](examples/README.md) for the
example layout. Validation resolves references locally without network access.

Examples include five complete pairs projected from saved real adapter outputs;
see their [provenance](examples/README.md#real-dataset-pairs). These demonstrate
contract compatibility, not completed worker/catalog integration.

## Versioned schemas

`VERSION` is the single collection version, currently `1.0.0`. Use matching Git
tags such as `v1.0.0`. Before 1.0, contracts may change; after 1.0, incompatible
changes require a major version, compatible additions a minor version, and
nonbreaking corrections a patch version. Describe changes in GitHub release notes.
Review compatibility for both producers and consumers.

Schemas use JSON Schema Draft 2020-12. Each `schemas/*.schema.json` file declares:

- `$schema`: `https://json-schema.org/draft/2020-12/schema`
- `$id`: its exact versioned URL, for example
  `https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/provider.schema.json`

Use relative `$ref` links between files and fragments for local definitions.
Keep `$id` at file roots; use `$defs` for subschemas. Update all file identifiers
when changing `VERSION`. Consume release URLs, not `main`.

## Direct schema URLs

- [Provider](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/provider.schema.json)
- [Dataset](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/dataset.schema.json)
- [Dataset metadata](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/dataset-metadata.schema.json)
- [Harvest config](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/harvest-config.schema.json)
- [Harvest input](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/harvest-input.schema.json)
- [PXWeb v1](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/adapters/pxweb_v1.schema.json)
- [PXWeb v2](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/adapters/pxweb_v2.schema.json)
- [Kolada](https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v1.0.0/schemas/adapters/kolada.schema.json)

## Manual release

Release publication is manual. Keep **release immutability** enabled in GitHub's
repository settings. Validate the intended commit and wait for its CI to pass
before publishing.

1. Update `VERSION` and schema identifiers; commit the intended release on `main`.
2. Run tests, then `uv run --locked python scripts/validate.py --release`.
   This checks the clean tree, nonempty collection, and unused tag locally and
   on configured remotes. It prints the exact checked commit and creates nothing.
3. Manually create an annotated `v<VERSION>` at that checked commit, push the
   commit and tag, and prepare a draft GitHub release with release notes.
4. Check out that tag and run
   `uv run --locked python scripts/validate.py --published`.
   It fetches every schema URL, compares the JSON with the checked-out release,
   and verifies references through the validated collection.
5. Publish the stable release, then repeat published verification and return to `main`.

Published versions stay unchanged. There is no custom archive distribution, package registry,
automatic publication, or required pull-request process.

## License

[Apache License 2.0](LICENSE).
