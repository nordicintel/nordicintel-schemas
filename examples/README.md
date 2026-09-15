# Examples

The Dataset set contains exactly three valid documents:

- [minimal-sv](dataset/valid/minimal-sv.json): required identity, title and a single
  time dimension; omission of optional fields is deliberate.
- [detailed-sv](dataset/valid/detailed-sv.json): optional dates/status, attribution,
  roles, elimination, notes, units, themes, contacts, resource links and extensions.
- [detailed-en](dataset/valid/detailed-en.json): the same dataset identity as the
  detailed Swedish document, with its own complete English metadata.

These are small synthetic examples informed by the PXWeb/Kolada source patterns
previously inspected. Codes, agency, contacts and URLs are illustrative, not live
exports or complete real tables. Explicit indexes preserve the shown order.
Unknown official-statistics status is represented as null rather than invented.

Six invalid Dataset documents each demonstrate one error: missing title,
unsupported language, invalid time unit, fractional category position, relative
resource URL, and null elimination boolean. Provider examples retain three useful
valid shapes and ten cases covering its distinct identity/translation/extension,
country, website, optional-null and unknown-field rules.

## Validation layout

`schemas/<name>.schema.json` uses `examples/<name>/valid/*.json` and
`examples/<name>/invalid/*.json`. Files contain instances directly. Each schema
requires both kinds; unmatched example files fail validation.

The normal command checks these files and the schemas' inline examples/defaults.
URI, email, date and date-time format checking is enabled. Inline examples describe
their local field or structure, not necessarily complete datasets.

The sample datasets' identities, dimension/category membership, contiguous
positions, role/elimination references and bilingual identity/order are inspected
during this revision. Those relationships remain consumer responsibilities, not
claims about the structural validator. No live source requests are needed.
