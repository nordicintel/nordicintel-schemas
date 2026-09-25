# NordicIntel schemas

JSON Schemas for standardized output from NordicIntel harvesters, scrapers and
wrappers. They guide implementation of those processes; public identifiers,
API responses and presentation belong to consuming systems.

This repository intentionally contains no runtime package, validator, test suite,
generated models, or standalone example collection. The schemas are consumed as
JSON files, and their inline descriptions and examples are the primary reference.

## Schemas

- [`dataset-metadata.schema.json`](schemas/dataset-metadata.schema.json) defines a
  valid JSON-stat2 Dataset in one language, with namespaced extensions: metadata-only
  or with observations parsed from provider files for NordicIntel to store and serve.
- [`provider.schema.json`](schemas/provider.schema.json) currently guarantees only
  `provider_code`. All other Provider content is deliberately open while that model
  is still changing.
- [`retrieval-result.schema.json`](schemas/retrieval-result.schema.json) defines the
  observation fragment returned by an API adapter's live retrieval function. The
  calling service assembles the complete Dataset from it and its catalog metadata.

[`DATASET-METADATA.md`](docs/DATASET-METADATA.md) records the Dataset metadata decisions, semantic
invariants that JSON Schema cannot express, and metadata-only, populated and sparse examples.

[`RETRIEVAL.md`](docs/RETRIEVAL.md) is the contract for the separately installable
retrieval function: packaging, entry-point discovery, inputs, result and errors.

The schemas use JSON Schema Draft 2020-12. The collection version is in [`VERSION`](VERSION).
The prepared `2.0.0` schemas are not yet published; released `1.0.0` files remain
available from their immutable Git tag.

## Metadata-only and file-backed output

The same schema covers two outputs; its existing filename does not limit it to
metadata-only documents:

- **Metadata-only:** emit `value: []` with complete dimensions and actual category
  counts in `size`. Omit `status`.
- **File-backed observations:** when the original provider offers observations only
  in files such as XLS/XLSX or CSV, rather than a reachable observations API,
  scrapers must parse the files into this same JSON-stat2 Dataset **with values**.
  NordicIntel ingests, stores and serves those observations itself.

Observations reflect exactly what the source provides, for scrapers and adapters
alike ([rules](docs/DATASET-METADATA.md#observation-content)): provided values are
kept (numeric zero stays `0`); marker cells get `null` with the marker in JSON-stat2
`status`, unless provider documentation states the marker's value, which is then
used and recorded in a standard substitution note; cells the source has no data for
are left out. Use a dense `value` array only when the source supplies every cell,
otherwise a sparse object keyed by zero-based observation index. The last dimension
varies fastest; dense arrays contain `product(size)` cells. An empty sparse object
`{}` means the source has no data for any cell, not the metadata-only marker `[]`.

Provider URLs stay in `extension.nordicintel`: `data_url` points to the original
provider file, and `metadata_url` can be omitted if no separate metadata resource
exists. Keep the optional `source_url` and `doc_url` as well. These outward-facing
URLs are not replaced by links to NordicIntel's public API endpoints. No new mode
flag, public API contract or separate metadata definitions are introduced.

See the [guide](docs/DATASET-METADATA.md#file-backed-observations) for parsing rules,
status semantics, consumer checks and complete examples, and the
[generated reference](docs/DATASET-METADATA-REFERENCE.md) for property types.

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
