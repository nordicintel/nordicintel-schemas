# Schemas

All files use Draft 2020-12 and versioned `$id` URLs. References resolve locally
during validation; public URLs become usable after publication of their tag.

| Contract | Purpose |
| --- | --- |
| [Provider](provider.schema.json) | Public information plus optional stored `harvest` settings |
| [Harvest config](harvest-config.schema.json) | Adapter, configured languages, rate limit, and config stored with a provider |
| [Harvest input](harvest-input.schema.json) | Resolved inputs for one provider-language execution |
| [Dataset](dataset.schema.json) | Basic information; owns the shared `identity` definition in `$defs` |
| [Dataset metadata](dataset-metadata.schema.json) | Dimensions, categories, classification, and optional retrieval configuration |
| [PXWeb v1](adapters/pxweb_v1.schema.json) | Harvest config at the root; retrieval config in `$defs/retrieval` |
| [PXWeb v2](adapters/pxweb_v2.schema.json) | Harvest config at the root; retrieval config in `$defs/retrieval` |
| [Kolada](adapters/kolada.schema.json) | Harvest config at the root; retrieval config in `$defs/retrieval` |

Adapter files validate only adapter-specific config. The surrounding harvest
contracts supply provider identity, language, and `rate_limit`; metadata supplies
identity and dimensions for retrieval. Adding an adapter requires updating the
harvest and retrieval dispatch schemas as well as its own config contract.
