# Upstream Release Triage

This document records the first release-focused pass over open upstream GitHub
issues in `Ghini/ghini.desktop`.

Reviewed source:

- Upstream repository: <https://github.com/Ghini/ghini.desktop>
- Open upstream issue list reviewed with `gh issue list` on 2026-05-23.
- Local release policy: [release-readiness.rst](release-readiness.rst)

The goal is not to bulk-import the upstream backlog. The first Ghini 4 baseline
release should include only issues that affect startup, data integrity,
database compatibility, search/navigation, or the daily
taxonomy-to-accession-to-plant workflow.

## Already Covered Or Superseded

| Upstream | Decision | Local coverage |
| --- | --- | --- |
| [#425](https://github.com/Ghini/ghini.desktop/issues/425) Error `(psycopg2.InterfaceError) connection already closed` | Covered | Closed locally by PostgreSQL dropped-connection recovery and `postgres-check` coverage. |
| [#308](https://github.com/Ghini/ghini.desktop/issues/308) Missing timezone in MapperBase timestamps | Covered | Closed locally by local date/UTC audit timestamp policy. |
| [#130](https://github.com/Ghini/ghini.desktop/issues/130) Cannot expand row if expanded while nothing depends on it | Covered | Closed locally by result expansion retry fix and GTK smoke coverage. |
| [#55](https://github.com/Ghini/ghini.desktop/issues/55) Intended-location buttons do not activate | Covered | Closed locally by accession intended-location button regression coverage. |
| [#56](https://github.com/Ghini/ghini.desktop/issues/56) New accession reuses previous intended locations | Covered | Closed locally by fresh-accession intended-location regression coverage. |
| [#157](https://github.com/Ghini/ghini.desktop/issues/157) Deleted top-level objects remain in result view | Covered | Closed locally by pruning deleted objects from the active search result tree after successful delete callbacks. |
| [#252](https://github.com/Ghini/ghini.desktop/issues/252) Empty location cannot be deleted after prior use | Covered | Closed locally by clearing historical `PlantChange` location references before deleting an otherwise empty location. |
| [#463](https://github.com/Ghini/ghini.desktop/issues/463) The Plant List to World Flora Online | Imported | Covered by GitLab #24. |
| [#472](https://github.com/Ghini/ghini.desktop/issues/472) TNRS moved | Imported | Covered by GitLab #24. |
| [#111](https://github.com/Ghini/ghini.desktop/issues/111) Autocomplete for manual query properties | Partially imported | Daily-workflow autocomplete is covered by GitLab #30; full query-builder-style completion remains deferred. |
| [#58](https://github.com/Ghini/ghini.desktop/issues/58) ID format and wild status in accession editor | Covered by release gate | The current Accession Editor exposes ID format and wild status fields. Keep this in the daily workflow guided test rather than importing separately unless testing fails. |
| [#72](https://github.com/Ghini/ghini.desktop/issues/72) Error creating connection manager presenter | Covered by release gate | Connection manager startup is covered by automated and guided tests. Import only if reproduced on GTK 3.24. |
| [#63](https://github.com/Ghini/ghini.desktop/issues/63) Identification qualifier spacing | Covered | Genus-level accession qualifiers now render between genus and epithet, and accession species-string caching includes qualifier state. |
| [#454](https://github.com/Ghini/ghini.desktop/issues/454) Authors missing on some labels | Covered | HTML label templates now render species authors, with Mako template regression coverage. |
| [#397](https://github.com/Ghini/ghini.desktop/issues/397) Ctrl-Enter accelerator consistency | Covered | Generic editor dialogs now accept sensitive OK/Accept responses on Ctrl-Enter. |
| [#452](https://github.com/Ghini/ghini.desktop/issues/452) Backup restore home count refresh | Covered | CSV restore updates both the active view and cached home view after import progress changes. |
| [#9](https://github.com/Ghini/ghini.desktop/issues/9) User-defined type-of-material values | Covered for baseline | Accession material now includes offset and rooted offset. Unknown typed material is preserved in an accession note while storing the legacy `UNKN` material code. |
| [#14](https://github.com/Ghini/ghini.desktop/issues/14) User-defined reason for current change | Covered for baseline | Plant current-change reasons now accept typed custom text. The change stores legacy reason `OTHR` and preserves the exact custom reason through the existing `plant_change.note_id` relationship. |
| [#36](https://github.com/Ghini/ghini.desktop/issues/36) Provenance list | Covered for baseline | Provenance values now include donation, confiscated material, collection, propagule, and in vitro material. |
| [#235](https://github.com/Ghini/ghini.desktop/issues/235) Accession source categories | Covered for baseline | The Source tab separates external contact/source records from garden propagation sources, source contacts are sorted/deduplicated, and contact source types include collection, donation, purchase, and confiscated material. |
| [#466](https://github.com/Ghini/ghini.desktop/issues/466) Quantity units and fuzzy support | Covered for accession baseline | Accession received quantity now accepts phrases with a number, stores the parsed integer quantity, and preserves the exact phrase in an accession note for display and future schema migration. |
| [#180](https://github.com/Ghini/ghini.desktop/issues/180) Notes tab in propagations | Covered | Propagation editors now expose structured notes through the same note presenter used elsewhere, including user/category/date/note persistence and focused GTK smoke coverage. |
| [#457](https://github.com/Ghini/ghini.desktop/issues/457) Implement autonyms | Covered for core taxonomy workflow | Non-cultivar infraspecific taxa now create/reuse the required autonym sibling, exact species retrieval distinguishes infraspecific taxa, and an existing base species is linked to the autonym as its accepted taxon. Covered by plants model tests. |

## Include In Release Scope

These issues should either be fixed before `v4.0.0` or explicitly reclassified
after current-code reproduction.

| Upstream | Release reason | Local action |
| --- | --- | --- |
| [#95](https://github.com/Ghini/ghini.desktop/issues/95) Vernacular-name entry requires Enter to persist | Daily species workflow includes adding vernacular names for labels. Losing the value is data loss from the user's perspective. | Imported as GitLab #32. |
| [#461](https://github.com/Ghini/ghini.desktop/issues/461) Quick CSV export stops on `None` values | Export should tolerate optional fields. This is part of the import/export release gate. | Imported as GitLab #33. |
| [#441](https://github.com/Ghini/ghini.desktop/issues/441) Taxon import with `accepted` field does not import both taxa | Taxonomic import/data integrity issue. It overlaps the SQLAlchemy/import regression gate. | Imported as GitLab #34. |
| [#399](https://github.com/Ghini/ghini.desktop/issues/399) Text entries do not validate database field lengths | Can turn normal editor input into database errors, especially for long location/source names. | Imported as GitLab #35, scoped to daily editors first. |

## Defer From First Baseline Release

These issues may matter later, but should not block the first stable Ghini 4
baseline unless a current test proves they break the supported workflow.

| Upstream | Decision |
| --- | --- |
| [#15](https://github.com/Ghini/ghini.desktop/issues/15) List for accession intended locations | Enhancement; verify current controls but do not expand behavior for baseline. |
| [#98](https://github.com/Ghini/ghini.desktop/issues/98) Accession ID qualifier semantics | Broader taxonomy/design question; researched below, not implemented. |
| [#465](https://github.com/Ghini/ghini.desktop/issues/465) Better plant culture information | Enhancement/design work; researched below, not implemented. |
| [#458](https://github.com/Ghini/ghini.desktop/issues/458) GBIF as taxonomic source | Provider decision belongs to GitLab #24, not baseline runtime stability. |
| [#444](https://github.com/Ghini/ghini.desktop/issues/444) Improved renaming and synonyms workflow | Important but larger than baseline stabilization. |
| [#403](https://github.com/Ghini/ghini.desktop/issues/403) Windows installer | Out of scope for Ubuntu/Docker baseline release. |
| [#432](https://github.com/Ghini/ghini.desktop/issues/432), [#325](https://github.com/Ghini/ghini.desktop/issues/325), [#245](https://github.com/Ghini/ghini.desktop/issues/245) macOS/OSX items | Out of scope for Ubuntu/Docker baseline release. |

## Researched Future Work

### #465 Better plant culture information

Current state: Ghini has species-level `habit`, `awards`, `label_distribution`,
`bc_distribution`, notes, and source habitat text. It does not have structured,
queryable culture requirements for common horticultural dimensions such as
moisture, light, pH, soil/drainage, temperature, frost tolerance, or greenhouse
conditions.

Recommended implementation subtasks:

1. Define scope and ownership:
   decide whether culture data belongs to Species, Accession, Plant, Location,
   or a combination. Default recommendation is Species-level defaults with
   optional Plant/Accession overrides later.
2. Define controlled vocabularies:
   choose stable value sets for moisture, light, temperature, soil/drainage,
   pH range, growth rate, and seasonal care. Keep free-text notes for uncommon
   detail instead of overfitting the first schema.
3. Add a normalized model:
   create culture-profile tables with controlled-value rows and optional numeric
   ranges where search/reporting needs them. Avoid encoding this in generic notes
   if the intent is searchable culture data.
4. Build import/export mapping:
   include CSV/JSON fields for the culture profile and make absent values safe
   for SQLite and PostgreSQL.
5. Add Species Editor UI:
   add a Culture or Properties tab with compact controls, validation, and no
   regression to the existing Additional info and Notes tabs.
6. Add search/report support:
   expose culture fields to search, infobox display, labels where useful, and
   flat export.
7. Add tests:
   cover schema creation, editor save/reopen, CSV round trip, search predicates,
   and PostgreSQL release smoke.

Do not implement until the vocabulary and ownership decisions are made. The
first implementation should be small enough to avoid forcing all gardens into
one culture model. A first-pass design proposal is documented in
`doc/culture-profile-design.md`.

### #98 Accession ID qualifier semantics

Current state: Accession stores `id_qual` plus `id_qual_rank` and injects the
qualifier into the selected taxon string. This handles simple cases such as
`Iris cf. florentina`, but it cannot represent a comparison target such as
`Genus species_1 aff. Genus species_2` as structured data.

Recommended implementation subtasks:

1. Define identification model semantics:
   distinguish the recorded taxon, qualifier, qualified rank, comparison target,
   determiner, verification date, confidence, and current accepted
   identification.
2. Reconcile with existing verifications:
   decide whether this is an extension of accession verifications or a new
   identification table. Prefer extending verification concepts if they already
   represent taxonomic determinations.
3. Preserve backward compatibility:
   keep `id_qual` and `id_qual_rank` readable/writable, and derive the old string
   display from the richer model during a transition.
4. Add comparison target support:
   allow a qualifier such as `aff.` or `cf.` to reference another Species record
   or a typed unresolved name when the comparison taxon is not in the database.
5. Update Accession Editor UX:
   add fields for qualifier target and determiner without making the common
   unqualified case slower.
6. Update formatting/search:
   centralize display generation so labels, search results, reports, and exports
   render the same identification phrase.
7. Add migration/import/export:
   migrate existing `id_qual` rows into the richer representation and include CSV
   and JSON round-trip coverage.
8. Add tests:
   cover simple legacy qualifiers, comparison-target qualifiers, unresolved
   targets, report output, search output, and PostgreSQL behavior.

Do not implement until the verification relationship is decided. The risk is not
the UI field itself; the risk is creating a second identification system that
conflicts with accession verifications.

## Follow-Up

1. Add current-code reproduction tests before fixing broad issues.
2. Continue upstream backlog triage when release blockers are stable.
3. Update this table when an upstream issue is fixed, imported, or explicitly
   deferred.
