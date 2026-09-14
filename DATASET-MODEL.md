# Normalized Dataset model

Agreed model specification, 2026-09-14. This replaces the earlier proposals in
this file. Python/Pydantic is the authority; JSON Schema is generated from the
Python classes. The definitions below specify the intended model, not an
installed runtime package. Applications and published schema 1.0.0 are unchanged.

NordicIntel combines statistical discovery and repeatable data retrieval across
providers. Swedish providers are the initial focus; the model supports Swedish
and English. Exact PxWeb UI compatibility does not dictate this model.

## One shared document, two optional language sections

Dataset identity is `{provider_code, dataset_code}`. Provider codes retain their
lowercase underscore-separated pattern; dataset codes are nonblank, opaque and
case-sensitive. The public identifier remains `provider_code:dataset_code`.

There is no language in identity and no separate basic/metadata pair. Store
structural information once, with language-dependent text under
`translations.sv` and/or `translations.en`. At least one complete translation is
required. Both are allowed; neither language silently substitutes for the other.
Swedish is the default when a consumer requests a default language, not a reason
to fabricate Swedish text or reject an otherwise complete English document.

| Shared Dataset field | Required | Definition |
|---|---|---|
| `identity` | Yes | Provider and dataset codes |
| `dimensions` | Yes | Nonempty ordered Dimension array |
| `translations` | Yes | Nonempty object with only `sv` and/or `en` entries |
| `official_statistics` | No | Boolean or None; unknown is valid |
| `updated`, `next_release` | No | Source date or timezone-aware timestamp |
| `time_unit` | No | `annual`, `semiannual`, `quarterly`, `monthly`, `weekly`, `daily`, `other` |
| `first_period`, `last_period` | No | Original period notation as nonblank strings |
| `discontinued` | No | Boolean; no invented default |
| `subject` | No | `{code}` for the primary subject |
| `paths` | No | Ordered thematic chains, each an ordered nonempty array of node codes |
| `contacts` | No | Defined Contact array, using canonical source contact details |
| `links` | No | Named language-independent links |

Optional attributes accept None in Python and null on input; normal JSON export
omits None fields with `model_dump(mode="json", exclude_none=True)`. None does
not become false, zero or an invented date. Nonblank descriptive strings and
identity values are required where supplied. Unknown object fields are rejected.
Empty optional lists are allowed; optional empty containers can be omitted by
construction helpers. These are model rules, not database publication rules.

### Dimensions, categories and translations

A Dimension contains required `code` and nonempty ordered `categories`, and
optional `role`, `elimination`, `elimination_value`. Role is one of `time`, `geo`,
`metric`, or None. Elimination is an optional source boolean; an elimination
value references an existing category code.

A Category contains `code`. Array position is its order. There is no index map,
repeated label, unit object, geographic object or category hierarchy in shared
structure. Future normalized period attributes can be added to Category without
replacing the source code or introducing generic extensions.

| Translation field | Definition |
|---|---|
| `label` | Required original dataset title |
| `dimensions` | Required dimension-text mapping keyed by shared dimension code |
| `description`, `source` | Optional descriptive/attribution text |
| `subject` | Optional primary subject label; may exist without a source subject code |
| `paths` | Optional nested label arrays matching shared path/node positions |
| `notes` | Optional ordered string list |
| `links` | Optional named language-specific links |

DimensionText contains required `label` and `categories` keyed by category code,
plus optional `notes`. CategoryText contains required original `label`, optional
`unit` text and optional `notes`. Use the original category label, not PX
alternative text. Unit text such as `antal`/`number` belongs in its translation;
precision, symbols and unit-position hints are excluded.

Every included translation covers all dimensions/categories. Shared path chains
store codes once; when translated paths are supplied, their outer length and
each chain length match the shared paths. Text maps use codes to address shared
objects; their dictionary iteration order does not establish statistical order.

Contact fields are `name`, `organization`, `email`, `phone`; at least one must be
populated. Keep canonical source details once, preferring the Swedish source
record when combining these examples. No raw contact string or contact-language
merge framework is part of the model.

