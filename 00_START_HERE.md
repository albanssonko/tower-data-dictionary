# Tower Mobility — `tower_mobility_db1` Data Dictionary

**Purpose of this document set:** give Claude (or any LLM) the business context that table/column names alone don't carry, so questions can be answered correctly on the first query instead of by trial and error. This is not a raw schema dump — the database has 503 tables across 7 schemas; only the ~109 tables analysts actually query are documented in depth (see "Schema map" below for why the rest are skipped on purpose).

Generated 2026-08-25 by introspecting the live database (`INFORMATION_SCHEMA`/`sys.*`) plus context gathered from ~190 production Python scripts in this repo (`hr_alerts_wav.py`, `alert_operations.py`, `alert_fleet.py`, and the `Updated/` and `WAV/` folders). Row counts and columns are accurate as of generation time; re-run the queries in `_regenerate.md` periodically to refresh, since this file will drift as new columns/tables are added.

## How to use this with Claude Desktop

Add this whole `data_dictionary/` folder to a **Claude Desktop Project's** knowledge, alongside the `mssql` MCP connector (read-only `svc_claude_desktop_ro` login, `db_datareader` — see chat history for setup). With both in place, ask questions in plain English; Claude cross-references this glossary against the live schema instead of guessing from column names alone.

---

## Schema map — where to look, and where NOT to

| Schema | Tables | What it is | Query it? |
|---|---|---|---|
| **std** | 68 | The cleaned, typed, actively-maintained layer. Source of truth for analysis. | **Yes — default here.** |
| **ref** | 41 | Reference/lookup data and large event-log tables (Uber driver roster, Samsara telemetry, weather, CRM). Also actively maintained. | **Yes.** |
| **rpt** | 24 tables + 13 views | Power BI-facing reporting views/rollups, pre-aggregated for dashboards. | Yes, if you specifically want a pre-built report shape. |
| **raw** | 203 | Untransformed API/vendor dumps — the landing zone before cleanup into `std`. Messy types, inconsistent casing, duplicate/near-duplicate columns. | Avoid — use the `std` equivalent. |
| **stg** | 29 | Transient staging tables used mid-pipeline. | Avoid. |
| **dbo** | 118 tables + 42 views | **Mixed bag — contains real tables AND abandoned shadow copies of `std`/`ref` tables that silently stopped updating.** See warning below. | **Verify before trusting — see below.** |
| **audit** | 20 | Change logs / audit trails. | Only if you're specifically auditing changes. |

### ⚠️ The `dbo` trap (confirmed, not theoretical)

This database's default schema for most SQL logins is `dbo`. That means **any unqualified table name** (e.g. `FROM uber_ev_trip_activity` instead of `FROM std.uber_ev_trip_activity`) silently resolves to `dbo`, not `std`. On 2026-08-24/25 this was traced as the root cause of a live production bug in `alert_operations.py`: a safety-event/trip-matching query used bare `uber_ev_trip_activity` and `paylocity_ev_employees_detail`, which resolved to `dbo` copies that had **stopped updating weeks earlier**, causing ~1,241 false "driver mismatch" alerts. Confirmed dead/stale `dbo` shadow tables (there may be more — these are just the ones checked):

