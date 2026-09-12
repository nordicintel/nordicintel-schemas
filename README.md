# NordicIntel schemas

Shared JSON contracts for the NordicIntel catalog and harvesting system.

Status: pre-1.0, with the first provider contract defined locally. Nothing is published yet.
The intended public repository is `nordicintel/nordicintel-schemas`; publishing
will be a separate step once version 1.0.0 is ready.

## Structure

- `schemas/`: shared JSON Schema definitions.
- `examples/`: representative JSON documents for the contracts.
- `docs/`: contract explanations and decisions.

## Intended scope

Define provider records, normalized dataset metadata, shared adapter input
requirements, and documents exchanged when requesting and reporting Harvests.
Concrete adapter configuration schemas remain with their adapter implementations.
Database migrations and HTTP routes/OpenAPI definitions remain with their applications.

All adapter inputs must require `provider_code` and `language`. Harvest output
must preserve that identity and contain metadata in the requested language.
These requirements still need to be expressed in the contracts and examples.

## Working approach

Start with provider identity, dataset identity, and language. Define small
contracts and examples together, then add automated validation before adopting
them in applications. JSON Schemas are the source of truth; language-specific
models can consume them later.

## Provider contract

[Provider schema](schemas/provider.schema.json) defines a provider's identity and
descriptive information. `code` and `label` are required; `description`,
`country_code`, `website`, and `extension` are optional. Omit absent optional
fields rather than setting them to `null`.

`code` is stable across display-name and adapter changes; other documents refer
to it as `provider_code`. Labels and descriptions contain nonblank `sv` and/or
`en` translations, independently of adapter language support. The optional
country identifies the provider's home country, not its dataset coverage.

Unknown top-level fields are rejected. Additional descriptive information can
go inside `extension`, including nested objects and arbitrary JSON values.
Adapter selection, endpoints, and request settings belong outside this document,
including outside `extension`; that ownership rule is documented, not something
the schema can infer from arbitrary extension contents.

Websites must be absolute HTTP(S) URIs with a host. Validation enables URI format
checking explicitly; consumers must do the same. See the
[provider examples](examples/provider) for valid and invalid documents.

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

## Versioned schemas

`VERSION` is the single collection version, initially `0.1.0`. Use matching Git
tags such as `v1.0.0`. Before 1.0, contracts may change; after 1.0, incompatible
changes require a major version, compatible additions a minor version, and
nonbreaking corrections a patch version. Describe changes in GitHub release notes.
Review compatibility for both producers and consumers.

Schemas use JSON Schema Draft 2020-12. Each `schemas/*.schema.json` file declares:

- `$schema`: `https://json-schema.org/draft/2020-12/schema`
- `$id`: its exact versioned URL, for example
  `https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v0.1.0/schemas/provider.schema.json`

Use relative `$ref` links between files and fragments for local definitions.
Keep `$id` at file roots; use `$defs` for subschemas. Update all file identifiers
when changing `VERSION`. These future URLs become accessible when the public
repository and corresponding tag exist. Consume release URLs, not `main`.

## Manual release

The repository remains local until publication is explicitly requested.
When creating the public repository, enable **release immutability** in GitHub's
repository settings before publishing the first release.

1. Update `VERSION` and schema identifiers; commit the intended release on `main`.
2. Run tests, then `uv run --locked python scripts/validate.py --release`.
   This checks the clean tree, nonempty collection, and unused tag locally and
   on configured remotes. It prints the exact checked commit and creates nothing.
3. Manually create `v<VERSION>` at that checked commit, push the commit and tag,
   and publish a GitHub release for that tag with release notes.
4. Check out that tag and run
   `uv run --locked python scripts/validate.py --published`.
   It fetches every schema URL, compares the JSON with the checked-out release,
   and verifies references through the validated collection.

Published versions stay unchanged. There is no archive, package registry,
automatic publication, or required pull-request process.

## License

[Apache License 2.0](LICENSE).
