# Schema overview

**JSON Schema is authoritative.** The unpublished **2.0.0** collection contains
[Provider](schemas/provider.schema.json) and [Dataset](schemas/dataset.schema.json).
Python/Pydantic models and generated schemas are shelved. Existing applications
continue consuming published 1.0.0 until separately updated.

- Dataset is one complete document per `sv` or `en` language, independently
  replaceable. Its public ID is `provider_code:dataset_code`; language identifies
  the document version, not a different dataset.
- Required fields are provider code, dataset code, dataset ID, language, label,
  ordered `dimension_ids` and the `dimension` mapping.
- `source` follows `label`; official-statistics status is first-class and nullable.
  Time granularity uses the seven-value enum documented in the model.
- Categories use explicit index maps. Roles reference dimensions, with at most
  one role per dimension. Elimination defaults to false; its category value is
  always optional and defaults to null.
- Unit objects, precision/position, open dimension/category extensions and
  `rel`/`href` link arrays are intentional. No adapter-specific Dataset schema exists.
- Provider remains descriptive. Harvest owns configuration, adapter validation
  and controls; retrieval settings remain outside Dataset. HTTP and persistence
  belong to consuming applications.

The collection replaces the previous table/metadata split and combined multilingual
proposal. Swedish providers are the initial focus, with both metadata languages
supported. Exact PxWeb UI compatibility does not dictate the model.

Read [the model](DATASET-MODEL.md), [contract reference](docs/README.md) and
[small example set](examples/README.md). No application integration, release or
deployment is implied by these contracts.
