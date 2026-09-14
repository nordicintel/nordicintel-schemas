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
- **Keep shared JSON Schemas authoritative for exchanged documents.** Focus this
  repository on provider descriptions, dataset documents, and statistical meaning.
  Published releases remain immutable. HTTP behavior belongs in application OpenAPI.

## Harvest and configuration ownership

- **Harvest owns its controls and inputs.** Job controls, queue behavior, common
  inputs (`provider_code`, `language`, `rate_limit`), and adapter registration belong
  in the Harvest project. `rate_limit` remains minimum seconds between request starts.
- **Implementations own configuration validation.** Each adapter defines its input
  model alongside its code. Adding an adapter must not require a shared-schema
  release unless it introduces a new shared output requirement. Remove the current
  adapter-specific input definitions and closed adapter lists from the next shared
  contract design, without modifying published 1.0.0.
- **Extensions describe meaning, not adapter identity.** Any adapter can populate a
  shared PX extension when its information has that meaning. Adapter configuration
  and statistical metadata extensions are separate contracts.
- **Use one Harvest configuration JSON file.** Keep it in the Harvest repository,
  with entries referencing catalog providers by `provider_code`. Public provider
  descriptions remain in the catalog; Harvest configuration moves out of those
  documents. No per-provider files, configuration-editing API, or database
  configuration store. Changes follow normal commits and deployment.
- **Keep loading separate from execution.** Adapters receive validated, resolved
  input without knowing where it was stored. Retain the queue's existing saved
  job input; no additional snapshot system is planned.
- **Retrieval implementations own their settings too.** Shared metadata can require
  a nonblank retrieval `type` and object-valued `config`, without enumerating
  implementations or defining their settings. The selected implementation validates
  those settings.

## Next decisions

Map existing fields to JSON-stat core, shared/PX extensions, source-specific
extensions, and catalog information. Settle exact extension names, nesting, and
required fields using saved PXWeb v1/v2 and Kolada examples. Define the initial
PxWeb API 2 compatibility scope and verify representative public responses.

Narrow the initial public provider set before deployment. Swedish providers are
the preferred initial focus; the exact list is not finalized. Provider location
does not change the shared `sv`/`en` metadata-language contract.

Harvest persistence, write consistency, and handling active jobs during configuration
deployments remain implementation decisions, not statistical schema decisions.
