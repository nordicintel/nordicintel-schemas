# NordicIntel schemas

Shared JSON contracts for provider descriptions and statistical dataset documents.
The next model direction is specified in [DATASET-MODEL.md](DATASET-MODEL.md):
one combined multilingual Dataset, with Python/Pydantic as authority. See the
[implementation handoff](DATASET-MODEL-HANDOFF.md). It is not yet an application
or released-contract change; the collection described below remains unchanged.

This branch prepares **2.0.0**, which is **not published**. Existing applications
continue consuming the immutable [1.0.0 release](https://github.com/nordicintel/nordicintel-schemas/releases/tag/v1.0.0).

## Contracts

| Schema | Purpose |
| --- | --- |
| [Provider](schemas/provider.schema.json) | Stable identity and descriptive translations; no Harvest configuration |
| [Dataset](schemas/dataset.schema.json) | Basic table information, identity, source, subject and thematic paths |
| [Dataset metadata](schemas/dataset-metadata.schema.json) | Ordered statistical dimensions, PX extensions and implementation-owned retrieval config |
| [JSON-stat structures](schemas/common/jsonstat.schema.json) | Reusable normalized dimension, category, unit, role, note and link definitions |
| [PX extensions](schemas/extensions/px.schema.json) | Shared PX metadata vocabulary, independent of the producing adapter |

See the [contract reference and migration mapping](docs/README.md),
[overview](OVERVIEW.md), [roadmap](docs/ROADMAP.md), and
[example provenance](examples/README.md).

JSON Schemas are authoritative for shared documents. Harvest owns adapter inputs,
registration, controls and its single configuration JSON file. Retrieval implementations
own their settings. Application OpenAPI describes HTTP behavior; database migrations
belong to the applications. Adding an adapter alone requires no shared-schema release.

## Validation

Use Python 3.12 and uv; development dependencies are locked in `uv.lock`.

```sh
uv run --locked python scripts/validate.py
uv run --locked python -m unittest discover -s tests
```

Validation is structural only: schema validity, versioned IDs, relative references,
formats, and valid/invalid examples. No network retrieval is used. Cross-document
identity, category ordering consistency, references to existing codes, and actual
text language remain application responsibilities.

Tests also check 15 illustrative public responses against pinned offline upstream
contracts. Their exact known PxWeb incompatibilities are asserted, not hidden.
See [public example results](tests/public/README.md). These do not claim a working
public API or complete PxWeb UI compatibility.

The existing read-only GitHub Actions workflow runs both commands on `main`.
No runtime Python distribution or automated publication is introduced.

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
