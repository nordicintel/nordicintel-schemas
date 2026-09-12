# Examples

For `schemas/provider.schema.json`, put JSON instances in:

- `examples/provider/valid/*.json`: must pass validation.
- `examples/provider/invalid/*.json`: must fail validation.

Nested schema paths mirror this layout: `schemas/common/code.schema.json`
uses `examples/common/code/valid/` and `examples/common/code/invalid/`.
Each schema requires at least one example of each kind. Store the instance
itself, without an extra wrapper. Unmatched example files fail validation.

The validation command explicitly enforces `format: "uri"`. Other formats
remain annotations. Consumers must likewise enable URI format checking when
validating provider websites; the schema also requires HTTP(S) and a host.

Use synthetic or public information only; never include credentials.
