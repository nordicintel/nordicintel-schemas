# Roadmap

1. **Prepared: 2.0.0 shared statistical contracts.** JSON-stat foundation, defined
   PX extensions, revised basic/detail split, and implementation-owned adapter
   settings. Examples and offline structural checks are included.
2. **Review public compatibility gaps.** Resolve API policy for missing dates and
   periods, contact completeness and upstream specification inconsistencies before
   claiming full PxWeb compatibility. Test the intended UI in the API project.
3. **Publish 2.0.0 deliberately.** Review/merge, pass CI, then follow manual release
   checks. Existing 1.0.0 stays immutable; application adoption is separate.
4. **Adopt in the separate projects.** Harvest owns configuration and job controls;
   catalog owns provider/dataset persistence and its public PxWeb-compatible API.
   Settle execution persistence and write consistency there.

No application changes, release, observation retrieval, provider selection or
recurring scheduling are implemented by this schemas revision.
