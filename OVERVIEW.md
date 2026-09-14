# Schema overview

**Current model:** [DATASET-MODEL.md](DATASET-MODEL.md) defines the agreed combined
multilingual Python model. See its [implementation handoff](DATASET-MODEL-HANDOFF.md)
and [complete proposed examples](docs/model-examples/README.md). The text below
describes the prepared 2.0.0 implementation, not approval to publish it or the
latest redesign direction.

**2.0.0 is prepared on this branch, not published.** Applications still consume 1.0.0.

- Shared schemas describe provider information and statistical documents, using
  a normalized JSON-stat 2 foundation and the PxWeb API 2 table/metadata split.
- Basic information owns source, structured subject and thematic paths. Preserve
  NordicIntel field names; map them into public responses.
- Metadata owns ordered dimensions, notes, links, PX extensions and retrieval.
  Contact and official-statistics status use their native PX extension locations.
- PX extensions describe meaning independently of adapters. Known fields are
  typed; extra information belongs in named objects. Kolada extras remain open.
- Harvest owns controls, common inputs, adapter registration/validation and one
  configuration JSON file. Provider descriptions remain in the catalog.
- Retrieval uses an open type/config envelope; implementations validate settings.
- Provider/dataset identity and sv/en language rules remain. Missing source facts
  remain absent. Static/derived response fields are not stored.
- Basic values are authoritative over optional matching PX copies. Cross-document
  consistency remains an application responsibility; normal validation is structural.
- Real public response examples are checked against pinned upstream contracts;
  known compatibility gaps are explicit. No HTTP API is implemented here.

Next: review the [public-response gaps](tests/public/README.md), then release and
adopt deliberately. Swedish providers are the preferred initial focus, with the
exact list undecided. Harvest persistence and write consistency remain separate
implementation decisions. See the [contract reference](docs/README.md) for details.
