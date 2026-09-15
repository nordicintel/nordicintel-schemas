# Contract reference

The authoritative 2.0.0 collection contains two Draft 2020-12 JSON Schemas:
[Provider](../schemas/provider.schema.json) and [Dataset](../schemas/dataset.schema.json).
It is not published. The previous 1.0.0 release remains unchanged.

## Provider

Required `code` is stable identity; required `label` contains Swedish, English or
both translations. Optional description uses the same structure. Country means
provider location, not dataset coverage; website is an absolute HTTP(S) URL.
Optional descriptive extensions use named objects with arbitrary JSON contents.
Null is not a substitute for omitted optional provider fields. Provider text
languages do not declare adapter support, and Harvest settings belong elsewhere.

## Dataset

See [DATASET-MODEL.md](../DATASET-MODEL.md) for the complete field reference and
the schemas themselves for precise types, descriptions and inline examples.
Each Dataset contains one language's complete metadata, including dimensions and
category labels. `(provider_code, dataset_code, language)` identifies the document;
`dataset_id` is the language-independent `provider_code:dataset_code`.

Updating Swedish does not require reading, merging or replacing English. Never
fabricate another translation or silently substitute its text. Both languages
remain supported, while Swedish providers are the initial product focus.

Dataset extensions at dimension/category level are open JSON objects. This is
intentionally more permissive than Provider's named-object extensions. Unit
objects and link arrays are intentional. Contact `url` remains a direct URL
string; Dataset links and thematic-node links use `rel`/`href` objects.

### Structural versus semantic validation

Normal validation checks required fields, types, enums, formats, schema
references and illustrative examples. It also checks inline `examples` and
`default` values against their containing schemas, including referenced definitions.
Enable URI, email, date and date-time format validation in consuming validators.
Defaults do not insert values: elimination has a false construction default and
elimination_value a null default, but both remain optional on the wire.

Consumers must additionally check:

- Dataset ID equals the exact combined provider and dataset code.
- Ordered dimension IDs correspond exactly to the dimension map.
- Category positions are unique and contiguous from zero, with labels for
  exactly the indexed codes; note/unit keys reference existing categories.
- Role assignments reference existing dimensions, with at most one role per
  dimension. Role arrays need not follow dimension order.
- Supplied elimination values reference existing category codes, without making
  the field mandatory when elimination is true.

Text language, source truth and live resource availability are not established by
schema validation. No semantic-validation framework is provided here.

## Transition from earlier contracts

| Earlier shape | Current shape |
|---|---|
| Basic Dataset plus separate metadata document | One complete Dataset per language |
| Nested identity object | Top-level provider_code, dataset_code, dataset_id and language |
| Combined document with translations blocks (proposal only) | Separate complete Swedish and English documents |
| Separate statistical/PX helper schemas | Dataset-local `$defs`; open dimension/category extensions |
| Source/resource fields spread across documents | Source attribution plus explicit related resource links |
| Retrieval type/config in metadata | Private retrieval settings outside Dataset |
| Python-authoritative model proposal | JSON Schema authority; no model package |

This is a contract replacement, not a compatibility layer or a data migration.
Published 1.0.0 URLs still identify their original documents; prepared 2.0.0 IDs
become consumable only after an explicit future release.

## Ownership

Harvest owns source parsing, normalization, adapter configuration and controls.
Retrieval implementations own executable request configuration. Catalog/API
projects own persistence and HTTP behavior. The Kolada supporting municipality
and OU mapping remains external, without introducing a general code-list framework.
Applications can adopt these contracts independently; no deployment or database
publication policy is included here.