### Links and retrieval

Links has exactly four optional names: `source`, `documentation`, `metadata`,
`data`. Each Link is `{href: <absolute HTTP(S) URL>}`. There is no rel array,
media-type field, language field, opaque classification URI or generic related
link list. A source identifier such as `infofile` is not a URL.

Keep known language-independent targets in shared `links`. A language-specific
target belongs in that translation's `links`; it overrides the shared target
for that same name. Do not copy the same target into both locations. Named
resources need not all be present. Links retain actual upstream targets, not
invented NordicIntel endpoints.

Retrieval configuration stays outside Dataset. A private binding preserves the
implementation identifier and configuration needed to execute requests, including
language-specific native addressing where needed. A data href is not a complete
POST request definition. See the separate binding examples linked below.

## Kolada's one shared mapping

Use one separate supporting resource with this shape:

```json
{
  "municipalities": {"1463": "Mark"},
  "ou_municipality": {"V11E100171": "1463"}
}
```

Production construction reads Kolada's existing `/municipality` and `/ou`
resources: municipality id/title and OU id/municipality respectively. The
current `KoladaClient.list_municipalities`, `KoladaOrganizationalUnitsClient.list_ous`
and `parse_ou` already expose those values. The existing
`build_ou_municipality_extension` is the point that currently duplicates them.

Keep this resource outside Dataset, with municipality labels once and one
OU-to-municipality code mapping. Dataset categories keep their own codes and
translated labels. No general code-list framework, PX code-list references,
per-category municipality object or mapping-conflict machinery is introduced.
The local mapping example contains the saved OU example's subset, not a claim
to have exported the complete provider resource.

## Exclusions and normalization

Excluded: contents; alternative labels; measuring/price type, adjustment,
reference/base period qualifiers; all precision and aggregation permission;
mandatory-note flags; raw contacts; child/coordinates; presentation hints;
general code lists; extension containers; remaining Kolada-specific flags,
classification extras, publication-calendar details and raw provenance.

Keep existing subject/group thematic paths and the common source description,
status and coverage. Do not reinterpret Kolada publication-calendar dates as
updated or coverage. Exact field moves/discards are recorded alongside the
[complete examples](docs/model-examples/README.md), not as a corpus audit here.

Adapters own provider-response parsing, text/code cleanup and native request
addressing. Model helpers normalize accepted enum spellings and construct the
shared/translated shape; they do not fetch resources or guess translations.
Do not infer an architecture from raw trailing-space/comma differences. Code
cleanup must preserve working native data selection; the public model does not
contain a new adapter-specific mapping bag for such cleanup.

## Python class definitions and validation

The following executable class specification is the intended public shape.
There is no separate hand-maintained JSON Schema authority. The production
package will generate its structural schema with `Dataset.model_json_schema()`.

Structural validation covers fields, types, nonblank strings, booleans, dates,
URLs and enums. Python semantic validation also checks unique codes, valid
elimination references, complete translations and corresponding thematic paths.
Actual text language cannot be proven by either structural schema or these
semantic checks; Harvest is responsible for returning the requested language.

