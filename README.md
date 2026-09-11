# NordicIntel schemas

Shared JSON contracts for the NordicIntel catalog and harvesting system.

Status: initial local scaffold, pre-1.0. No contracts are defined or published yet.
The intended public repository is `nordicintel/nordicintel-schemas`; publishing
will be a separate step once version 1.0.0 is ready.

## Structure

- `schemas/`: shared JSON Schema definitions.
- `examples/`: representative JSON documents for the contracts.
- `docs/`: contract explanations and decisions.

## Intended scope

Define provider records, normalized dataset metadata, shared adapter input
requirements, and documents exchanged when requesting and reporting Harvests.
Concrete adapter configuration schemas remain with their adapter implementations.
Database migrations and HTTP routes/OpenAPI definitions remain with their applications.

All adapter inputs must require `provider_code` and `language`. Harvest output
must preserve that identity and contain metadata in the requested language.
These requirements still need to be expressed in the contracts and examples.

## Working approach

Start with provider identity, dataset identity, and language. Define small
contracts and examples together, then add automated validation before adopting
them in applications. JSON Schemas are the source of truth; language-specific
models can consume them later.

No package manager, release workflow, schema dialect, or license has been chosen
in this scaffold. Agree those details as the first contracts take shape.
