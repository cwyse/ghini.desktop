# Culture Profile Design

Status: implemented for the Ghini 4 release baseline. This document records
the approved species-level scope and the schema/UI decisions used by the
implementation.

## Goal

Add structured, searchable plant culture information for Ghini issue #465 while
keeping entry manual and reliable. The first implementation should support the
daily garden workflow without becoming a complete trait database.

The profile describes default culture requirements for a species. Local garden
observations belong in normal notes on the relevant species, accession, plant,
location, or propagation record. Lower-level culture overrides are intentionally
out of scope.

## Existing Ghini Context

Ghini already stores these culture-adjacent values:

- `Species.habit`, backed by the controlled `habit` table imported from
  `bauble/plugins/plants/default/habit.txt`.
- `Species.awards`, free text.
- `Species.label_distribution` and `Species.bc_distribution`, free text.
- species notes, source habitat text, accession source details, and actual
  propagation records.

Those fields should stay intact. The new culture profile should not replace
`Habit`; it should add searchable growing requirements that are currently only
possible as notes.

## External Models Reviewed

### Trefle

Trefle's plant field model is the best structural starting point. It separates
taxonomy from growth/specification fields and defines numeric or constrained
values for duration, pH, light, atmospheric humidity, growth months, bloom
months, fruit months, annual precipitation, root depth, minimum/maximum
temperature, soil nutrients, salinity, texture, and soil humidity.

Use from Trefle:

- 0-10 scale for light, humidity, soil nutrients, salinity, texture, and soil
  humidity.
- Controlled duration/life-cycle terms.
- Decimal ranges for pH and temperature.
- Month-set fields for growth, bloom, and fruiting periods.

Do not copy blindly:

- Some terms are ecological/agronomic rather than day-to-day horticultural UI
  terms.
- The service documentation was last updated in 2022, so Ghini should treat it
  as a model, not a dependency.

Reference: https://docs.trefle.io/docs/advanced/plants-fields/

### Perenual

Perenual is closer to user-facing plant-care language. It exposes practical
fields such as watering, sunlight, hardiness, soil, propagation, growth rate,
maintenance, duration/cycle, drought tolerance, salt tolerance,
poisonous-to-humans/pets, tropical, indoor, pruning month, and care level.

Use from Perenual:

- User-friendly enum labels for watering, sunlight, hardiness, growth rate, and
  maintenance.
- Practical cycle labels that map cleanly onto duration terms.
- Optional future mapping from practical API values to Ghini's internal numeric
  ranges.

Do not copy blindly:

- Some fields are paid-tier dependent.
- Some values are more consumer-houseplant oriented than botanical-garden
  oriented.

Reference: https://perenual.com/docs/api

### OpenFarm

OpenFarm had growing-guide concepts such as spacing, watering, soil composition,
companion plants, and sun/shade requirements. It is not suitable as a live
dependency because its public servers were shut down in April 2025, but its
guide-oriented approach confirms that culture data needs structured fields plus
free-text notes.

Reference: https://github.com/openfarmcc/OpenFarm

## Proposed Ownership

Phase 1 should add one culture profile per species:

- A species can have zero or one culture profile.
- The culture profile stores default requirements for successful cultivation.
- It is independent of actual propagation events.
- It does not change accession, plant, location, or source behavior.

Not included:

- Accession-specific culture overrides.
- Plant/location/greenhouse overrides.
- Imported culture-provider records.
- Recommendation engines or automatic fill from external APIs.

## Proposed Phase 1 Field Set

The first set should be small enough to implement and test well, but expressive
enough to support accurate search.

### Core Searchable Requirements

