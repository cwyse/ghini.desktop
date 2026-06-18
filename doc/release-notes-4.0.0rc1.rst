Ghini 4.0.0rc1 Release Notes
============================

Status
------

These are draft release-candidate notes for the Ghini 4 baseline. Do not tag
``v4.0.0rc1`` until final release review is complete.

Supported Baseline
------------------

This release candidate targets the Docker development/runtime workflow on a
current Ubuntu host. The supported path is:

* GTK 3.24 through the Docker development image.
* Python dependencies from the repository lock files.
* SQLAlchemy 2 runtime behavior.
* SQLite databases for local testing and small deployments.
* PostgreSQL databases, including the disposable Docker PostgreSQL test lane.
* VS Code development against the Docker image.

Ghini remains a GTK 3 application. GTK 4 migration is intentionally out of
scope.

Daily Workflow Scope
--------------------

The release-candidate baseline focuses on the daily botanical collection
workflow:

* search for families, genera, species, accessions, plants, and locations;
* create and edit family, genus, and species records;
* use genus autocomplete while creating species;
* validate species names through the WFO-backed taxonomic lookup path;
* add vernacular names and notes;
* add species-level structured culture guidance;
* create accessions from species;
* select or create accession sources;
* create locations and plants;
* add and redisplay seed propagation records;
* edit records from the result tree context menu;
* handle delete confirmations without accidental removal.

Major Changes
-------------

Runtime and development
~~~~~~~~~~~~~~~~~~~~~~~

* Added the Docker/VS Code development workflow as the supported runtime and
  development path.
* Added pinned dependency locks and warning-gated test commands.
* Added Black to the Docker development image and check workflow.
* Added deterministic version reporting from git metadata.
* Added release smoke, regression, GUI E2E, guided visual, and PostgreSQL test
  commands through ``scripts/docker-dev``.

Database and SQLAlchemy 2
~~~~~~~~~~~~~~~~~~~~~~~~~

* Updated SQLAlchemy 2 behavior around transactions, raw SQL execution,
  relationship handling, and nullable schema fields discovered during import
  testing.
* Added a PostgreSQL disposable test lane.
* Fixed PostgreSQL closed-connection recovery for search/home navigation.
* Fixed sequence reset behavior and error reporting paths found during import
  testing.

GUI workflow
~~~~~~~~~~~~

* Restored autocomplete behavior in primary search and daily workflow
  selectors.
* Stabilized result-tree context-menu editing after search refreshes.
* Fixed result infobox tracebacks in daily searches for location, family,
  genus, and species results.
* Added automated GUI E2E coverage for search, edit, delete confirmation,
  creation, location, source, plant, and propagation workflows.
* Fixed propagation persistence and redisplay behavior found during guided
  testing.
* Fixed editor handling for vernacular-name persistence and database length
  validation.
* Made Ctrl-Enter accept editor dialogs when the OK/Accept response is enabled.
* Enabled current-change reason controls for existing plant records.
* Allowed custom current-change reason text without changing the legacy schema:
  the stored reason remains ``Other`` and the exact text is attached through
  the existing change-note relationship.
* Allowed custom accession material text and fuzzy received quantities while
  preserving legacy database columns. Custom material stores ``Unknown`` plus
  an accession note; fuzzy quantities store the parsed integer plus the exact
  quantity phrase in an accession note.
* Added species-level culture profiles with controlled terms, numeric ranges,
  practical flags, active growth/bloom/fruit/pruning months, notes, source
  citation, a Species Editor Culture tab, and result-detail display.
* Split accession source mode from contact selection so garden propagation is
  no longer shown as a contact, while real contacts remain sorted and
  deduplicated.
* Added source/contact categories for collection, donation, purchase, and
  confiscated material.

Import and export
~~~~~~~~~~~~~~~~~

* Fixed quick CSV export handling for optional empty relationships.
* Added tests that accepted-name imports preserve both the original and
  accepted taxa.
* Kept useful exception details in import failure dialogs.
* Refreshed both the active view and home count view after CSV restore/import
  operations.

Reports and labels
~~~~~~~~~~~~~~~~~~

* Included species authors in the HTML plant label templates.
* Added focused regression coverage for author rendering in the small and
  standard HTML label templates.

Taxonomic lookup
~~~~~~~~~~~~~~~~

* Added a normalized taxonomic lookup provider layer.
* Implemented WFO as the first provider for interactive species lookup.
* Kept the existing Species Editor callback behavior through a compatibility
  adapter.
* Verified live WFO lookup from the Docker image with HTTPS verification
  enabled.
* Updated the legacy manual batch TNRS workflow to use the WFO-backed provider
  lookup path.

Fixed Release-Blocking Issues
-----------------------------

