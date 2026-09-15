# Next steps

1. **Prepared here:** Provider and single-language Dataset JSON Schemas, useful
   inline descriptions/examples and a small structural validation suite.
2. **Adopt in Harvest:** map output to the complete Dataset shape, preserve source
   identities/order and add the documented semantic checks. Keep private retrieval
   settings outside Dataset. Use representative sources for integration checks.
3. **Adopt in the catalog/API:** store and read independent language documents.
   Settle persistence and HTTP behavior in that project; development data needs
   no preservation migration.
4. **Publish deliberately when requested:** run release checks and CI, then follow
   the manual publication steps. No push, tag or publication is part of this revision.

JSON Schema is authoritative. Python/Pydantic models are shelved. Exact PxWeb UI
compatibility, observations and deployment are not prerequisites added by this
schema change. Existing 1.0.0 applications remain unchanged until adoption.