| Table | `dbo` copy | `std`/`ref` copy (live) |
|---|---|---|
| `uber_ev_trip_activity` | 0 rows since 2026-07-21 | current through today |
| `paylocity_ev_employees_detail` | 6,977 rows (stale) | 8,148 rows (current) |
| `Paylocity_ev_Punches` | stale since 2026-08-07 | current through today |
| `samsara_ev_safety_events` | stale since 2026-08-07 (found while building this doc — `alert_operations.py`'s `initialize_queue()` still reads this bare reference, unfixed as of this writing) | `ref.samsara_ev_safety_events`, current through today |

**Rule of thumb: always schema-qualify. If a query (yours or an existing script) references a table without `std.`/`ref.` in front of it, verify which schema it actually hit before trusting the result — don't assume it's the live one.**

---

## Naming convention: AV / EV / WAV = three fleets

Tower Mobility operates (at least) three separate fleet business units, and most Paylocity/Uber/Samsara tables are duplicated per fleet with a suffix:

- **EV** — Electric Vehicle fleet (largest — ~8,150 employee records)
- **WAV** — Wheelchair Accessible Vehicle fleet (~2,907 employee records), legal entity seen in data as `TOWER WAV LLC` (e.g. `TOWER WAV LLC W2 - LA EV` is a specific org value used to exclude a driver subset in HR alert queries)
- **AV** — smallest fleet (~48 employee records) — likely newer/pilot-scale; documented with lower confidence since it wasn't directly exercised by scripts read this session. **`std.paylocity_av_employees_detail` and `std.paylocity_av_shift_unified` are entirely untyped (`nvarchar(max)`/`varchar(max)`)** unlike their EV/WAV counterparts — always `TRY_CAST` AV date/numeric fields, never assume they behave like EV/WAV.

A table with no fleet suffix (e.g. `std.uber_driver_trip_payments`, `std.samsara_drivers` with a `fleet` column instead) generally spans all fleets, distinguishing them via a `fleet`/`Organization`/`source_org_id` column rather than a separate table.

---

## Universal join keys

These four identifiers are how the fleet's disparate systems (Paylocity/HR, Uber, Samsara, Fleetio) connect to each other. Almost every cross-system question routes through one of these:

| Key | Found as | Links |
|---|---|---|
| **Uber driver UUID** | `custom_Uber_ID` / `custom_Uber_ID_guid` (Paylocity), `driver_uuid`/`DriverUUID`/`DriverUuid` (Uber tables, casing varies by table), `driverUuid` (`ref.uber_drivers`) | HR employee record ↔ every Uber trip/activity/payment/quality table |
| **Driver's license number** | `custom_Driver_License` (Paylocity), `licenseNumber` (`std.samsara_drivers`), `LICENSENUMBER` (`std.tower_driver_policies`) | HR employee record ↔ Samsara driver profile (used for name-mismatch/identity verification — see `get_name_mismatch_alerts()` pattern in `hr_alerts_wav.py`) ↔ Tower's own insurance policy roster |
| **License plate** | `license_plate` (most tables), `licensePlate` (Samsara tables, camelCase) | Vehicle across Fleetio, Uber trip activity, Samsara telemetry, Samsara safety events (`vehicle_name` in `ref.samsara_ev_safety_events` is actually a license plate, not a Samsara asset name) |
| **Paylocity `employeeId`** | `employeeId` (Paylocity core, punches, shift_unified), `paylocity_employee_id` (IMS, training verification) | HR employee record ↔ punches ↔ shifts ↔ IMS internal-ops directory |

**Casing/format gotcha:** the same conceptual column is spelled differently across table families that came from different source APIs — `driver_uuid` vs `DriverUUID` vs `DriverUuid`, `license_plate` vs `licensePlate`. Check the actual column list before writing a join; don't assume consistent casing.

---

## Business code glossary

**Paylocity `status_employeeStatus`** (all `std.paylocity_*_employees_detail` tables):
- `A` = Active
- `T` = Terminated
- `L` = On Leave
- `H` = On Hold

**Paylocity `departmentPosition_positionCode`** (observed values):
- `DVR` = Driver
- `OC` = Operations Coordinator (dispatcher-adjacent; alert scripts check who's "on shift" by position code + cost center + active shift)
- `ITS` = IT Services staff — **note: IT staff records only exist in the EV Paylocity table regardless of which fleet they actually support** (a known cross-fleet quirk, not a data error)
- `HRT` / `HRA` / `HRC` = HR Team / HR Admin / HR Clerk
- `SCH` = Scheduler
- Non-driver support job titles seen excluded from driver-focused checks: `Biohazard Technician`, `Janitor`, `Car Wash Attendant`, `Administrative Assistant`

**`departmentPosition_costCenter2`** — numeric cost-center code. Two LA-specific values used to route alerts by physical location: `200LAX0103` = Mission, `200LAX0104` = Douglas. A `costCenter2` ending in `101` is used as a filter for "LA-market" drivers in some Uber-ID validation checks.

**`workAddress_location`** — human-readable site name (e.g. `Los Angeles (WAV)`, `Chicago`, `Washington DC`, `Boston`, `Portland`, `San Francisco`, `Mission`, `Douglas`, `Folsom`). Used to infer expected driver's-license state format and expected Uber org — see per-domain notes.

**Driver's license format validation** (only states actually seen in the roster are checked): CA = 1 letter + 7 digits, IL = 1 letter + 11 digits, MD = 1 letter + 12 digits (or `MD` + 11 digits), MA = 9 digits / 1 letter + 8 digits / 2 letters + 7 digits, OR = optional leading letter + 1-9 digits, DC = 7 digits, IN = 10 digits.

---

## Domain reference files

| File | Covers |
|---|---|
| [`01_hr_payroll.md`](01_hr_payroll.md) | Paylocity (AV/EV/WAV employees, payments, punches, shifts), pay/deduction code lookups, Tower's own insurance policy rosters, pre-hire training verification |
| [`02_uber_trips_drivers.md`](02_uber_trips_drivers.md) | Uber trip activity, driver activity/quality/performance/payments/transactions, Uber org & driver reference data |
| [`03_fleet_vehicles.md`](03_fleet_vehicles.md) | Fleetio (vehicles, contacts, parts, renewals), service tasks, vehicle inspections |
| [`04_telematics_safety.md`](04_telematics_safety.md) | Samsara (drivers, trips, safety events, idle time, onsite/location tracking) |
| [`05_ims_internal_ops.md`](05_ims_internal_ops.md) | IMS — Tower's internal ops/facilities/HR-ticketing platform (backup-mirrored from a MongoDB-backed app; lower-confidence documentation, not directly exercised this session) |
| [`06_external_misc.md`](06_external_misc.md) | Freshsales CRM (recruiting pipeline), mail server domains, weather data, fuel/energy & EV charging sessions, driver license compliance review (`epn_review`) |
| [`07_powerbi_glossary.md`](07_powerbi_glossary.md) | The Power BI semantic layer built on top of this SQL schema — DAX measure definitions, the driver A/B/C/D grading system (AR/CR/EPH/UR), turnover/safety/fleet-status terminology. First pass — see its "Open items" section for what's not yet covered. |

Each file lists, per table: row count, column count, primary key (if defined — 80 of 109 documented tables have one; the rest have no enforced uniqueness, so `SELECT DISTINCT`/dedup logic matters), full column list for narrow tables, and the ~20-30 most relevant columns (plus a flat name list of the rest) for wide tables — several Paylocity/Uber payment tables run 50-230 columns of mostly self-descriptive, rarely-queried fields. For the full exhaustive column list of any table, ask Claude to query `INFORMATION_SCHEMA.COLUMNS` live via the connector — that's cheap and always current, so this document deliberately doesn't try to be an exhaustive raw catalog.