| Field | Type | Proposed values or constraints | Source model |
| --- | --- | --- | --- |
| `light_min`, `light_max` | integer range | 0-10, where 0 is no light and 10 is full intense sun | Trefle |
| `soil_moisture_min`, `soil_moisture_max` | integer range | 0-10, dry/xeric to aquatic/subaquatic | Trefle |
| `atmospheric_humidity_min`, `atmospheric_humidity_max` | integer range | 0-10, very dry to very humid | Trefle |
| `soil_ph_min`, `soil_ph_max` | decimal range | 0.0-14.0 | Trefle |
| `temperature_min_c`, `temperature_max_c` | decimal range | Celsius, nullable | Trefle |
| `hardiness_zone_min`, `hardiness_zone_max` | integer range | USDA zones 1-13, nullable | Perenual/common horticulture |
| `soil_nutrient_min`, `soil_nutrient_max` | integer range | 0-10, low to high fertility | Trefle |
| `soil_salinity_tolerance` | integer | 0-10, intolerant to highly tolerant | Trefle |
| `soil_texture_min`, `soil_texture_max` | integer range | 0-10, clay/heavy to rock/coarse | Trefle |
| `watering` | enum | none, minimum, average, frequent | Perenual |
| `growth_rate` | enum | slow, moderate, fast | Perenual/Trefle |
| `maintenance` | enum | low, moderate, high | Perenual |

### Controlled Multi-Value Fields

These should be many-to-many controlled terms, not comma-separated text:

| Field | Values |
| --- | --- |
| `duration_terms` | annual, biennial, perennial, monocarpic_perennial, short_lived_perennial |
| `sunlight_terms` | full_shade, part_shade, part_sun, full_sun |
| `soil_drainage_terms` | poor, moderate, well_drained, sharply_drained |
| `soil_type_terms` | clay, loam, sand, gravel, rock, organic, bark, aquatic |
| `recommended_propagation_terms` | seed, cutting, division, grafting, layering, offsets, spores, tissue_culture |
| `environment_terms` | outdoor, indoor, cool_greenhouse, warm_greenhouse, hot_house, seasonal_protection |

`sunlight_terms` intentionally duplicates the numeric light range in a
user-friendly way. Search can use either exact terms or numeric range
comparisons, and the UI can map terms to ranges.

`duration_terms` is intentionally separate from `Species.habit`. Habit describes
plant form, while duration describes life cycle. Existing habit values such as
"Herbaceous, Annual" should remain valid, but new searches should not need to
parse habit labels to find annuals, biennials, or perennials.

### Seasonal Fields

Use month sets, not free text:

| Field | Type |
| --- | --- |
| `growth_months` | set of month numbers 1-12 |
| `bloom_months` | set of month numbers 1-12 |
| `fruit_months` | set of month numbers 1-12 |
| `pruning_months` | set of month numbers 1-12 |

These are useful, but they can be omitted from the first UI if the initial
implementation needs to stay smaller.

### Boolean Flags

Keep boolean flags limited. Proposed phase 1 flags:

| Field | Meaning |
| --- | --- |
| `drought_tolerant` | Can tolerate extended dry periods once established. |
| `salt_tolerant` | Can tolerate saline soil or salt exposure. |
| `frost_sensitive` | Requires protection from frost. |
| `indoor_suitable` | Suitable for indoor culture under ordinary conditions. |
| `greenhouse_required` | Normally needs greenhouse/protected culture locally. |

Fields such as edible, medicinal, toxic, invasive, rare, and thorny are useful
plant traits but are not culture requirements. They should be separate future
work unless the release scope changes.

### Free Text

Free text should supplement, not replace, structured fields:

| Field | Purpose |
| --- | --- |
| `culture_notes` | Short horticultural notes not captured by controlled fields. |
| `source_citation` | Manual reference text or URL for the profile values. |
| `local_notes` | Dormant compatibility column. Not exposed in the UI; use normal notes for local observations. |

## UI Vocabulary Labels

The stored values should remain stable codes. The UI can present friendlier
labels:

- Light: deep shade, shade, part shade, part sun, full sun.
- Duration: annual, biennial, perennial, monocarpic perennial, short-lived
  perennial.
- Moisture: dry, average, moist, wet, aquatic.
- Humidity: dry air, average, humid, very humid.
- Fertility: low, average, high.
- Salinity: none, low, moderate, high.
- Texture: clay/heavy, loam, sandy, gravelly, rocky/coarse.
- Maintenance: low, moderate, high.

## Search Requirements

The design must support queries such as:

- species suitable for full sun.
- species that tolerate dry soil.
- species hardy to zone 6 or colder.
- species with pH range overlapping 5.5-6.5.
- species suitable for warm greenhouse culture.
- species propagated by cuttings.
- annual species, perennial species, or short-lived perennials.

