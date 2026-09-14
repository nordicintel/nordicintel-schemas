# Schema collection

Version 2.0.0 (unpublished) contains provider, dataset and dataset-metadata document
schemas plus reusable common/jsonstat and extensions/px schemas. The latter expose
local `$defs`; their roots validate a core dimension and a root PX extension respectively.

All use Draft 2020-12, versioned file-level `$id` and relative `$ref`. There are no
adapter-specific schemas. Consult [the contract reference](../docs/README.md).
