# Examples

For `schemas/provider.schema.json`, put JSON instances in:

- `examples/provider/valid/*.json`: must pass validation.
- `examples/provider/invalid/*.json`: must fail validation.

Nested schema paths mirror this layout: `schemas/common/code.schema.json`
uses `examples/common/code/valid/` and `examples/common/code/invalid/`.
Each schema requires at least one example of each kind. Store the instance
itself, without an extra wrapper. Unmatched example files fail validation.

The validation command explicitly enforces `uri`, `date`, and `date-time` formats. Other formats
remain annotations. Consumers must likewise enable URI format checking when
validating provider websites; the schema also requires HTTP(S) and a host.

Use synthetic or public information only; never include credentials.

## Real dataset pairs

Matching `real-*.json` filenames in `dataset/valid` and `dataset-metadata/valid`
are five complete projected pairs from the public-source harvest of 2026-09-12.
They are saved examples, not direct exports from adapters adopting these contracts.
The smallest saved metadata sample for each case was selected; categories and
ordering were not trimmed. Pair identities, dimension membership, contiguous
category positions, and category/role references were checked before inclusion.
The regular validator checks their JSON Schema structure.

Projection splits basic/detail fields, renames path-node `id` to `code`, places
extra fields in `extension`, percent-encodes source URLs where needed, and uses
advertised language-specific PXWeb v2 metadata links. Kolada OU is represented
under provider `kolada` with the `_OU` dataset-code suffix. These examples do not
prove upstream link correctness, semantic language correctness, or API integration.
The SSB source-page URL is retained from the audit despite a suspicious repeated
path; syntax validation does not establish that it is the correct landing page.

The source manifest records `7f56bbf`; the run included the then-uncommitted
PXWeb fix subsequently reported as backend commit `56bc1df`. Local raw files and
the full audit remain ignored in `tmp/`. Source hashes below identify those files.

- `real-pxweb-v1-csn-sv.json`: `ABAKD12.px`, source `tmp/live-harvest/20260912T031124Z/pxweb/csn/sv/02-metadata.json`; SHA-256 `f7494f90772ddacc4a73d57a35dc5427f848c108d8d6af816e9c6d901cf0b7cb`. URL changes: none.
- `real-pxweb-v2-scb-sv.json`: `TAB4723`, source `tmp/live-harvest/20260912T031124Z/scb/sv/04-metadata.json`; SHA-256 `a4ae881556e7bc039168e120da72f9639240a82e2cd7908f42cf03c2d68f55c7`. URL changes: metadata_url.
- `real-pxweb-v2-ssb-en.json`: `13618`, source `tmp/live-harvest/20260912T031124Z/ssb/en/03-metadata.json`; SHA-256 `1ffbe9b2bee273047bad126d8da5d4e6c1f8cd9fa7f90b9d1b9fbacb45152df5`. URL changes: metadata_url.
- `real-kolada-municipality-sv.json`: `N00009`, source `tmp/live-harvest/20260912T031124Z/kolada/sv/03-metadata.json`; SHA-256 `d1188f3000fafdf6d79c0c34eb67e3dcf8b94e9ea75623ee1343cce509e0ac5c`. URL changes: none.
- `real-kolada-ou-sv.json`: `N11042_OU`, source `tmp/live-harvest/20260912T031124Z/kolada_ou/sv/05-metadata.json`; SHA-256 `31a23a4ace7c209df7601294f5170b4fb71910e55c3923dcd204638097387704`. URL changes: none.

## 2.0.0 revision

The five pairs above were migrated without changing identities, dimension order,
category index maps or category labels. Source/subject/paths moved to basic info;
contact and official-statistics moved to PX extensions; unit base and path sortCode
became explicit fields. Loose extras are preserved under named upstream objects.
Existing PX/Kolada objects remain, and source URLs were not rewritten in this revision.

New synthetic cases cover the documented optional PX fields, enum/type errors,
named-object extensibility and open retrieval envelopes. Former adapter-setting
restrictions are now valid retrieval examples; implementation validation is separate.
Removed provider Harvest configuration is represented by invalid examples.

Public projections live outside this structural example layout under tests/public;
see their [results and limitations](../tests/public/README.md).