For numeric ranges, search should use overlap semantics:

- A plant matches a requested value if `min <= requested <= max`.
- A plant matches a requested range if the ranges overlap.

## Proposed Database Schema

Distribution is intentionally excluded from this schema. Existing
`SpeciesDistribution`, `GeographicArea`, `Species.label_distribution`, and
`Species.bc_distribution` behavior should remain unchanged.

The schema is species-level only. It stores culture defaults for a species.
Accession-, plant-, location-, and greenhouse-specific culture overrides are
not planned for this release path; use normal Ghini notes for those cases.

### `species_culture_profile`

One optional profile per species.

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | integer primary key | no | Autoincrement primary key. |
| `species_id` | integer foreign key | no | References `species.id`; unique. |
| `light_min` | small integer | yes | 0-10. |
| `light_max` | small integer | yes | 0-10, `light_min <= light_max` when both present. |
| `soil_moisture_min` | small integer | yes | 0-10. |
| `soil_moisture_max` | small integer | yes | 0-10, min/max checked. |
| `atmospheric_humidity_min` | small integer | yes | 0-10. |
| `atmospheric_humidity_max` | small integer | yes | 0-10, min/max checked. |
| `soil_ph_min` | numeric(3, 1) | yes | 0.0-14.0. |
| `soil_ph_max` | numeric(3, 1) | yes | 0.0-14.0, min/max checked. |
| `temperature_min_c` | numeric(5, 2) | yes | Celsius. |
| `temperature_max_c` | numeric(5, 2) | yes | Celsius, min/max checked. |
| `hardiness_zone_min` | small integer | yes | USDA zone 1-13. |
| `hardiness_zone_max` | small integer | yes | USDA zone 1-13, min/max checked. |
| `soil_nutrient_min` | small integer | yes | 0-10. |
| `soil_nutrient_max` | small integer | yes | 0-10, min/max checked. |
| `soil_salinity_tolerance` | small integer | yes | 0-10. |
| `soil_texture_min` | small integer | yes | 0-10. |
| `soil_texture_max` | small integer | yes | 0-10, min/max checked. |
| `watering` | enum/string | yes | `none`, `minimum`, `average`, `frequent`. |
| `growth_rate` | enum/string | yes | `slow`, `moderate`, `fast`. |
| `maintenance` | enum/string | yes | `low`, `moderate`, `high`. |
| `drought_tolerant` | boolean | yes | Tri-state: unknown/null, yes/true, no/false. |
| `salt_tolerant` | boolean | yes | Tri-state. |
| `frost_sensitive` | boolean | yes | Tri-state. |
| `indoor_suitable` | boolean | yes | Tri-state. |
| `greenhouse_required` | boolean | yes | Tri-state. |
| `culture_notes` | unicode text | yes | Structured fields should be preferred for search. |
| `source_citation` | unicode text | yes | Manual reference text or URL. |
| `local_notes` | unicode text | yes | Dormant compatibility column; not exposed in the v4.0.0rc1 UI. |

Recommended constraints:

- `unique(species_id)`.
- Check each 0-10 scale column is between 0 and 10.
- Check pH values are between 0.0 and 14.0.
- Check USDA hardiness zones are between 1 and 13.
- Check every min/max pair is ordered when both values are present.
- Check enum/string columns use only the approved values.

Recommended indexes:

- Unique index on `species_id`.
- Individual indexes on searchable min/max columns that are likely to be used
  often: light, soil moisture, pH, temperature, hardiness zone.

### Controlled Lookup Tables

Use category-specific lookup tables instead of one generic term table. This
adds more tables, but it gives clearer foreign keys and prevents linking a soil
type where a duration term is expected.

Each lookup table has the same shape:

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | integer primary key | no | Autoincrement primary key. |
| `code` | unicode(40) | no | Stable ASCII code used in import/export/search. |
| `label` | unicode(80) | no | Human-readable label. |
| `description` | unicode text | yes | Optional help text. |
| `sort_order` | integer | no | UI order. |
| `active` | boolean | no | Defaults true; allows hiding old terms without data loss. |

Recommended constraints:

- `unique(code)` for each lookup table.

Lookup tables and initial values:

