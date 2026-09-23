<!-- markdownlint-disable-file MD013 MD033 -->

# Dataset metadata property reference

Generated from [`schemas/dataset-metadata.schema.json`](../schemas/dataset-metadata.schema.json); do not edit by hand.

`required` means required within the containing object, not necessarily at the root. Conditional requirements are noted in descriptions; consult the schema for full constraints.

`jstat` marks standard JSON-stat2 fields; `nordicintel` marks fields inside the NordicIntel namespace and custom namespace conventions (including nested objects). Provider/adapter namespace contents are open and have no fixed property inventory.

Paths are relative to each section; `{key}` is a dynamic map key and `[]` an array item. Shared objects are documented once. Primitive map entries, unused definitions and arbitrary additional properties are omitted. Examples come only from schema annotations.

<a id="section-0"></a>

## Dataset

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `version` | jstat | true | string | Fixed value: "2.0". | <code>[]</code> |
| `class` | jstat | true | string | Fixed value: "dataset". | <code>[]</code> |
| `label` | jstat | true | string | Human-readable dataset name/title, as given by the provider. | <code>["Befolkning efter region och år"]</code> |
| `source` | jstat | false | string | Dataset attribution as reported by the provider; it may name another originating organization. Omit when unknown. The provider identity is extension.nordicintel.provider_code. | <code>["Statistiska centralbyrån"]</code> |
| `updated` | jstat | false | string | Valid calendar date in YYYY-MM-DD form, within the published JSON-stat2 schema's 1900–2099 range. Extract the provider's calendar date without timezone conversion. Omit when unknown; preserve useful original text as updated_original in the provider or adapter namespace. | <code>["2026-09-15"]</code> |
| `note` | jstat | false | array&lt;string&gt; | Dataset-level explanatory notes in the document language; omit when unavailable. | <code>[]</code> |
| `href` | jstat | false | string | Provider's human-readable page for this Dataset. | <code>[]</code> |
| `link` | jstat | false | object | JSON-stat2 relation map. Use describedby for documentation and metadata, related for data and other supporting resources. Other relation names accepted by the published JSON-stat2 schema are also supported. Avoid duplicate resources. | <code>[]</code> |
| `link.{key}[]` | jstat | false | object | JSON-stat2 resource link. Use label and known type to describe the target; custom descriptions and category references belong in extension.nordicintel. Provider or adapter extras use their own namespaces. See [properties](#section-1). | <code>[]</code> |
| `id` | jstat | true | array&lt;string&gt; | Complete ordered dimension codes. Consumers check exact correspondence with dimension keys. This is dimension ordering, not a Dataset identifier. | <code>[["Region", "Time"]]</code> |
| `size` | jstat | true | array&lt;integer&gt; | Actual category counts in id order, even though value is empty. Consumers check correspondence with each dimension's categories. | <code>[[2, 2]]</code> |
| `role` | jstat | false | object | Semantic roles assigned to existing dimension codes. Each supplied array is nonempty and unique; array order need not follow dimension order. Applications enforce at most one role per dimension. | <code>[{"time": ["Time"], "geo": ["Region"]}]</code> |
| `role.time` | jstat | false | array&lt;string&gt; | Existing dimension codes assigned the time role; references and cross-role uniqueness are application checks. | <code>[]</code> |
| `role.geo` | jstat | false | array&lt;string&gt; | Existing dimension codes assigned the geo role; references and cross-role uniqueness are application checks. | <code>[]</code> |
| `role.metric` | jstat | false | array&lt;string&gt; | Existing dimension codes assigned the metric role; references and cross-role uniqueness are application checks. | <code>[]</code> |
| `dimension` | jstat | true | object | Complete JSON-stat2 dimension metadata keyed by provider dimension code; id supplies order. | <code>[]</code> |
| `dimension.{key}` | jstat | false | object | JSON-stat2 dimension with complete categories. Custom shared metadata belongs in extension.nordicintel; provider or adapter extras belong in sibling namespaces. See [properties](#section-2). | <code>[]</code> |
| `value` | jstat | true | array | Always an empty array for metadata-only output. This field is required; size still describes the full category structure. | <code>[[]]</code> |
| `extension` | jstat | true | object | Namespaced extensions. nordicintel holds shared fields; other keys are provider_code or adapter_type namespaces with open object contents. Never place unnamespaced custom fields here. Defined namespace fields retain their constraints. See [properties](#section-3). | <code>[]</code> |

<a id="section-1"></a>

## resource

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `href` | jstat | true | string | Absolute HTTP(S) resource URL. Resolve relative provider URLs against their original page or endpoint. | <code>[]</code> |
| `label` | jstat | true | string | At least one non-whitespace character; validation does not trim or normalize text. | <code>[]</code> |
| `type` | jstat | false | string | Known resource media type; omit when unknown. | <code>[]</code> |
| `note` | jstat | false | array&lt;string&gt; | Nonempty array of distinct nonblank strings, used for JSON-stat2 notes and dimension roles. | <code>[]</code> |
| `extension` | jstat | false | object | Namespaced extensions. nordicintel holds shared fields; other keys are provider_code or adapter_type namespaces with open object contents. Never place unnamespaced custom fields here. Defined namespace fields retain their constraints. See [properties](#section-4). | <code>[]</code> |

<a id="section-2"></a>

## jstat_dimension

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `label` | jstat | false | string | Provider's dimension label in this document language; omit if unavailable. | <code>[]</code> |
| `category` | jstat | true | object | JSON-stat2 categories. Supply an index, or a single category label when the dimension has exactly one category. Labels are optional when an index is supplied. Conditional required groups: [["index"], ["label"]]. See [properties](#section-5). | <code>[]</code> |
| `note` | jstat | false | array&lt;string&gt; | Nonempty array of distinct nonblank strings, used for JSON-stat2 notes and dimension roles. | <code>[]</code> |
| `href` | jstat | false | string | Absolute HTTP(S) resource URL. Resolve relative provider URLs against their original page or endpoint. | <code>[]</code> |
| `link` | jstat | false | object | JSON-stat2 relation map. Use describedby for documentation and metadata, related for data and other supporting resources. Other relation names accepted by the published JSON-stat2 schema are also supported. Avoid duplicate resources. | <code>[]</code> |
| `link.{key}[]` | jstat | false | object | JSON-stat2 resource link. Use label and known type to describe the target; custom descriptions and category references belong in extension.nordicintel. Provider or adapter extras use their own namespaces. See [properties](#section-1). | <code>[]</code> |
| `extension` | jstat | false | object | Namespaced extensions. nordicintel holds shared fields; other keys are provider_code or adapter_type namespaces with open object contents. Never place unnamespaced custom fields here. Defined namespace fields retain their constraints. See [properties](#section-6). | <code>[]</code> |

<a id="section-3"></a>

## dataset_extension

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `nordicintel` | nordicintel | true | object | Open namespace object: additional properties may contain any JSON value, including null, arrays and nested objects. Use existing JSON-stat2 or NordicIntel fields whenever their meaning fits; do not duplicate or alias them. Additional properties allowed. See [properties](#section-7). | <code>[]</code> |

<a id="section-4"></a>

## resource_extension

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `nordicintel` | nordicintel | false | object | Open namespace object: additional properties may contain any JSON value, including null, arrays and nested objects. Use existing JSON-stat2 or NordicIntel fields whenever their meaning fits; do not duplicate or alias them. Additional properties allowed. See [properties](#section-8). | <code>[]</code> |

<a id="section-5"></a>

## jstat_category

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `index` | jstat | false | array&lt;string&gt; / object | Category ordering as an ordered code array or a code-to-position object. | <code>[["00", "01"], {"00": 0, "01": 1}]</code> |
| `label` | jstat | false | object | Provider labels keyed by existing category code. Omit unavailable labels; do not invent translations. With no index, exactly one category label identifies the sole category. | <code>[{"00": "Riket", "01": "Stockholms län"}]</code> |
| `note` | jstat | false | object | Category code to ordered notes; each key must reference an existing category. | <code>[]</code> |
| `unit` | jstat | false | object | Units by existing category code, commonly on a metric dimension. Omit unknown units. | <code>[]</code> |
| `unit.{key}.label` | jstat | false | string | Provider's unit label in the document language. | <code>[]</code> |
| `unit.{key}.decimals` | jstat | false | integer | Nonnegative decimal places for display; not a statement of measurement accuracy. | <code>[]</code> |
| `unit.{key}.position` | jstat | false | string | Placement of the unit symbol relative to the value: start or end. Allowed: ["start", "end"]. | <code>[]</code> |
| `unit.{key}.symbol` | jstat | false | string | Unit symbol, such as %, EUR or kr. | <code>[]</code> |
| `child` | jstat | false | object | Category hierarchy: parent category code to its immediate child category codes. All codes refer to categories in this dimension. | <code>[]</code> |
| `coordinates` | jstat | false | object | Geographic category code to [longitude, latitude]. | <code>[]</code> |

<a id="section-6"></a>

## dimension_extension

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `nordicintel` | nordicintel | false | object | Open namespace object: additional properties may contain any JSON value, including null, arrays and nested objects. Use existing JSON-stat2 or NordicIntel fields whenever their meaning fits; do not duplicate or alias them. Additional properties allowed. See [properties](#section-9). | <code>[]</code> |
| `{key}.categories` | nordicintel | false | object | Additional metadata keyed by category code in the enclosing dimension. Each value is an open object; codes must identify existing categories. Standard category labels, notes, units, hierarchies and coordinates stay in category. | <code>[]</code> |

<a id="section-7"></a>

## nordicintel_dataset

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `provider_code` | nordicintel | true | string | Stable provider code, e.g. scb. | <code>["scb", "kolada"]</code> |
| `dataset_code` | nordicintel | true | string | Opaque, case-sensitive provider dataset code, unique within its provider and shared across language versions. Do not slugify. | <code>["TAB335", "ABAKD12.px", "N11730_OU"]</code> |
| `language` | nordicintel | true | string | Language of this metadata document; no silent language fallback. Allowed: ["sv", "en"]. | <code>["sv", "en"]</code> |
| `description` | nordicintel | false | string / null | Longer free-text description of the dataset. | <code>["Folkmängd vid årets slut."]</code> |
| `discontinued` | nordicintel | false | boolean / null | Whether publication or updates for this Dataset have stopped. False means explicitly active; omission or null means unknown. | <code>[true, false, null]</code> |
| `official_statistics` | nordicintel | false | boolean / null | Provider-reported official national statistics status. Preserve true, false and unknown (omitted or null); never infer it solely from provider identity. | <code>[true, false, null]</code> |
| `time_unit` | nordicintel | false | string / null | Granularity of statistical time periods, not publication frequency. Use other for a known granularity outside the enum; omit or use null when unknown. Allowed: ["annual", "semiannual", "quarterly", "monthly", "weekly", "daily", "other", null]. | <code>["annual", "quarterly", "other", null]</code> |
| `first_period` | nordicintel | false | string / null | First period covered by the Dataset, either reported by the Provider or inferred by a local implementation; not necessarily a category label. Preserve the Provider's original form instead of standardizing it. | <code>["2020", "2020K1", null]</code> |
| `last_period` | nordicintel | false | string / null | Last period covered by the Dataset, either reported by the Provider or inferred by a local implementation; not necessarily a category label. Preserve the Provider's original form instead of standardizing it. | <code>["2025", "2025K4", null]</code> |
| `next_release` | nordicintel | false | string / null | Date/datetime of the next expected release of the dataset, as announced by the provider. | <code>["2027-02-20", null]</code> |
| `subject` | nordicintel | false | object | Primary thematic classification with code, localized label or both. Omit when unavailable; null and empty objects are not accepted. Conditional required groups: [["code"], ["label"]]. | <code>[{"code": "BE", "label": "Befolkning"}]</code> |
| `subject.code` | nordicintel | false | string | Original subject code. | <code>[]</code> |
| `subject.label` | nordicintel | false | string | Subject name in this document language. | <code>[]</code> |
| `paths` | nordicintel | false | array&lt;array&lt;object&gt;&gt; / null | Ordered thematic chains from broader to narrower nodes. Multiple chains describe multiple thematic memberships, never API routes or dataset lookup keys. | <code>[[[{"id": "population", "label": "Befolkning"}, {"id": "count", "label": "Folkmängd"}]]]</code> |
| `paths[][]` | nordicintel | false | object | One thematic node identified by the provider's thematic node code and localized label, with an optional supporting URL. See [properties](#section-10). | <code>[]</code> |
| `contacts` | nordicintel | false | array&lt;object&gt; / null | Provider-reported contacts. Populate the named attributes whenever the supplied information can be parsed or mapped to them. Additional properties are ONLY for information that cannot be represented by those attributes. | <code>[[{"organization": "Statistikmyndigheten", "email": "statistics@example.org"}]]</code> |
| `contacts[]` | nordicintel | false | object | Provider-reported contact. Additional properties are ONLY for information that cannot be parsed or mapped into name, email, phone, organization, address or url. Do not use alternate keys or raw copies to bypass or duplicate these attributes. At least one property must be supplied. Additional properties allowed. See [properties](#section-11). | <code>[]</code> |

<a id="section-8"></a>

## nordicintel_resource

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `description` | nordicintel | false | string | Optional explanation of the resource or its use. | <code>[]</code> |
| `category_id` | nordicintel | false | string | Existing category code in the enclosing dimension. Only use on links belonging to a dimension; omit for whole-dimension resources. Dataset links concern the whole Dataset. | <code>[]</code> |

<a id="section-9"></a>

## nordicintel_dimension

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `elimination` | nordicintel | false | boolean | Whether this dimension may be omitted from a data selection. Construction default is false. True does not require an elimination_value; validation inserts neither default. | <code>[false, true]</code> |
| `elimination_value` | nordicintel | false | string / null | Optional category code to use when this dimension is omitted. Null when unspecified. A supplied code must identify a category in this dimension, including a sole category identified by its label map; consumers check this relationship. | <code>[null, "00"]</code> |
| `source` | nordicintel | false | string | Attribution for this dimension as reported by the provider, which may name a different originating organization. | <code>[]</code> |
| `updated` | nordicintel | false | string / null | Provider-reported dimension update text, preserving provider precision and formatting. A consumer must be able to extract a calendar date. Omit or use null when unknown. | <code>["2026-09-15", "2026-09-15T09:00:00", "2026-09-15 09:00:00", null]</code> |
| `categories` | nordicintel | false | object | Additional metadata keyed by category code in the enclosing dimension. Each value is an open object; codes must identify existing categories. Standard category labels, notes, units, hierarchies and coordinates stay in category. | <code>[]</code> |

<a id="section-10"></a>

## path_node

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `id` | nordicintel | true | string | Original thematic node identifier, not a dataset access key. | <code>[]</code> |
| `label` | nordicintel | true | string | Thematic node label in the document language. | <code>[]</code> |
| `url` | nordicintel | false | string | Optional classification or documentation URL for this thematic node. | <code>[]</code> |

<a id="section-11"></a>

## contact

| Property | Source | Required | Type | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `name` | nordicintel | false | string | Contact person or team name. | <code>[]</code> |
| `email` | nordicintel | false | string | Email address, not a mailto URL; enable email format checking. | <code>[]</code> |
| `phone` | nordicintel | false | string | Telephone number as text, preserving prefixes and extensions. | <code>[]</code> |
| `organization` | nordicintel | false | string | Organization responsible for this contact. | <code>[]</code> |
| `address` | nordicintel | false | string | Postal or visiting address as provider text. | <code>[]</code> |
| `url` | nordicintel | false | string | Contact page URL. | <code>[]</code> |
