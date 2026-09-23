# Dataset metadata

[The schema](../schemas/dataset-metadata.schema.json) defines a JSON-stat2 metadata-only
Dataset for harvester, scraper and wrapper output, one complete document per
language. Its definitions are local and require no network access. Standard fields
follow the [published JSON-stat2 Dataset schema](https://json-stat.org/format/schema/2.0/dataset.json)
(v1.05, 2025-06-13); this profile adds constraints and namespaced metadata.

## Standard structure

Required fields are `version: "2.0"`, `class: "dataset"`, `value: []`, `id`,
`size`, `dimension`, `label` and `extension.nordicintel`.

`id` lists dimension codes in order; `size` lists their actual category counts in
that same order. Neither changes because observations are omitted. `value` must
be present and empty. `id` is not a combined Dataset identifier.

Use standard `label`, `source`, `updated`, `note`, `role`
and `dimension` wherever applicable. Omit unknown standard fields instead of
emitting null. Public identifiers and populated observation responses belong to
consuming systems. Standard tools can read the metadata; tools requiring data
still need observations.

## Namespaces and identity

Every extension is an object whose keys identify namespaces:

| Namespace                   | Contents                                                 |
| --------------------------- | -------------------------------------------------------- |
| `extension.nordicintel`     | Shared fields defined by this schema                     |
| `extension.<provider_code>` | Additional metadata specific to a provider               |
| `extension.<adapter_type>`  | Additional metadata shared by providers using an adapter |

**Every namespace body accepts arbitrary additional properties**, including scalars,
null, arrays and nested objects. Namespace bodies themselves must be objects.
Defined fields retain their declared types and constraints. Use existing
JSON-stat2 or NordicIntel fields whenever they fit; never duplicate, alias or
bypass them through an extension. Reserve `nordicintel` for shared metadata.
Provider and adapter namespace names must be distinguishable; use the actual
provider code or established adapter type, not arbitrary per-record names.

Dataset `extension.nordicintel` requires `provider_code`, the provider's opaque,
case-sensitive `dataset_code`, and `language` (`sv` or `en`). Swedish and English
documents are independent. Preserve provider text and codes; never invent or
silently substitute translations. Harvesters do not construct a `dataset_id`.

Other shared Dataset fields remain optional inside that namespace:
`description`, `discontinued`, `official_statistics`, `time_unit`,
`first_period`, `last_period`, `next_release`, `subject`, `paths` and `contacts`.
Their existing meanings, nullable types and defaults remain defined in the schema.
Schema defaults annotate documents; they do not insert values.

## Attribution and dates

Root `source` is attribution reported by the provider and may name another
originating organization. It does not identify the provider.

Root `updated` records the last provider-reported modification, including data,
structure or metadata changes. Extract a valid `YYYY-MM-DD` calendar date without
requiring timezone conversion. Preserve useful original text as `updated_original`
in the provider or adapter namespace, for example
`extension.pxweb_v2.updated_original`. Omit root `updated` when unknown or when no
valid supported date can be extracted; do not invent one. The published schema
restricts date-only years to 1900–2099, which this profile follows.

`extension.nordicintel.next_release` remains permissive provider date/timestamp
text or null. `first_period` and `last_period` preserve provider period notation
and may be inferred by the implementation; `time_unit` describes granularity.
Unknown `official_statistics` or `discontinued` remains omitted or null.

## Dimensions and category metadata

Dimension `category.index` accepts an ordered code array or a code-to-position
map. Labels are optional when an index exists. A single category can instead be
identified by a one-entry label map. Category notes, hierarchies (`child`),
coordinates and units remain in their standard locations.

Unit `label`, `decimals`, `symbol` and `position` are optional. Preserve known
units without inventing precision; `position` places the symbol. Extra unit
metadata follows the category namespace convention below.

Shared dimension fields live in
`dimension.<id>.extension.nordicintel`: `elimination` (default false),
`elimination_value` (default null), optional attribution `source`, and permissive
provider update text `updated`. A supplied elimination value identifies an
existing category. The published Dataset schema does not allow dimension-level
`class`, `source` or `updated`, so they are not emitted as standard dimension fields.

There is no `category.extension`. Additional category metadata goes under the
enclosing dimension's namespace as `categories.<category_code>`, for example
`dimension.Region.extension.example.categories.01`. Each category entry is an
open object. Shared custom category fields use `nordicintel.categories`; provider
and adapter extras use their own namespace's `categories`. Keep standard category
fields in `category`, rather than repeating them in these objects.

## Provider URLs and additional resources

The following optional fields belong in `extension.nordicintel`. Each accepts
an absolute HTTP(S) URL or null when unknown; omission is also allowed.

| Field          | Purpose                                             |
| -------------- | --------------------------------------------------- |
| `source_url`   | Provider's human-readable Dataset page               |
| `doc_url`      | Provider's primary documentation or methodology      |
| `metadata_url` | Provider's metadata endpoint or file, for refetching  |
| `data_url`     | Provider's observation endpoint or file, for requests |

These URLs point **outward to the provider**. Current adapters supply both
`metadata_url` and `data_url` so downstream processes can reuse them directly
instead of reconstructing URLs from API conventions. Keep supplying them even
when the endpoint could be derived from other metadata. A URL does not encode
POST bodies or other retrieval configuration.

This model is for harvesters, scrapers and adapters, not the public API.
Public API data and metadata links point inward to that API's own endpoints;
they are separate from these provider URLs. Do not replace the named URL fields
with `href`, `link.describedby` or `link.related` entries.

Standard `href` and `link` remain available for additional resources. Each link
entry requires `href` and a descriptive `label`; include `type` when known.
Use `describedby` for additional documentation and `related` for other supporting
resources. Resolve relative URLs against the provider's page or endpoint.

Dimensions use the same `href` and `link` structures. A dimension resource can
set `extension.nordicintel.category_id` to an existing category of that dimension;
omit it for a dimension-wide resource. Dataset links concern the whole Dataset.
Custom explanatory text belongs in the entry's
`extension.nordicintel.description`. Other entry metadata uses provider/adapter
namespaces. Thematic path nodes and contacts remain custom NordicIntel structures
and keep their existing `url` attributes.

## Contacts

Within `extension.nordicintel.contacts`, always map parseable information to
`name`, `email`, `phone`, `organization`, `address` and `url`.
Extra properties are allowed only for information that cannot be parsed or mapped
into those attributes. Do not introduce aliases or raw duplicates. At least one
property is required; do not invent unknown details.

## Consumer checks

Enable format checking when validating. JSON Schema cannot enforce every
relationship: consumers check that `id` matches dimension keys, `size` matches
category counts, index-map positions are unique and contiguous from zero, and
category metadata and hierarchy references exist. Roles reference existing
dimensions, with at most one role per dimension. Check elimination values,
namespaced category entries and resource category IDs against their enclosing
dimension, and check namespace ownership and resource duplication.

## Example

One complete metadata document; further field-level examples live in the schema.

```json
{
  "version": "2.0",
  "class": "dataset",
  "label": "Befolkning efter region och år",
  "source": "Exempelmyndigheten",
  "updated": "2026-09-15",
  "note": ["Avser årets slut."],
  "id": ["Region", "Time"],
  "size": [2, 2],
  "role": { "geo": ["Region"], "time": ["Time"] },
  "dimension": {
    "Region": {
      "label": "Region",
      "category": {
        "index": ["00", "01"],
        "label": { "00": "Riket", "01": "Stockholms län" }
      },
      "link": {
        "related": [
          {
            "href": "https://example.org/regions/01/boundaries",
            "label": "Länsgränser",
            "extension": {
              "nordicintel": {
                "category_id": "01",
                "description": "Kartunderlag för regionen."
              }
            }
          }
        ]
      },
      "extension": {
        "nordicintel": {
          "elimination": true,
          "elimination_value": "00"
        },
        "example": {
          "categories": {
            "01": { "boundary_revision": "2025" }
          }
        }
      }
    },
    "Time": {
      "label": "År",
      "category": {
        "index": { "2024": 0, "2025": 1 },
        "label": { "2024": "2024", "2025": "2025" }
      }
    }
  },
  "value": [],
  "extension": {
    "nordicintel": {
      "provider_code": "example",
      "dataset_code": "POP01",
      "language": "sv",
      "source_url": "https://example.org/population",
      "doc_url": "https://example.org/population/methodology",
      "metadata_url": "https://example.org/api/POP01/metadata",
      "data_url": "https://example.org/api/POP01/data",
      "time_unit": "annual",
      "contacts": [
        {
          "organization": "Exempelmyndigheten",
          "email": "statistics@example.org",
          "opening_hours": "Vardagar 09–15"
        }
      ]
    },
    "pxweb_v2": {
      "updated_original": "2026-09-15 09:00:00"
    },
    "example": {
      "revision_policy": "Preliminary figures may be revised."
    }
  }
}
```
