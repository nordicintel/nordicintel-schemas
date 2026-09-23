# NordicIntel schemas

JSON Schemas for standardized output from NordicIntel harvesters, scrapers and
wrappers. They guide implementation of those processes; public identifiers,
API responses and presentation belong to consuming systems.

This repository intentionally contains no runtime package, validator, test suite,
generated models, or standalone example collection. The schemas are consumed as
JSON files, and their inline descriptions and examples are the primary reference.

## Schemas

- [`dataset-metadata.schema.json`](schemas/dataset-metadata.schema.json) defines a
  valid JSON-stat2 metadata-only Dataset in one language, with namespaced extensions.
- [`provider.schema.json`](schemas/provider.schema.json) currently guarantees only
  `provider_code`. All other Provider content is deliberately open while that model
  is still changing.

[`DATASET-METADATA.md`](docs/DATASET-METADATA.md) records the Dataset metadata decisions, semantic
invariants that JSON Schema cannot express, and a complete compact example.

The schemas use JSON Schema Draft 2020-12. The collection version is in [`VERSION`](VERSION).
The prepared `2.0.0` schemas are not yet published; released `1.0.0` files remain
available from their immutable Git tag.

## Development hooks

The only development dependency is [Ruff](https://docs.astral.sh/ruff/), for Python
linting and formatting. The reference generator itself uses only the standard library.
With Python 3.10+ installed, enable the tracked hook once per clone:

```sh
python -m pip install ruff==0.16.5
git config core.hooksPath .githooks
```

Before each commit, the hook checks staged Python files with `ruff check` and
`ruff format --check`. Changing `ruff.toml` checks all tracked Python files.
Failures block the commit; fixes are explicit so partially staged work stays intact:

```sh
python -m ruff check --fix .githooks
python -m ruff format .githooks
```

Review and restage fixes before committing. Ruff checks Python, not JSON or Markdown.

When `schemas/dataset-metadata.schema.json` is staged for addition or modification,
the hook generates and stages [the property reference](docs/DATASET-METADATA-REFERENCE.md)
from that **staged version**, not from unstaged schema edits. Other commits skip
generation. Local or staged manual reference edits are protected; resolve them before
retrying. The generated reference documents shared objects once, resolves local
references and keeps arbitrary provider fields out of the fixed property inventory.
Required flags apply within the containing object; the schema remains authoritative
for conditional requirements and other validation constraints.

To regenerate manually from the working-tree schema (without staging):

```sh
python .githooks/pre_commit.py --generate
```

[GitHub Actions](.github/workflows/checks.yml) runs Ruff lint and formatting checks
on pushes and pull requests, and verifies that the committed property reference
matches the schema. CI reports failures; it does not modify or commit files.

## License

[Apache License 2.0](LICENSE).
