# NordicIntel schemas

JSON Schemas for standardized output from NordicIntel harvesters, scrapers and
wrappers. They guide implementation of those processes; public identifiers,
API responses and presentation belong to consuming systems.

This repository intentionally contains no runtime package, validator, test suite,
generated models, or standalone example collection. The schemas are consumed as
JSON files, and their inline descriptions and examples are the primary reference.

## Schemas

- [`dataset.schema.json`](schemas/dataset.schema.json) defines one complete Dataset
  document in one language.
- [`provider.schema.json`](schemas/provider.schema.json) currently guarantees only
  `provider_code`. All other Provider content is deliberately open while that model
  is still changing.

[`DATASET-MODEL.md`](DATASET-MODEL.md) records the Dataset decisions, semantic
invariants that JSON Schema cannot express, and a complete compact example.

The schemas use JSON Schema Draft 2020-12. The collection version is in [`VERSION`](VERSION).
The prepared `2.0.0` schemas are not yet published; released `1.0.0` files remain
available from their immutable Git tag.

## License

[Apache License 2.0](LICENSE).
