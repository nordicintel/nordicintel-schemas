# Schema collection

Two authoritative Draft 2020-12 contracts:

- [provider.schema.json](provider.schema.json): stable descriptive provider record.
- [dataset.schema.json](dataset.schema.json): complete statistical metadata for one language.

Dataset keeps reusable structures in local `$defs`. Each file's `$id` is pinned
to the collection VERSION and future release tag. Current 2.0.0 is unpublished.
Use [the contract reference](../docs/README.md) for semantic responsibilities and
[examples](../examples/README.md) for small, readable instances. No adapter inputs,
Python model package or generated schemas are part of this collection.
