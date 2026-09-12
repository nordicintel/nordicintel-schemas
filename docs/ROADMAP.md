# Roadmap

Updated 2026-09-12. Current version: **0.1.0**, local and unpublished.

This repository owns JSON contracts and their validation examples. Application
implementations, database migrations, HTTP routes, and deployment belong to the
consuming projects. Keep the initial contracts small and develop directly on
`main`; no extra contribution process or automatic publishing is planned.

## Completed

- [x] Apache-2.0 license, collection versioning, direct versioned schema URLs,
  locked validation tooling, CI, and manual release checks.
- [x] Provider records with optional stored harvest configuration.
- [x] Shared Harvest inputs: provider, language, adapter, `rate_limit`, and config.
- [x] Separate Dataset and Dataset metadata contracts sharing `identity`.
- [x] Harvest/retrieval config contracts for PXWeb v1, PXWeb v2, and Kolada.
- [x] Structural validation of 107 real projected Dataset/metadata pairs after
  documented URL corrections; additional dimension/category consistency checks.
- [x] Small live retrieval probes for PXWeb v1, both sampled v2 providers, and
  Kolada municipality/OU data.

These are contract and sample checks, not proof that the new system is integrated.
See [real-data findings](README.md#real-data-check-2026-09-12) for evidence and limits.

## 1. Confirm backend adoption — underway elsewhere

The user has assigned backend integration to another agent. Do not duplicate that
work here. When its results arrive:

- [ ] Validate actual new adapter outputs against these schemas, replacing the
  temporary projection as the evidence for compatibility.
- [ ] Confirm the shared inputs, Dataset/metadata split, Kolada merge/code convention,
  URL encoding, and language-specific metadata links are handled by the backend.
- [ ] Retain a small representative set of real examples in this repository for
  PXWeb v1, PXWeb v2, and both Kolada data kinds. Keep large exports in ignored `tmp/`.

Done when the consuming code produces valid documents directly and any concrete
contract mismatch is resolved. Do not add hypothetical collision machinery or
force small provider-specific branches into configuration frameworks.

## 2. Define the missing exchange contracts — next work here

- [ ] Define submission of a Dataset/metadata pair, with identity agreement and
  the intended atomic persistence behavior documented.
- [ ] Define the minimum Harvest request, progress/outcome, and terminal-result
  documents needed by the catalog and worker. Reuse the existing resolved input.
- [ ] Agree how repeated submissions are identified so retries do not duplicate
  writes or progress counts, and how failures/cancellation preserve successful results.

Keep these as shared document contracts; route design stays with the catalog API.
Decide fields with the consuming implementations, then add schemas and examples.
Do not create a general workflow engine.

## 3. Verify the complete exchange — across consuming projects

- [ ] Exercise one bounded Harvest through the catalog API: request, execute,
  submit dataset pairs, observe progress, and finish. Initially run one globally.
- [ ] Check failure, cancellation, repeated submission, and restart persistence.
- [ ] Verify application-level identity and dimension/category consistency checks.
- [ ] Exercise retrieval from stored metadata without harvest initialization,
  including PXWeb placeholder normalization and correct observation ordering.

The actual language of text, upstream resource correctness, and cross-document
relationships are not guaranteed by structural JSON Schema validation alone.
Bring demonstrated contract gaps back here; keep provider implementation fixes
in their owning project.

## 4. Prepare and publish 1.0.0 — only when explicitly requested

- [ ] Confirm the intended first-release contracts are exercised by consumers,
  with required behavior and validation limits documented.
- [ ] Run validation and tests; review examples and release notes.
- [ ] Update `VERSION` and all schema `$id` URLs together.
- [ ] Create the public `nordicintel/nordicintel-schemas` repository and enable
  immutable releases before the first publication.
- [ ] Follow the [manual release procedure](../README.md#manual-release), then
  verify every published schema URL and its references.

No release date is committed. The public PxWeb-compatible UI/API does not need
to be completed merely to publish stable contracts for the initial consumers.

## Later, as needed

Recurring scheduling, overlapping Harvests, broader retrieval selection behavior,
and the public PxWeb API 2-compatible interface are application work. Add shared
schemas only where those implementations need them. Package registries, generated
language models, and hosted schema documentation are deferred until useful.

The StatFin archive sample timed out and Kolada OU N01967 had no usable metadata.
Keep those explicit coverage limits; they are not reasons to broaden the schemas
or block unrelated contract work.