```python
from datetime import date, datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

Text = Annotated[str, Field(strict=True, pattern=r"\S")]
Language = Literal["sv", "en"]
TimeUnit = Literal["annual", "semiannual", "quarterly", "monthly", "weekly", "daily", "other"]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Identity(Model):
    provider_code: Annotated[str, Field(strict=True, pattern=r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")]
    dataset_code: Text


class Link(Model):
    href: Text

    @model_validator(mode="after")
    def absolute_resource(self):
        parsed = urlsplit(self.href)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or any(c.isspace() for c in self.href):
            raise ValueError("href must be an absolute HTTP(S) resource URL")
        return self


class Links(Model):
    source: Link | None = None
    documentation: Link | None = None
    metadata: Link | None = None
    data: Link | None = None


class Contact(Model):
    name: Text | None = None
    organization: Text | None = None
    email: Text | None = None
    phone: Text | None = None

    @model_validator(mode="after")
    def populated(self):
        if not any(getattr(self, k) is not None for k in type(self).model_fields):
            raise ValueError("contact requires at least one populated field")
        return self


class Category(Model):
    code: Text


class Dimension(Model):
    code: Text
    categories: Annotated[list[Category], Field(min_length=1)]
    role: Literal["time", "geo", "metric"] | None = None
    elimination: Annotated[bool, Field(strict=True)] | None = None
    elimination_value: Text | None = None


class CategoryText(Model):
    label: Text
    unit: Text | None = None
    notes: list[Text] | None = None


class DimensionText(Model):
    label: Text
    categories: dict[Text, CategoryText]
    notes: list[Text] | None = None


class Translation(Model):
    label: Text
    dimensions: dict[Text, DimensionText]
    description: Text | None = None
    source: Text | None = None
    subject: Text | None = None
    paths: list[Annotated[list[Text], Field(min_length=1)]] | None = None
    notes: list[Text] | None = None
    links: Links | None = None


class Subject(Model):
    code: Text


class Dataset(Model):
    identity: Identity
    dimensions: Annotated[list[Dimension], Field(min_length=1)]
    translations: Annotated[dict[Language, Translation], Field(min_length=1)]
    official_statistics: Annotated[bool, Field(strict=True)] | None = None
    updated: date | AwareDatetime | None = None
    next_release: date | AwareDatetime | None = None
    time_unit: TimeUnit | None = None
    first_period: Text | None = None
    last_period: Text | None = None
    discontinued: Annotated[bool, Field(strict=True)] | None = None
    subject: Subject | None = None
    paths: list[Annotated[list[Text], Field(min_length=1)]] | None = None
    contacts: list[Contact] | None = None
    links: Links | None = None

    @field_validator("updated", "next_release", mode="before")
    @classmethod
    def source_date(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                if len(value) == 10:
                    return date.fromisoformat(value)
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("expected a date or timezone-aware timestamp") from exc
        if isinstance(value, datetime):
            if value.utcoffset() is None:
                raise ValueError("timestamps require a timezone")
        elif not isinstance(value, date):
            raise ValueError("expected a date or timezone-aware timestamp")
        return value

    @model_validator(mode="after")
    def consistent_references(self):
        dimensions = {d.code: d for d in self.dimensions}
        if len(dimensions) != len(self.dimensions):
            raise ValueError("dimension codes must be unique")
        for dimension in self.dimensions:
            codes = {c.code for c in dimension.categories}
            if len(codes) != len(dimension.categories):
                raise ValueError("category codes must be unique within their dimension")
            if dimension.elimination_value is not None and dimension.elimination_value not in codes:
                raise ValueError("elimination_value must reference an existing category")
        for translation in self.translations.values():
            if set(translation.dimensions) != set(dimensions):
                raise ValueError("each included translation must cover every dimension")
            for code, text in translation.dimensions.items():
                if set(text.categories) != {c.code for c in dimensions[code].categories}:
                    raise ValueError("each included translation must cover every category")
            if translation.paths is not None:
                if self.paths is None or [len(p) for p in translation.paths] != [len(p) for p in self.paths]:
                    raise ValueError("translated path labels must correspond to shared path nodes")
        return self
```

No provider HTTP parser, SQL, job control or mutable application state belongs
in these classes. Future shared helpers may construct and validate these types;
they must return clear validation errors rather than silently invent values.

## Examples and next implementation

[Complete proposed documents and their transformation notes](docs/model-examples/README.md)
cover PXWeb v1, bilingual PXWeb v2, Kolada municipality and Kolada OU. They are
design fixtures, not claimed new-format exports from the running adapters.

The [implementation handoff](DATASET-MODEL-HANDOFF.md) defines the next code work.
No applications, generated contract collection, package publication, database
publication rules or deployment are changed by this specification. Existing
development documents can be discarded when application adoption is undertaken;
there is no preservation migration project here.
