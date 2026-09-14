# Public response examples and known gaps

Fifteen checked-in responses cover table, table-list and metadata forms for the
five real pairs. `tests/public_support.py` is a test-only projection, not a public
API implementation. It uses illustrative catalog.example.org URLs and source
dataset codes; final public routing/identifiers remain API decisions.

The normal test suite compares fixtures with that projection, validates metadata
against the unchanged JSON-stat schema, and checks every exact PxWeb validation
error against `expected-pxweb-gaps.json`. New or changed errors fail the tests.
Upstream schemas are not patched or weakened. Tests require no network access.

## Results

- All five metadata responses pass JSON-stat structural validation.
- Both Kolada samples lack updated: their table/list responses fail that required
  PxWeb field. No date is invented.
- CSN lacks firstPeriod and lastPeriod; these remain absent in table/list responses.
- All three PXWeb samples have real ISO timestamps. The pinned PxWeb updated regex
  rejects them in table/list and metadata responses. It is date-only, additionally
  double-escaped in the upstream YAML; table.updated also declares date-time format.
- A synthetic contact with a name but no raw text demonstrates the stricter PxWeb
  contact requirement. Shared metadata permits it; the upstream check rejects it.
- The two Kolada metadata responses pass the pinned PxWeb metadata schema;
  remaining real response failures are precisely those listed above.

These checks do not establish UI compatibility, completeness for every provider,
code-list endpoint support, source-link correctness, or observation retrieval.
Unknown extension namespaces are preserved; a consumer is not thereby expected
to interpret them. API publication eligibility must address missing required facts.

## Separate implementation audit

All five source pairs were manually/script-audited during this revision: identities,
dimension/category ordering and category labels match the prior examples exactly;
positions are contiguous; category and role references, elimination values, PX maps,
heading/stub references and overlapping basic/PX fields were checked successfully.
This audit is recorded evidence, not an additional semantic validator in the normal
command. The temporary audit script and bulky source exports remain ignored.