The following GitLab issues were fixed or reclassified for this release
candidate:

* #24 Replace legacy plant-name lookup with maintained TNRS/WFO-compatible
  service.
* #29 Stabilize accession source selector for daily accession workflow.
* #30 Restore autocomplete in primary search and daily workflow selectors.
* #32 Vernacular-name entry must persist without special Enter-key handling.
* #33 Quick CSV export must tolerate optional empty values.
* #34 Taxon import with accepted-name data must preserve both taxa.
* #35 Daily editor fields should validate or safely handle database length
  limits.
* #36 PlantsPlugin initialization fails when preferences are unavailable.
* #37 Modernize batch taxonomy check with provider-backed lookup.
* #38 Main search field unusable after species editor save.
* #39 Species Notes editor can hang during routine species entry.
* #40 Daily searches log infobox tracebacks during result display.
* #41 Add Accession from new Species can fail with detached Species instance.
* #42 Add Accession can autoflush incomplete seed propagation during editor
  startup.
* Upstream #63 identification qualifiers now render in the expected position.
* Upstream #397 editor dialogs accept Ctrl-Enter for enabled OK/Accept actions.
* Upstream #452 backup restore/import refreshes the home count view.
* Upstream #454 HTML plant labels include species authors.
* Upstream #55/#56 intended-location regressions.
* Upstream #157 deleted top-level records remain in search results.
* Upstream #252 previously used empty locations cannot be deleted.
* Upstream #9 accession material can record offset/rooted offset and preserve
  custom typed material.
* Upstream #14 plant current-change reasons can preserve custom typed text.
* Upstream #36 provenance values include donation, confiscated material,
  collection, propagule, and in vitro material.
* Upstream #235 accession source/contact categories include collection,
  donation, purchase, and confiscated material, and garden propagation is a
  source mode rather than a pseudo-contact.
* Upstream #466 accession received quantity can preserve fuzzy quantity text
  while keeping a parsed integer for legacy quantity behavior.
* Upstream #180 propagation editors include structured notes.
* Upstream #457 infraspecific taxa create/reuse required autonym taxa.
* Upstream #465 species-level culture information can be recorded manually
  through structured culture profiles.

Deferred Issues
---------------

The following work is intentionally deferred from ``v4.0.0rc1``:

* #7 Triage the full upstream GitHub issue backlog.

Known Scope Limits
------------------

* The root ``Dockerfile`` is older experimental packaging work. Use
  ``Dockerfile.dev`` and ``scripts/docker-dev`` for this release candidate.
* The batch taxonomy-check workflow now uses the provider-backed WFO lookup
  path instead of the old TNRS file-import flow.
* Culture profiles are manually entered species-level guidance. Import/export,
  external culture-data providers, and lower-level accession/plant/location
  culture overrides are not included in this release candidate.
* Full report generation is not yet treated as a release-blocking daily
  workflow gate. HTML plant-label author rendering is covered by a focused
  regression test.
* GTK menu icon warnings are tracked as non-blocking unless they affect daily
  workflow behavior.

Test Evidence
-------------

Release-gate evidence was refreshed on 2026-06-18 at ``c2159e62``
with application code through ``8a5920e3``:

* ``scripts/docker-dev test-regression`` passed:

  * warning-gated suite: 459 passed, 44 skipped;
  * GTK smoke suite: 175 passed;
  * full automated Dogtail GUI E2E suite: 30 passed.

* ``scripts/docker-dev build`` completed successfully and rebuilt
  ``ghini-desktop-dev:latest`` from the current checkout.

* ``GHINI_SOURCE_POSTGRES_URI=... scripts/docker-dev postgres-release`` passed
  after copying representative ``ghini_test3`` data from
  ``postgres.wysechoice.net`` into a disposable local PostgreSQL container:

  * disposable PostgreSQL schema lane: 3 passed;
  * representative PostgreSQL read-only smoke lane: 8 passed.

* Open GitLab issue review completed at ``32b59e85``:

  * #31 remains open as the release tracker;
  * #7 remains open as ``release-deferred``;
  * #37 and the imported release-scope upstream workflow items are implemented
    in-tree and closed in the tracker.

Earlier release hardening also verified a live WFO provider smoke query from
the Docker image. That check should be rerun if the release candidate is
rebuilt after additional dependency or certificate changes.

Pending Release Gates
---------------------

Before tagging ``v4.0.0rc1`` with culture support included:

* perform final review of the release notes and open issue classifications;
* tag ``v4.0.0rc1`` after final review is complete.

Guided visual scenarios are not a required ``v4.0.0rc1`` gate after the
automated GUI E2E suite passes. The guided scenarios were used to find release
blockers, and the current automated suite covers those regressions. They remain
available for optional visual confirmation before tagging.