| Table | Codes |
| --- | --- |
| `culture_duration` | `annual`, `biennial`, `perennial`, `monocarpic_perennial`, `short_lived_perennial` |
| `culture_sunlight` | `full_shade`, `part_shade`, `part_sun`, `full_sun` |
| `culture_soil_drainage` | `poor`, `moderate`, `well_drained`, `sharply_drained` |
| `culture_soil_type` | `clay`, `loam`, `sand`, `gravel`, `rock`, `organic`, `bark`, `aquatic` |
| `culture_recommended_propagation` | `seed`, `cutting`, `division`, `grafting`, `layering`, `offsets`, `spores`, `tissue_culture` |
| `culture_environment` | `outdoor`, `indoor`, `cool_greenhouse`, `warm_greenhouse`, `hot_house`, `seasonal_protection` |

### Category-Specific Join Tables

Each join table links a species culture profile to values from exactly one
lookup table.

| Join table | Columns |
| --- | --- |
| `species_culture_profile_duration` | `profile_id`, `duration_id` |
| `species_culture_profile_sunlight` | `profile_id`, `sunlight_id` |
| `species_culture_profile_soil_drainage` | `profile_id`, `soil_drainage_id` |
| `species_culture_profile_soil_type` | `profile_id`, `soil_type_id` |
| `species_culture_profile_recommended_propagation` | `profile_id`, `recommended_propagation_id` |
| `species_culture_profile_environment` | `profile_id`, `environment_id` |

Recommended constraints and indexes:

- Composite primary key or unique constraint on each pair of IDs.
- Index the lookup-side foreign key in each join table for reverse searches,
  such as all profiles marked `full_sun`.

### `species_culture_profile_month`

Stores month sets without comma-separated text or bitmask encoding.

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | integer primary key | no | Standard Ghini row ID. |
| `profile_id` | integer foreign key | no | References `species_culture_profile.id`. |
| `month_type` | enum/string | no | `growth`, `bloom`, `fruit`, `pruning`. |
| `month` | small integer | no | 1-12. |

Recommended constraints and indexes:

- Unique constraint on `(profile_id, month_type, month)`.
- Check `month between 1 and 12`.
- Check `month_type` is one of `growth`, `bloom`, `fruit`, `pruning`.
- Index on `(month_type, month)` for searches such as species blooming in May.

### Relationship Summary

- `Species` one-to-zero-or-one `SpeciesCultureProfile`.
- `SpeciesCultureProfile` many-to-many duration, sunlight, soil drainage, soil
  type, recommended propagation, and culture environment lookup rows through
  category-specific join tables.
- `SpeciesCultureProfile` one-to-many `SpeciesCultureProfileMonth`.

Deletion behavior should follow Ghini's existing ORM style:

- Deleting a species deletes its culture profile.
- Deleting a culture profile deletes its lookup links and month rows.
- Controlled culture lookup rows should not be deleted while referenced.

### Database Upgrade Behavior

The initial implementation adds only the database model and controlled lookup
defaults. Existing Ghini databases are upgraded when the Plants plugin starts:
missing culture tables are created with SQLAlchemy `create_all(checkfirst=True)`,
and missing lookup rows are inserted by `code`.

The startup upgrade intentionally does not run the general default CSV importer
against existing databases. That importer is still used for full database
creation, but it can drop and recreate data during forced imports. For culture
lookup defaults, the startup path is additive and preserves any local edits to
existing lookup labels or descriptions.

### Why Not Store Lists In Text Fields?

Text lists would be simpler to add but would make search, import/export, and
PostgreSQL/SQLite consistency weaker. The join-table approach lets Ghini answer
questions such as "show full-sun perennials that tolerate dry soil" without
string parsing.

## First Implementation Boundary

The approved implementation boundary was:

1. Add model and defaults for controlled values.
2. Add tests for SQLite and PostgreSQL schema behavior.
3. Add Species Editor Culture tab with compact grouped controls.
4. Add result-detail display for selected species.
5. Add guided and automated GUI coverage for save/reopen/search.

Do not add API integrations or import/export in the first implementation. The
model should be compatible with later provider mappings from Trefle, Perenual,
or another source if that becomes useful, but all data entry should be manual
for #465.
