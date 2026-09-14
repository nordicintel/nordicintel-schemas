# PxWeb2 UI requirements for the catalog API

Investigated 2026-09-14 against upstream [PxTools/PxWeb2 commit
6c46c20d5ed8547c009ec255532c64ca884e762e](https://github.com/PxTools/PxWeb2/tree/6c46c20d5ed8547c009ec255532c64ca884e762e).
This is a source-code trace, not a browser acceptance test. The upstream checkout
is kept only in ignored `tmp/`. No application or shared schema was changed.

## Conclusion

The existing UI can browse a metadata catalog, but its table viewer expects data
retrieval immediately. Our decision to return 501 for data, codelists and saved
queries is valid API behavior; it does **not** create a working metadata-only UI
without a small UI adaptation. Keep the stubs and explicitly disable unavailable
UI actions and automatic data fetching, with an explanatory presentation panel.
Do not simulate successful observation responses.

## Actual HTTP interactions

All paths below are relative to the configured API base, proposed as `/api/v2`.

| Interaction | Actual request | Consequence for our implementation |
|---|---|---|
| Open catalog or switch language | `GET /tables?lang=sv&includeDiscontinued=true&pageNumber=1&pageSize=10000` | Return the requested page and honor language/status parameters. The UI does not fetch later pages. |
| Search | Same endpoint with `query` | Implement useful basic text matching; ignoring `query` breaks search. Most other filtering and sorting happens locally. |
| Open table | `GET /tables/{id}?lang=sv` and `GET /tables/{id}/metadata?lang=sv&defaultSelection=true` | Both responses must work together. |
| Initialize selected categories | `GET /tables/{id}/defaultselection?lang=sv` | Required by the current selection UI; not a 501 candidate. |
| Open viewer/change selections | `POST /tables/{id}/data?lang=sv&outputFormat=json-stat2` | Automatic, not only a deliberate download action. Our 501 requires UI handling. |
| Choose an advertised codelist | Metadata endpoint with `codelist[dimensionCode]=listId` | Stubbing only `/codelists/{id}` does not cover this behavior. |
| Save/reopen query | `POST /savedqueries`, `GET /savedqueries/{id}`, `/savedqueries/{id}/selection`, `/savedqueries/{id}/data` | Include the selection route in the stubs. Disable save/reopen actions for initial UI use. |
| API configuration | No application call found | Generated `/config` client exists, but the app reads a local configuration file. |

Evidence: [listing/search implementation](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/util/tableHandler.ts#L34-L103),
[selection initialization and codelists](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/components/Selection/Selection.tsx#L267-L465),
[saved-query client](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2-api-client/src/services/SavedQueriesService.ts),
[application startup](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/main.tsx#L17-L21).

The 10,000-row request is a concrete integration constraint: a smaller server cap
silently gives this UI an incomplete catalog. Initially honor the request; if the
eligible corpus exceeds 10,000, add actual paging to the UI. This does not require
a search engine. The client's exposed `pastDays` parameter is not supplied by the
traced application listing/search calls.

## Why 501 needs UI work

`Presentation` initiates a data fetch on its first run and after appropriate
selection changes. Matrix-size checking starts enabled. The provider posts the
selection, catches an API error, stores its message, then throws that message
from an effect. The enclosing error boundary replaces its children with a
generic error view. There is no special 501 handling in this path.

Evidence: [automatic fetching](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/components/Presentation/Presentation.tsx#L230-L290),
[fetch failure](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/context/TableDataProvider.tsx#L1175-L1197),
[error effect](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/context/TableDataProvider.tsx#L139-L147),
[error boundary](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/components/ErrorBoundary/ErrorBoundary.tsx#L27-L51).

Return `application/problem+json` with `status`, `title` and `type` (and a useful
`detail`), rather than FastAPI's default detail-only response. The UI's error
formatter reads those first three fields. Its client recognizes both JSON and
problem JSON content types.
[Formatter](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/util/problemMessage.ts),
[response handling](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2-api-client/src/core/request.ts#L238-L294).

## Public response requirements beyond stored schema validity

- Populate metadata `extension.px.tableid` with our combined public ID and
  `extension.px.language` with the selected language. The mapper obtains its
  metadata identity there, not from a NordicIntel identity object. Generate
  these in the public response; do not retain an upstream table ID in this field.
- Supply public `self` and `alternate` table links with `hreflang`, advertising
  only eligible language variants. The table language switcher derives its
  available languages from those relations.
- Populate metadata `label` and `updated` from basic information. Missing
  metadata `updated` is replaced by the current date in the UI, so our agreed
  publication requirement also prevents a misleading UI fallback.
- Return normalized category index and label maps. The UI sorts category codes
  by their numeric positions. It enumerates dimensions from the object and
  reorders them by role for selection display rather than simply following `id`.
  Keep canonical `id` ordering for the API; do not claim the UI preserves it.
- Preserve truthful `role.time`, `role.metric` and `role.geo` assignments.
  Content units are read from `category.unit[code].base`, with decimals; a generic
  unit label alone does not populate that display. Normalize known source units
  in the public representation when appropriate, not by inventing unit text.
- Optional root/dimension `link.related` entries need special care: the mapper
  dereferences each item's `extension.relation` or `extension.metaid` without
  checking that `extension` exists. Valid generic JSON-stat related links are
  therefore not automatically safe to pass through. Adapt relevant links to the
  PX shape, or guard these accesses in the UI; preserve the stored originals.
- PX `stub`/`heading` are used for presentation layout, without an automatic
  layout in these mapper functions. They can be derived by the public API when
  data presentation is implemented; they are not new stored eligibility fields.

Evidence: [metadata mapper](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/mappers/JsonStat2ResponseMapper.ts#L34-L268),
[categories and units](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/mappers/JsonStat2ResponseMapper.ts#L341-L431),
[language links](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/components/Selection/selectionUtils.ts#L10-L22).

## Publication policy and public formatting

Agreed NordicIntel policy remains: each eligible language variant needs a valid,
consistent basic/metadata pair and actual `updated`, `first_period`, `last_period`
and `time_unit` values. Missing values block publication, not authenticated
storage. PostgreSQL should maintain eligibility and blocking reasons on writes.
Existing development documents can be discarded and reharvested.

The UI uses update dates for ordering/display, periods for year filtering, and
time units for frequency filters. These support our policy, although its code
contains fallbacks for missing values. It does not enforce the pinned upstream
specification's contradictory update-date regex at runtime. Emit parseable dates
without fabricating an observation-update timestamp. The public enum is
`Annual`, `Quarterly`, `Monthly`, `Weekly`, `Other`: map known stored time-unit
notations into this vocabulary, keeping the stored string unchanged.
The year filter understands a leading four-digit year or a `YYYY-YYYY` range;
nonblank period strings alone do not guarantee useful year filtering. Check real
provider period notation during public projection tests.

Thematic paths power subject filtering. They remain classifications, not access
keys. Breadcrumb selection looks for a path whose first node ID matches the
table's `subjectCode`; absent or mismatched paths reduce navigation rather than
preventing metadata mapping. Do not add paths as a publication requirement just
to satisfy this optional UI feature.

Evidence: [table-card rendering](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/pages/StartPage/StartPage.tsx#L400-L478),
[filters and sorting](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/util/startPageFilters.ts),
[public time-unit enum](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2-api-client/src/models/TimeUnit.ts).

## Configuration, identifiers and deferred features

Configure the UI's `public/config/config.js` with our API URL and Swedish default
and fallback language; API defaults alone do not control its initial language.
Advertise `sv`/`en` as supported as appropriate. Its current feature switch is
for charts, not a general metadata-only mode, and `/config` feature declarations
will not automatically disable data or saved-query controls. Implement `/config`
for the public API contract, without treating it as a UI bootstrap dependency.
If UI and API have different origins, configure public-route CORS and serve the
SPA with deep-link fallback. No admin credentials belong in browser configuration.
[Static config](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/public/config/config.js),
[config type](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/util/config/configType.ts).

The agreed colon separator works with the inspected URL construction. However,
the UI interpolates IDs directly into routes and the generated client uses
`encodeURI`, which preserves `/`, `?` and `#`. Existing opaque dataset codes
containing those characters need correct encoding throughout UI links, client
requests and server routing. Keep the agreed identifier; test actual problematic
codes rather than inventing a second identifier system.
[UI link construction](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/app/pages/StartPage/StartPage.tsx#L408-L420),
[client encoding](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2-api-client/src/core/request.ts#L90-L110).

Until codelist support exists, do not advertise selectable codelists in the public
response. Retain them in stored metadata. Requests that explicitly ask for an
unsupported codelist or saved-query transformation must fail clearly, not return
unchanged metadata as if the transformation succeeded. The default-selection
response can use actual category codes without applying codelists; its concrete
selection policy still needs implementation. The UI consumes `selection` entries
with `variableCode`, `valueCodes` and optional `codelist`.
[Selection mapper](https://github.com/PxTools/PxWeb2/blob/6c46c20d5ed8547c009ec255532c64ca884e762e/packages/pxweb2/src/mappers/TableSelectionResponseMapper.ts).

## Implementation and acceptance scope

1. Build catalog publication checks and public table/list/metadata/default-selection
   responses, simple query matching, language links and consistent problem errors.
2. Keep the agreed data/codelist/saved-query 501 routes, including saved-query
   selection. Add a small explicit UI mode that leaves category selection usable
   while disabling automatic data loads, downloads and saved-query controls.
3. Set static UI configuration and public CORS. Handle related links and ID
   encoding. Do not change the shared storage schemas just to mirror UI internals.
4. Run the pinned UI against the actual catalog API: Swedish default, English
   switch, hidden variants, search, frequency/year/subject filters, colon IDs,
   real opaque IDs, direct URL reloads, default selections and category changes.
5. Verify unsupported operations return 501 while the adapted UI stays usable;
   exercise missing dates and incomplete documents through admin writes and verify
   public eligibility changes. Inspect browser network traffic, not just fixtures.

These are recommendations grounded in the inspected source. UI changes, catalog
implementation, deployments and browser acceptance remain future work. The
schemas collection's pinned PxWeb specification and this pinned UI revision are
separate references; passing structural fixtures alone does not prove UI behavior.
