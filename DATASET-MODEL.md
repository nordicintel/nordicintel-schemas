# Dataset model

[The schema](schemas/dataset.schema.json) defines metadata output from harvesters,
scrapers and wrappers, one complete document per language. Its field descriptions
and inline examples guide those implementations. Public identifiers, API response
formatting and presentation are responsibilities of consuming systems.

## Identity and language

`provider_code` and the provider's opaque, case-sensitive `dataset_code` identify
the dataset. `language` identifies its metadata variant. Swedish and English
documents can be refreshed independently. Preserve provider codes and text;
do not invent translations or silently substitute languages.

Required fields: `provider_code`, `dataset_code`, `language`, `label`,
`dimension_ids`, and `dimension`. Harvesters do not construct a `dataset_id`.

## Provider metadata and dates

`source` means attribution reported by the provider, which may name another
originating organization. It does not identify the provider.

`updated` means the provider's last reported modification, including data,
structure or metadata changes. `next_release` is the provider's announced next
release. Both accept nonblank strings or null. Preserve the provider's value
as long as a consumer can extract a valid calendar date from it. No timezone,
RFC 3339 format or normalized timestamp is required. For example,
`2026-09-15`, `2026-09-15 09:00:00` and `2026-09-15T09:00:00+02:00` are accepted.
Schema acceptance alone does not establish that a string contains a valid date.

`first_period` and `last_period` preserve provider period notation; they may be
inferred by the implementation. `time_unit` describes period granularity.
Unknown `official_statistics` or `discontinued` values remain omitted or null.

Dataset-level `extension` is an optional open object for additional provider
metadata that cannot be parsed or mapped into the defined Dataset fields.
It supports scalar values, arrays and nested objects. Always use the existing
fields wherever they fit; do not duplicate them or introduce aliases in extension.
URLs belong in the named URL fields or `additional_urls`.

## Dimensions

`dimension` uses JSON-stat2 dimension objects, defined locally in
`$defs/jstat_dimension` and `$defs/jstat_category`. `dimension_ids` retains the
ordered dimension codes for this harvest document. Root `role` identifies time,
geographic and metric dimensions.

The local definitions follow the [JSON-stat2 specification](https://json-stat.org/full/):
category indexes accept ordered code arrays or position maps; labels may be
omitted; a sole category can be identified by its label map without an index.
Notes, hierarchies (`child`), coordinates, units and extensions preserve metadata.
Unit objects allow optional `label`, `decimals`, `symbol`, `position` and extras;
`position` places the symbol. Preserve known units even when precision is unknown,
and omit unavailable `decimals` rather than inventing a value.

Harvest-specific choices are explicit: dimensions include their categories;
resource URLs use the fields below, and dates use the permissive rules above.
This is a harvest metadata document, not a complete JSON-stat2 observation response.

`elimination` and `elimination_value` now belong in each dimension's `extension`.
They mean that the dimension may be omitted from a selection and, optionally,
which category to use when omitted. Their defaults remain false and null.
Other provider extension metadata is allowed. Schema defaults do not insert values.

## URLs

Use these optional string fields for their defined purposes; omit or use null
when unavailable:

| Field | Meaning |
|---|---|
| `source_url` | Provider's human-readable dataset page; unrelated to the attribution in `source` |
| `doc_url` | Primary dataset documentation or methodology |
| `metadata_url` | Provider's dataset metadata endpoint or file |
| `data_url` | Provider's observations endpoint or file |

Resolve relative URLs against the provider's page or endpoint. A URL does not
encode POST bodies or other retrieval configuration.

For resources that do not fit those fields, reuse `$defs/additional_url` through
`additional_urls` at Dataset level or `dimension.<code>.extension.additional_urls`.
Each entry requires `url` and `label`; `description` and extra properties are optional.
Within a dimension, optional `category_id` identifies a category-specific resource.
Omit it for a whole-dimension resource. Dataset-level entries concern the whole
dataset; put category-specific entries under their dimension.

Additional URLs must never replace or duplicate the named URL fields.
Thematic path nodes use an optional plain `url`.

## Contacts

Always map parseable contact information to `name`, `email`, `phone`,
`organization`, `address` and `url`. Extra properties are permitted **only when
the information cannot be parsed or mapped into those attributes**. Do not
introduce aliases or raw copies of already represented information. A contact
must contain at least one property; unknown contact details need not be invented.

## Consumer checks

JSON Schema cannot express all relationships. Consumers check that dimension
codes match `dimension_ids`, position maps are contiguous and unique from zero,
and category metadata and hierarchy references identify existing categories.
Role references must exist and a dimension has at most one role. Non-null
`extension.elimination_value` and URL `category_id` values refer to categories
of their enclosing dimension. Consumers also check date extractability and that
additional URLs do not duplicate named URL fields.

## Example

Illustrative harvester output; further field-level examples live in the schema.

```json
{
  "provider_code": "example",
  "dataset_code": "POP01",
  "language": "sv",
  "label": "Befolkning efter region och år",
  "source": "Exempelmyndigheten",
  "updated": "2026-09-15 09:00:00",
  "time_unit": "annual",
  "dimension_ids": ["Region", "Time"],
  "role": {"geo": ["Region"], "time": ["Time"]},
  "dimension": {
    "Region": {
      "label": "Region",
      "category": {
        "index": ["00", "01"],
        "label": {"00": "Riket", "01": "Stockholms län"}
      },
      "extension": {
        "elimination": true,
        "elimination_value": "00",
        "additional_urls": [
          {
            "url": "https://example.org/regions/01/boundaries",
            "label": "Länsgränser",
            "description": "Kartunderlag för regionen.",
            "category_id": "01"
          }
        ]
      }
    },
    "Time": {
      "label": "År",
      "category": {
        "index": {"2024": 0, "2025": 1},
        "label": {"2024": "2024", "2025": "2025"}
      }
    }
  },
  "source_url": "https://example.org/population",
  "doc_url": "https://example.org/population/methodology",
  "metadata_url": "https://example.org/api/POP01/metadata",
  "data_url": "https://example.org/api/POP01/data",
  "additional_urls": [
    {
      "url": "https://example.org/population/seminar",
      "label": "Presentation av statistiken",
      "description": "Inspelat seminarium.",
      "media_type": "video/mp4"
    }
  ],
  "contacts": [
    {
      "organization": "Exempelmyndigheten",
      "email": "statistics@example.org",
      "opening_hours": "Vardagar 09–15"
    }
  ]
}
```
