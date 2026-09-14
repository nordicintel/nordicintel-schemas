# Schema direction

Working decisions for the next contract review. The published **1.0.0** schemas
remain unchanged; this document describes direction, not implemented changes.

## Agreed direction

- **Settle the public contract first.** Target PxWeb API 2 compatibility for table
  listings, basic information, metadata, and eventual data requests. Check actual
  response examples before redesigning the shared schemas.
- **Use JSON-stat 2 as the statistical foundation.** Reuse its field meanings and
  structures for dimensions, categories, ordering, roles, labels, notes, units,
  and links. Avoid custom restrictions without a demonstrated application need.
- **Define extensions explicitly.** Support dataset-, dimension-, and
  category-level information where needed. Reuse common PX definitions across
  PXWeb v1/v2; keep genuinely source-specific information separate. Known fields
  should be typed, with structured room for additional information.
- **Keep catalog concerns distinct.** Provider/dataset identity, language, and
  retrieval configuration have their own responsibilities. This does not require
  a separate complete dataset model for every adapter.
- **Preserve identity and language.** Providers use `code`; references use
  `provider_code`. Dataset identity is provider plus dataset code; `sv`/`en`
  identify metadata languages. Harvests must produce the requested language
  without silent fallback.
- **Preserve explicit ordering.** Dimension and category order must be consistent
  with future observation values. Sorting policy belongs to application logic.
- **Keep stored metadata lean.** Static `class`/`version` and derived `size` need
  not be stored. Observation `value` remains outside metadata harvesting; public
  responses supply the fields required by their target format.
- **Keep retrieval self-contained.** Dataset retrieval configuration and dimension
  metadata must be sufficient without reconstructing harvest initialization.
- **Keep JSON Schemas authoritative.** Implementations consume versioned contracts;
  published releases remain immutable. HTTP behavior belongs in application OpenAPI.

## Next decisions

Map existing fields to JSON-stat core, shared/PX extensions, source-specific
extensions, and catalog information. Settle exact extension names, nesting, and
required fields using saved PXWeb v1/v2 and Kolada examples. Define the initial
PxWeb API 2 compatibility scope and verify representative public responses.

Moving Harvest controls into the harvesting project is the intended ownership
direction; persistence and write-consistency details remain unresolved and are
not statistical schema decisions.
