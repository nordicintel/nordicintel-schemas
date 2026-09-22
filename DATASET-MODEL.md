# Dataset model

The authoritative contract is [`schemas/dataset.schema.json`](schemas/dataset.schema.json).
It uses JSON Schema Draft 2020-12 and represents one complete Dataset document in
one language. The schema itself contains the exact types, descriptions, defaults,
and field-level examples; this document records the decisions around it.

## Identity and language

`provider_code`, `dataset_code`, `dataset_id`, and `language` are top-level fields.
The public Dataset identity is `provider_code:dataset_code`; `dataset_id` must be
that exact value. Source dataset codes remain opaque and case-sensitive.

Swedish and English are separate complete documents with the same Dataset identity.
Language is therefore part of the document identity, not the public Dataset ID.
One language can be refreshed without reading, merging, or replacing the other.
Never invent a translation or silently substitute text from another language.

## Dataset fields

Only these fields are required:

- `provider_code`, `dataset_code`, `dataset_id`, and `language`
- `label`
- `dimension_ids` and `dimension`

Optional metadata includes source attribution, description, discontinued and
official-statistics status, update and release dates, time coverage, notes,
subject, dimension roles, links, thematic paths, and contacts. Optional does not
always mean nullable; the schema is authoritative for that distinction.

Important meanings:

- `source` is a provider-reported attribution for the Dataset, not the Provider.
- `updated` is the provider-reported last Dataset modification, including data or
  structural/metadata changes. It is not harvest time.
- `first_period` and `last_period` preserve the provider's notation. An adapter may
  infer them when needed, but must not standardize the stored form.
- `time_unit` is the granularity of time, not publication frequency.
- `official_statistics` and `discontinued` preserve true, false, and unknown.
- Private retrieval configuration remains outside the Dataset document.

## Dimensions and categories

`dimension_ids` is the canonical dimension order. `dimension` maps those codes to
Dimension objects. Each Dimension requires a label and a Category object.

Category requires:

- `index`, mapping category codes to zero-based positions
- `label`, mapping the same category codes to their labels

Dictionary iteration order has no statistical meaning. Optional category notes
and units are keyed by category code. Dimension and Category `extension` objects
are intentionally open for shared metadata that is not yet standardized.

`elimination` says whether a Dimension may be omitted from a selection and defaults
to `false`. `elimination_value` optionally identifies the category used when it is
omitted and defaults to `null`. Defaults are annotations; JSON Schema does not add
them to documents.

## Semantic invariants

JSON Schema handles document structure. Consumers must additionally enforce:

- `dataset_id == provider_code + ":" + dataset_code`.
- `dimension_ids` contains exactly the keys in `dimension`.
- Category positions are unique and contiguous from zero.
- Category labels cover exactly the indexed codes; note and unit keys refer to
  indexed categories.
- Role entries refer to existing Dimensions, and a Dimension has at most one role.
- A non-null `elimination_value` refers to an indexed category.

Adapters own source parsing and mapping into this common model. They should preserve
source identities, ordering, labels, units, notes, attribution, and status rather
than deriving meaning from display text. There are no adapter-specific schemas.

## Compact example

```json
{
  "provider_code": "example",
  "dataset_code": "POP01",
  "dataset_id": "example:POP01",
  "language": "sv",
  "label": "Befolkning efter region och år",
  "source": "Exempelmyndigheten",
  "updated": "2026-09-15",
  "official_statistics": true,
  "time_unit": "annual",
  "first_period": "2024",
  "last_period": "2025",
  "subject": {
    "code": "BE",
    "label": "Befolkning"
  },
  "role": {
    "geo": ["Region"],
    "time": ["Time"]
  },
  "dimension_ids": ["Region", "Time"],
  "dimension": {
    "Region": {
      "label": "Region",
      "elimination": true,
      "elimination_value": "00",
      "category": {
        "index": {"00": 0, "01": 1},
        "label": {"00": "Riket", "01": "Stockholms län"}
      }
    },
    "Time": {
      "label": "År",
      "category": {
        "index": {"2024": 0, "2025": 1},
        "label": {"2024": "2024", "2025": "2025"},
        "unit": {
          "2024": {"label": "antal", "decimals": 0, "position": "end"},
          "2025": {"label": "antal", "decimals": 0, "position": "end"}
        }
      }
    }
  },
  "links": [
    {
      "rel": "source",
      "href": "https://example.org/sv/population",
      "hreflang": "sv"
    }
  ]
}
```

This is illustrative metadata, not a live export and not an additional contract.
