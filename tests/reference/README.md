# Offline reference contracts

- **PxWeb API 2:** unmodified `PxAPI-2.yml` from PxTools/PxApiSpecs commit
  `8689b18c2d44d43e03e6e48cea7e95536869be18`. Apache-2.0 licence retained in `pxweb/LICENSE`.
  Source: https://github.com/PxTools/PxApiSpecs/tree/8689b18c2d44d43e03e6e48cea7e95536869be18
- **JSON-stat 2 dataset schema:** unmodified `schemas/vendored/dataset.json` from
  jsonstat/validator commit `febca681ce699b221cb1977c9a7da58a8ede1ee6`. Its parsed contents were checked equal to
  https://json-stat.org/format/schema/2.0/dataset.json when preparing this revision.
  Upstream Apache-2.0 licence retained in `jsonstat/LICENSE`.
  Source: https://raw.githubusercontent.com/jsonstat/validator/febca681ce699b221cb1977c9a7da58a8ede1ee6/schemas/vendored/dataset.json

These are test references, not members of the NordicIntel schema collection.
Normal tests use local files and never download upstream updates. Updating a
reference is an explicit reviewed change. Shared PX definitions derive from the
credited PxTools specification; the source vocabulary/types are retained except
for documented NordicIntel normalization in the contract reference.
