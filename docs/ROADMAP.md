# Roadmap

Updated 2026-09-12. Collection version: **1.0.0**.

## 1. Publish the foundational contracts

The first release contains Provider, Dataset, Dataset metadata, stored Harvest
configuration, resolved Harvest input, and PXWeb v1/v2 and Kolada config schemas.
Validation tooling, CI, manual release checks, and five real projected example
pairs accompany the contracts. Follow the [release procedure](../README.md#manual-release)
for an immutable GitHub release with directly accessible versioned JSON files.

Completed application integration is not a publication prerequisite. No new
Harvest lifecycle schemas or database/API implementation are required for 1.0.0.
See [example provenance](../examples/README.md#real-dataset-pairs) and the
[real-data findings](README.md#real-data-check-2026-09-12) for evidence and limits.

## 2. Build the consuming projects concurrently

- **Catalog API:** a separate repository providing authenticated CRUD over hosted
  PostgreSQL. It owns migrations, persistence, and OpenAPI routes, including initial
  Harvest requests, durable jobs, progress/results, and dataset-pair submission.
- **Harvest worker:** a separate repository owning adapters, upstream requests,
  metadata generation, and submission through the catalog API. Integration has
  been assigned to another agent; do not duplicate that work here.
- Both consume the published 1.0.0 document contracts. Coordinate the minimal
  operational API between them, including consistent pair writes and retries.

Validate direct adapter outputs when available and resolve concrete mismatches.
Keep provider-specific branches practical; no hypothetical collision framework.

## 3. Verify application integration

Exercise a bounded Harvest: API request, durable queue, one global execution,
dataset submission, progress, and completion. Check failure/cancellation, retries,
and restart persistence. Applications enforce matching identities, explicit
ordering, category references, and actual requested-language output.

Exercise retrieval from stored metadata without reconstructing harvest inputs,
including PXWeb response normalization and observation ordering. These checks
belong to the consuming projects; bring demonstrated contract gaps back here.

## Later releases

Add shared operational schemas only when useful. New contracts and compatible
additions receive a minor release; incompatible changes require a major release.
Nonbreaking corrections receive a patch. Never alter published schema contents
or tags. Scheduling, parallel Harvests, and the public PxWeb API 2-compatible
interface remain application work, independent of publishing these contracts.
