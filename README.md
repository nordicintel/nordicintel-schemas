# NordicIntel schemas

Authoritative JSON Schemas for provider descriptions and statistical dataset
metadata. This branch prepares **2.0.0**, which is **not published**. Existing
applications continue consuming the immutable
[1.0.0 release](https://github.com/nordicintel/nordicintel-schemas/releases/tag/v1.0.0).

## Contracts

| Schema | Purpose |
|---|---|
| [Provider](schemas/provider.schema.json) | Stable identity, translated descriptions and descriptive extras; no Harvest configuration |
| [Dataset](schemas/dataset.schema.json) | Complete metadata for one language, including identity, statistical dimensions, categories and resource links |

Dataset documents for Swedish and English share a dataset ID and can be refreshed
independently. This replaces both the former basic/detail split and the proposed
combined multilingual model. Python/Pydantic model development is shelved;
Python here is validation tooling only.

See [the model](DATASET-MODEL.md), [overview](OVERVIEW.md),
[contract reference](docs/README.md), [examples](examples/README.md) and
[next steps](docs/ROADMAP.md). Schemas include descriptions, inline examples and
documented defaults for implementers.

## Validation

Use Python 3.12 and uv with locked development dependencies:

```sh
uv run --locked python scripts/validate.py
uv run --locked python -m unittest discover -s tests
```

Ordinary validation works offline. It checks Draft 2020-12 structure, versioned
IDs, local references, document examples, inline examples and defaults against
their containing definitions. URI, email, date and date-time formats are enforced.
Defaults are annotations; validation does not populate missing fields.

Cross-field identity, category ordering and reference consistency require consumer
checks described in the contract reference. The validator is structural only;
there is no runtime model package or public-API compatibility test suite.
Read-only GitHub Actions runs the same commands on pushes to `main`.

## Versioning and direct consumption

`VERSION` versions the collection together. Breaking changes require a major
version; compatible additions use minor versions and nonbreaking corrections use
patch versions. Review compatibility for producers and consumers.

Each schema uses Draft 2020-12 and an exact release-tag `$id`, for example:

```text
https://raw.githubusercontent.com/nordicintel/nordicintel-schemas/v2.0.0/schemas/dataset.schema.json
```

The 2.0.0 URLs are reserved for the future release and are not available yet.
Published JSON files are consumed directly, without an archive. Use exact released
tags, not `main`. Internal references remain relative; reusable definitions use
`$defs`. Previously published 1.0.0 URLs and tags remain unchanged.

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
