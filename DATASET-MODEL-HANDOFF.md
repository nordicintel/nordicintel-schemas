# Implement the normalized Dataset model

Use [DATASET-MODEL.md](DATASET-MODEL.md) as the approved specification and
[docs/model-examples](docs/model-examples/README.md) as complete design fixtures.
Do not reopen the rejected fields or introduce adapter-specific Dataset objects.

## First code task: model package

Implement the Python model in this repository, on `public-contract-direction`,
using a `nordicintel_schemas` import package with public Dataset and nested types.
Keep the repository name. Use Python 3.12, Pydantic 2 and uv-locked development
dependencies. This import/package placement is an implementation default; no
registry publication or new repository is needed to implement or test the model.

Translate the executable class specification into maintained code. Keep one
validation path for construction, parsing and serialization. Export optional None
values as omitted JSON fields. Expose generated JSON Schema through
`Dataset.model_json_schema()`; do not maintain a second manual Dataset schema.

Keep the interface small: validated construction, JSON parsing/export, schema
generation and shared normalization helpers. Provider HTTP parsing, native
request addressing, database writes and Harvest controls are outside this package.
Do not add a generic plugin system, translation service or code-list framework.

No new version/tag is assigned by this handoff. Existing 1.0.0 consumers keep
using that release. Generate development schema output locally; replacing the
unpublished collection and publishing a package/release is a subsequent explicit
task, not an automatic side effect of implementing the Python classes.

## Construction and language behavior

- Build shared identity, ordered dimensions/categories and other structural
  fields once. Translation objects contain only the specified text and localized
  resource links. Preserve source codes and original labels.
- Adapters perform source-specific code/text cleanup. Do not design separate
  language datasets around raw whitespace/punctuation differences. If cleaned
  codes differ from native request codes, retrieval must still address the source
  correctly; keep native addressing outside Dataset.
- A Dataset contains at least one complete sv/en translation. Construction fails
  clearly for missing dimension/category text in an included translation; it does
  not fabricate text or silently switch languages.
- Shared helper code accepts already resolved shared structure plus translated
  content. It does not decide which independently harvested source revision wins
  or implement a database patch protocol. Whole-document construction/validation
  is the initial interface; revision reconciliation belongs to later Harvest
  orchestration work.
- Keep common resource links once. Localized links override the same named shared
  resource when resolving a language view. Do not expose relation arrays or turn
  lookup IDs into hrefs.
- Store canonical contacts once, retaining name, organization, email and phone.
  No raw contacts, mandatory-note flags or translated contact machinery.
- Keep the one Kolada OU/municipality mapping outside Dataset. Its producer uses
  existing provider resources directly. There is no general code-list subsystem.

## Maintained tests and acceptance

Turn the four complete Dataset examples into package fixtures. Validate both
Pydantic construction and generated JSON Schema, without requiring upstream HTTP
or a database. Keep the private retrieval and Kolada mapping samples separate.

Test required identity/labels, provider-code pattern, sv/en restriction, all seven
time units, nullable optional fields, original labels, named hrefs, date versus
timezone-aware timestamp, valid contacts, ordered arrays and one role per
dimension. Reject every removed field at its former and proposed location.

Semantic tests must reject duplicate dimension/category codes, unknown
elimination references, missing/unknown translation references and mismatched
thematic label chains. Verify a complete English-only document is allowed and
that missing Swedish text never silently falls back to English.

Retain meaningful source-to-model checks: category ordering, unit text, notes,
attribution and official status. Test shared structure once with two translations,
and check that removed qualifiers/precision/raw extras do not reappear. Exercise
language-independent versus localized links and round-trip export without None.

Extend the existing read-only CI with package installation, model tests and
generated-schema consistency. Keep existing collection tests until replacement
of the unpublished collection is explicitly undertaken. No automatic publication.

Done for this first task means installable local models, maintained tests,
generated-schema output and concise usage documentation. Commit on the working
branch; no application changes, main merge, push, tag or publication are implied.

## Following application work — separately authorized

1. **Harvest:** use the model package, assemble combined translations, preserve
   native retrieval bindings separately, and produce the shared Kolada mapping
   from `/ou` and `/municipality`. Update relevant adapter regression tests.
2. **Catalog:** accept/store the combined document and expose language-specific
   views without retaining separate full structural copies per language. Define
   its submission/replacement interface with Harvest. Existing development
   documents can be discarded; no preservation migration is required.
3. **Integration:** verify a harvest constructs a Dataset, validates it, stores it
   through the catalog and reads back its shared structure and both translations.
   Separately verify retrieval can still use the retained native addressing.

Database publication rules, control-plane migration, observation retrieval
implementation, public PxWeb endpoints and deployment are not part of the model
package task. Do not invent those policies to complete model validation.
