# Power BI Model Glossary — Common Phrases & KPI Definitions

Companion to [`00_START_HERE.md`](00_START_HERE.md) through [`06_external_misc.md`](06_external_misc.md), which document the raw SQL schema (`std`/`ref`). This file documents the **business/reporting layer** built on top of it: the semantic model in Power BI (Model name: `Model`, 87 tables, 324 measures, 79 calculated columns, 47 Power Query table loads).

Source: `PowerBI_Model_Dictionary.md` (generated 2026-08-26 via Tabular Editor C# script, from `C:\Users\Alban Ssonko\Downloads\extract_model_dictionary (2).csx`), which pulls DAX/M directly from the live model — treat that file's formulas as authoritative when this glossary and the raw DAX ever disagree.

**Status: complete pass (2026-08-26).** All 324 measures, all 79 calculated columns, and all 47 Power Query M table-load definitions have been read. See the "Coverage note" near the end of this file for exactly what got deep-dived vs. lineage-only, and the small list of genuinely open items (an orphaned `Total Crashes` reference that needs Power BI Desktop to resolve, and a couple of lower-traffic queries not transcribed line-by-line). This pass also found and fixed a real gap from the first pass: `EPM`/`actual_trip_fare` don't exist as SQL columns anywhere (they're computed in Power Query), which caused a live query failure before this file explained why — see the warning section immediately below.

---

## ✅ SQL views now exist for the Power-Query-only logic below — query these directly, don't recompute

**Created 2026-08-26**, so the formulas below are queryable from any device via the same read-only `mssql` connector, not dependent on this glossary being loaded as local context. All three are plain views (`SELECT` only needed, `db_datareader` already covers them) — additive, don't touch any table Power BI depends on, and are trivially reversible (`DROP VIEW`) if anything about them needs revisiting:

| View | Wraps | Adds |
|---|---|---|
| **`rpt.vw_driver_trip_activity`** | `rpt.DriverTripActivity` | `EPM`, `actual_trip_fare` |
| **`rpt.vw_all_drivers_enriched`** | `dbo.vw_all_drivers` + `dbo.test_punches` + `rpt.DriverTripActivity` + `raw.paylocity_car_seat_trained_drivers` | `[Locations]` (Mission/Douglas mapping), `[Last Active Date]`, `[Last Active Minus Terminated At]` (the ghosting formula), `[Veteran Status]`, `[Hire Type]`, `[Length of Service (Days)]`, `car_seat_active` |
| **`rpt.vw_uber_ev_driver_activity_enriched`** | `std.uber_ev_driver_activity` + `audit.vw_driver_shifts` | `[Hours On Trip]`/`[Hours Online]` parsed to decimal (base table stores them as `'DD:HH:MM'` text), `dispatch_type` (`Re-dispatched`/`Regular`, via the AM/PM-cycle shift logic) |
| **`rpt.vw_uber_ev_driver_payments_enriched`** | `std.uber_ev_driver_payments` | `[Actual Net Fare]` (the date-dependent methodology switch at 2025-12-01), `[Pay Date]`, excludes the dummy driver UUID `9b63e6e2-16f8-4224-9d77-fd731eb51fec` |

**Deliberately NOT built as views** (scope decision, not an oversight):
- The **`Summary`** weekly-attrition table's own DAX has literal `-- adjust column names if needed` developer comments — replicating unverified logic into a new "official" SQL view would enshrine something the model's own author didn't finish trusting. Use `rpt.vw_all_drivers_enriched` (backing the confirmed-accurate `real turnover rate` metric) for turnover analysis instead.
- **`Vehicle Inventory Status`/`Vehicle Status Change`** (OOS day-tracking) — very complex recursive CTEs, and rebuilding them properly means fixing the `fleetio_all_vehicles` bare-reference bug (see `00_START_HERE.md`) at the same time, not bundling a bug-for-bug replica. Flagged as a larger follow-up, not done here.

**⚠️ Performance note on `rpt.vw_uber_ev_driver_activity_enriched`:** unlike the Power BI M query it's based on (which always filters by a `RangeStart`/`RangeEnd` date parameter), this view has **no date bound** — the `dispatch_type` redispatch logic scans all of `audit.vw_driver_shifts` and groups by driver/date across full history before any filter you add gets applied. A `SELECT TOP 5` against it took a couple of minutes during testing (2026-08-26, 506K rows). **Always add a `WHERE [Date] >= ...` predicate when querying this one** — the other three views are fine unfiltered.

**Note on `'All Drivers'`'s scope:** `rpt.vw_all_drivers_enriched` inherits the EV-only scope from `dbo.vw_all_drivers` (confirmed: EV fleet only, WAV/AV not yet included), but **deliberately does NOT apply Power BI's additional San Francisco exclusion** (`WHERE [Location] <> '200SFO0101'`) — the view shows all EV locations including SFO, which is *more* complete than the Power BI table it's based on. If you want the exact same population Power BI reports on, add that filter yourself; if you want the true full EV picture, this view already gives you that.

---

## ⚠️ Power BI table/column names do not always map 1:1 to SQL — read this before querying via the MCP connector

**Found 2026-08-26, after a real failure:** Claude tried to find a column called `EPM` and couldn't, because the glossary referenced `'Uber Trip Activity'[EPM]` from DAX without clarifying that neither the Power BI table name nor that column exist in SQL the way the name suggests. Two distinct traps, both apply here:

**1. The Power BI table `'Uber Trip Activity'` does NOT source from `std.uber_ev_trip_activity`.** Its Power Query M (line ~6999 of the model dictionary export) actually queries **`rpt.DriverTripActivity`** — a different table entirely, richer than the raw trip table. Lineage, confirmed against the live DB and the `dbo.Update_DriverTripActivity` stored procedure that populates it:

```
std.uber_ev_trip_activity  ──┐
                              ├─▶  rpt.DriverTripActivity  ──▶  Power BI 'Uber Trip Activity'
std.uber_ev_driver_transactions ─┘   (via dbo.Update_DriverTripActivity,
                                       incremental: 3-day lookback, full
                                       3-day rebuild at midnight)
```

`rpt.DriverTripActivity` (6M+ rows, updates continuously — confirmed current to today) adds, beyond what's in `std.uber_ev_trip_activity`:
- **`total_paid_to_you`, `total_your_earnings`, `total_tip`** — summed per trip from `std.uber_ev_driver_transactions` (a table not otherwise part of the trip-activity family)
- **`shift_id`, `shift_start_time`, `shift_end_time`, `trip_start_flag`, `trip_end_flag`** — a shift is inferred, not stored anywhere upstream: a new shift starts whenever the gap since the driver's previous trip drop-off exceeds **4 hours**. This 4-hour-gap rule is the actual definition of "shift" used throughout the Power BI grading/attendance measures that reference trip-derived shift times — not the same thing as a Paylocity scheduled shift (`std.paylocity_ev_shift_unified`).
- **`assigned_date`** — the trip's drop-off time (or request time if never completed) shifted back 4 hours before taking the date, so a trip just after midnight still counts toward the previous day's shift

**2. `EPM` and `actual_trip_fare` are not stored anywhere in SQL — not in `std`, not in `rpt`.** They're computed fresh, in the `'Uber Trip Activity'` Power Query M step itself, every time the model refreshes:

```sql
-- EPM (earnings per mile)
CASE
    WHEN trip_distance = 0 OR trip_distance IS NULL THEN 0
    ELSE (total_paid_to_you - total_tip) / trip_distance
END AS EPM

-- actual_trip_fare (normalizes a magnitude/scaling data-quality issue in total_paid_to_you —
-- some values come through scaled up by a power of 10; this brings them back to a 2-digit integer part)
CASE
    WHEN LEN(CAST(FLOOR(ABS(total_paid_to_you)) AS varchar)) > 2
    THEN total_paid_to_you / POWER(10.0, LEN(CAST(FLOOR(ABS(total_paid_to_you)) AS varchar)) - 2)
    ELSE total_paid_to_you
END AS actual_trip_fare
```

**So: to get EPM via the MCP connector, query `rpt.DriverTripActivity` and apply the `CASE` expression above — there is no `EPM` column to `SELECT` anywhere.** This is a real gap, not a one-off — assume any DAX-referenced `'TableName'[column]` might be M-query-computed (like this) or a DAX calculated column (the 79 Calculated Columns section is still unreviewed — see Open Items) rather than a literal SQL column, and verify before querying live.

## The driver grading system

The model's central pattern: four raw KPIs, each turned into a per-driver A/B/C/D letter grade against thresholds from a `Grading Targets` table, then rolled up into grade-distribution counts and percentages. All grading measures key off **`'All Drivers'[Uber Unique ID]`** — `COALESCE(custom_Uber_ID, employeeId as text)`, defined in the `dbo.vw_all_drivers` view (verified 2026-08-26: despite living in `dbo`, this view correctly queries `std.paylocity_ev_employees_detail`/`std.paylocity_ev_punches`/`std.uber_ev_driver_activity` — not a victim of the stale-shadow-table issue documented in `00_START_HERE.md`).

| Abbrev. | Full meaning | Raw formula | Grade direction |
|---|---|---|---|
| **AR** | Acceptance Rate | `AVERAGE('Uber Driver Quality'[acceptance_rate])` where `trips_completed > 0` | Higher = better (A = highest) |
| **CR** | Cancellation Rate | `AVERAGE('Uber Driver Quality'[cancellation_rate])` | Lower = better (A = lowest) |
| **EPH** | Earnings Per Hour | `[Net Earnings] / [Uber Hours Online]` — "No tips" variant nets out tips via `Actual Net Fare` | Higher = better |
| **UR** | **Driver (star) Rating** — *not* "Utilization Rate*, despite the name | `AVERAGE('Uber Driver Quality'[driver_ratings_last_4_weeks])` where `trips_completed > 0` | Higher = better, graded on a tight band (A ≤ 5.0, B ≤ 4.9, C ≤ 4.8, D otherwise) |

`AR`/`CR`/`EPH`/`UR` each have a matching `[Selected * Grade A/B/C/D]` threshold measure and a `Grading Targets` table row (indexed by a numeric `KPI` code seen in the DAX: EPH=1, Gap Time=2, Attendance=4, UR=8 — looks bit-flag-shaped; AR/CR's codes weren't confirmed in this pass). Each KPI also has:
- **`(A) <KPI>` / `(B) <KPI>` / `(C) <KPI>` / `(D) <KPI>`** — count of drivers falling in that grade band
- **`% A <KPI>` / `% B <KPI>` / etc.** — that count ÷ total distinct drivers
- **`<KPI> Grade`** — the per-driver letter itself (used for row-level grade lookup/coloring)
- **`Count of A/B/C/D Grades`** and **`% (Grade A/B/C/D) Drivers`** — same pattern applied to **`Overall Grade`** (a composite across all four KPIs — not yet reviewed in detail this pass)

`EPH (No tips)` and `EPH (Uber)` are two distinct, intentionally-both-kept definitions (confirmed 2026-08-26) — but not parallel/equal-status metrics: **`EPH (No tips)` is the company's actual metric** (feeds `EPH Grade` and the grading system) — tips are excluded because they're the driver's, not revenue Tower measures performance against. **`EPH (Uber)`** (raw `TotalEarnings`, tips included) exists purely as a **reconciliation check** — Uber's own platform-reported EPH includes tips and Uber doesn't expose a tips-excluded breakdown, so this measure lets Tower verify its own EPH calculation against Uber's reported total rather than being used as a metric in its own right. Don't collapse these into one, and don't treat `EPH (Uber)` as an alternate "official" EPH.

## Gap Time family

"Gap time" = the difference between hours an employee is clocked in (Paylocity) and hours they're actually online in Uber — i.e., paid time not spent working trips.

- **`Total Hours Punched`** — from Paylocity punches
- **`Uber Hours Online`** — `SUM('Uber Driver Activity'[Hours Online])`
- **`Gap Hours`** — `Punched − Online` (blanked out for March 2025 specifically — a hardcoded date exclusion in the DAX, likely a known bad-data period)
- **`% Gap Time`** — `Gap Hours ÷ Total Hours Punched`
- **`Gap Time Grade`** — A–D banding of `% Gap Time` (lower gap = better grade; defaults to "D" if `Uber Hours Online` = 0)
- **`Gap time Variance`** — `Gap Hours − (12% × Total Hours Punched)` — deviation from a 12%-acceptable-gap baseline
- **`Gap time Variance ($)`** — variance dollarized at a flat **$18/hour** rate (hardcoded in the DAX)
- **`Gaptime P/driver`** — `Gap Hours ÷ hours_per_driver`

Naming is inconsistent across this family (`Gap Time` / `Gap Hours` / `Gaptime` all appear) — that's the model's existing convention, not something to "fix" without being asked.

## Attendance family

- **`Attendance %`** (in `_scheduling_measures`, not yet fully reviewed)
- **`Actual Attendance`** — `COUNT('Paylocity Punches'[employeeId])`
- **`Attendance Target`** — scheduled headcount minus explicitly-off headcount (`schedule-paylocity` minus `schedule-paylocity (off)`), floored at 0
- **`Attendance Grade`** — A–D banding of `Attendance %`, defaults to "A" if blank
- **`Days not Attended`** — no-show count from `schedule-paylocity[Show/No Show]`, net of scheduled days off
- Same `(A)/(B)/(C)/(D) Attendance` and `% A/B/C/D Attendance` pattern as the KPI grades above

## Turnover / Termination cluster

Five related measures — **confirmed with the user 2026-08-26**, resolving what initially looked like duplicates:

- **`terminated_paylocity(Turn Over)`** — the headline number, **all terminated employees, unaffected by any report date-slicer** (its `TREATAS` filters against `'All Drivers'[Termination Date]` itself rather than the report's `Date_table`, so it doesn't respond to date-range filters the way the other two do).
- **`terminated_paylocity`** — same distinct-count logic, but filtered via `TREATAS(VALUES(Date_table[Date]), ...)`, so **this one *does* respect whatever date range is selected** on the report page. Used as a building block elsewhere (e.g. `hired_paylocity − terminated_paylocity` for a churn variant).
- **`terminated_paylocity(recently available)`** — same as `terminated_paylocity`, plus a "not ghosted" filter (`Last Active Minus Terminated At <= 21` days, not blank).
- **`turnover_recently_active_drivers`** — the "real" attrition-event count: DVR position code only, has a termination date, **and** was still active within 21 days of that termination (i.e., excludes people who'd already effectively stopped showing up long before the formal termination was processed — "ghosted" drivers).
- **`Active Drivers Turnover (Termination Axis)`** — the eligible driver population for the denominator: DVR drivers whose employment span overlapped the current termination-date filter window, **minus** the ghosted-termination count (`terminated_paylocity(Turn Over) − turnover_recently_active_drivers`) — so ghosted terminations are excluded from both numerator and denominator.
- **`real turnover rate`** — `turnover_recently_active_drivers ÷ Active Drivers Turnover (Termination Axis)` — the headline turnover rate, deliberately excluding ghosted-then-terminated drivers from both sides of the ratio so they don't distort it either direction.

**In short: `(Turn Over)` = raw/total, unfiltered by date. `real turnover rate` = the metric that actually matters for reporting, purpose-built to exclude ghost terminations.**

## Safety / Accidents / Incidents / Violations cluster

**Clarified 2026-08-26 (corrects the initial pass):** two genuinely distinct *sources*, but the terminology pairs within each are synonyms, not distinct sub-concepts:

- **"Accident" = "Collision"** — same thing. Both refer to `Accident Data` rows: a physical vehicle-to-something collision that actually occurred. Human-logged, one row per event, with fault determination and collision-type detail (Front/Rear/etc.).
- **"Incident" = "Violation"** — same thing. Both refer to `Safety Violations` (Samsara telematics) rows: **the broader, catch-all bucket of unsafe/notable driving behavior Samsara's hardware detects in real time** — not just soft-coaching events. This includes things like running a red light, speeding, and harsh driving behaviors, *and can include a crash/collision as detected by Samsara's own sensors* as one event type among many — separate from, and not automatically reconciled with, the human-filed `Accident Data` report for the same physical event. So a single real-world crash could plausibly generate both an `Accident Data` row (filed by a person) and a `Safety Violations` row (auto-detected by telematics) — they're two independent logs of overlapping-but-not-identical scope, not a strict subset/superset relationship.

**`Accident Data`** (= `rpt.vw_accident_data`, the same table the Collision-Type Front/Rear classifier was built for):
- **`Total Accidents`** — `COUNT('Accident Data'[Vehicle Number])`
- **`Collisions`** — `COUNT('Accident Data'[Collision Type])` — same concept as `Total Accidents`, counted via a different column; treat as synonyms unless the two columns can diverge (e.g. a row missing `Collision Type` but present in `Vehicle Number`)
- **`at_fault`** / **`AF Accidents`** — count where `At Fault = "Yes"`
- **`NAF Accidents`** — count where `At Fault = "No"`
- **`Daily Average Accidents`**, **`Weekly Average Accidents`** — straightforward date/week-bucketed averages
- **`AverageDailyIncidents`**, **`AverageDailylyIncidentsAtFault`** (note: typo "Dailyly" is in the actual measure name), **`AverageDailylyIncidentsNoAtFault`**, **`AverageWeeklyIncidentsNotAtFault`**, **`LowestAverageWeeklyIncidents`** — despite the "Incidents" naming, these all slice `Accident Data[Collision Type]` (i.e. they're accident/collision measures misnamed with "Incidents" — a naming inconsistency in the model itself, not a sign they pull from `Safety Violations`), by fault/day/week, restricted to `YEAR('Date') >= 2025`
- **`Accidents per 30k miles`** — `(Total Crashes ÷ Miles Driven) × 30,000`. **⚠ `Total Crashes` is referenced here and in `Driver Rank` but has no measure definition anywhere in the model file — likely an orphaned reference to a renamed or deleted measure. Worth checking in Power BI Desktop directly (this would show as a DAX error in the model, not something visible from the exported dictionary alone).**

**`Safety Violations`** (Samsara telematics — matches `ref.samsara_ev_safety_events` in the SQL layer) — `[Event Type]` values referenced in the `Safety KPI Avg` formula: "no seat belt", "harsh brake", "rolling stop", "inattentive driving", "obstructed" (view), "smoking" — **per the 2026-08-26 clarification, the full `Event Type` vocabulary is broader than these six** (also includes things like red-light/speeding/crash-type events); those six are just the ones this particular weighted-scoring formula assigns a penalty to, not the complete list of what `Incidents`/`Violations` counts:
- **`Incidents`** — `DISTINCTCOUNT('Safety Violations'[Safety Events ID])`
- **`Total Incidents`** — `COUNT('Safety Violations'[Event Type])` — same concept as `Incidents`/`Violations`, counted via a different column (COUNT vs DISTINCTCOUNT, `Event Type` vs `Safety Events ID`) — treat as synonyms unless a single Safety Events ID can carry multiple Event Type rows, which would make them diverge
- **`Total Violations`** — literally `[Incidents]` (a pure alias, not a separate definition) — consistent with Incidents=Violations being the same concept
- **`Incidents per 1k miles`** — `(Incidents ÷ Miles Driven) × 1,000`
- **`Action`** — business rule: `IF([Incidents] > 2, "Suspension", "Coach")` — the threshold that turns raw incident/violation counts into an HR/safety action recommendation
- **`Safety KPI Avg`** — a weighted composite safety score per location: starts at 100, subtracts `count(violation type) × weight` for each of the six Event Types listed above (weights pulled from a `Target Saftey` table [sic — typo in the actual table name, not fixed here] indexed 2–7), then caps the result at 85 if there's been any at-fault accident (`at_fault > 0`, i.e. from `Accident Data`) in the current filter context — note this formula deliberately only penalizes those six behavior types, not every `Event Type` value that exists
- **`Safety KPI_Target`** — the target line itself, `Target Saftey[Index] = 1`

---

## Fleet / vehicle status terms (`_fleetio` measure folder)

Vehicle status values seen across measures (from `'fleetio-vehicle-export'[vehicle_status_name]`, i.e. `std.fleetio_all_vehicles` — see `03_fleet_vehicles.md`): `Road Ready`, `Biohazard`, `Out of service`. Separately, `'Vehicle Status Change'` table uses **`Active`**/**`OSS`** as its own from/to status values — **not yet confirmed whether `OSS` = `Out of service` and `Active` = `Road Ready` are the same underlying states under different labels, or a genuinely separate status vocabulary** tracked by whatever populates `Vehicle Status Change`. Worth a targeted question if this table gets used for anything beyond the `Active to OOS Count`/`OOS to Active Count` transition-counting measures.

- **`Total Vehicles (Fleetio)`** / **`Purchased Vehicles`** — **confirmed duplicates (2026-08-26)**: both `DISTINCTCOUNT(license_plate)`, same meaning under two names. `Total Vehicles (Fleetio)` is the one other measures reference (e.g. `Road Ready + Biohazard`, `Actual Assigned - Target`), so treat it as canonical; `Purchased Vehicles` as the alias.
- **`Road Ready`**, **`Biohazard`**, **`Road Ready + Biohazard`** — vehicle counts filtered to those specific status values
- **`Road Ready`** / **`Active Vehicles`** — **confirmed duplicates (2026-08-26)**: both filter `Total Vehicles (Fleetio)`/`Purchased Vehicles` to `vehicle_status_name = "Road Ready"`. `Road Ready` is the shorter name and the one composed into other measures (`Road Ready + Biohazard`, `road_ready - dispatch_target`); treat it as canonical.
- **`Percentage Active`** — `Active Vehicles ÷ Purchased Vehicles`
- **`Avg_MTTR_work_orders`** — Mean Time To Repair, in days: total OOS hours on completed work orders ÷ completed work order count ÷ 24
- **`Overall Car Score`** — average of `(exterior_score + interior_score) / 2` from `fleetio_inspections`

**`Vehicle Status Change`'s `Active`/`OSS` vocabulary, resolved (2026-08-26, moderate confidence):** these come from a different source than `fleetio_all_vehicles.vehicle_status_name` — specifically `rpt.vehicle_status_shift`, a status-transition log with only `from_vehicle_status_id`/`to_vehicle_status_id` values `Active`/`OSS`. This looks like a simplified binary bucketing (OOS-type statuses collapsed into one `OSS` value) rather than the full `Road Ready`/`Out of Service`/`Biohazard`/etc. vocabulary on `fleetio_all_vehicles` — but what populates `rpt.vehicle_status_shift` and maps the richer statuses down to two buckets wasn't traced this pass. Treat `OSS` ≈ "any out-of-service-type status" until confirmed further.

---

## ⚠️ Confirmed: the `dbo` shadow-table bug also lives inside the Power BI model itself, not just Python scripts

Found 2026-08-26 by reading all 47 Power Query M table-load definitions. Three Power BI tables — **`Samsara Vehicles`**, **`Vehicle Inventory Status`**, **`Vehicle Status Change`** — all reference bare, unqualified `fleetio_all_vehicles` in their M-embedded SQL. Per `00_START_HERE.md`, that resolves to `dbo.fleetio_all_vehicles` (676 vehicles), not `std.fleetio_all_vehicles` (851) — meaning these three tables (and everything built on `Vehicle Inventory Status`/`Vehicle Status Change`, including the entire OOS-day-tracking `Report Rows` layer below) silently exclude ~175 vehicles' worth of status history. This is a live model bug, not just a documentation gap — fixing it means editing the M query in Power Query Editor (add `std.` in front of `fleetio_all_vehicles` in all three), not something fixable from this glossary alone.

A fourth: **`return_table`** (backing the `Dead Distance_%` measure) references bare `vw_daily_driver_activity`, resolving to `dbo.vw_daily_driver_activity` (291,591 rows) instead of `ref.vw_daily_driver_activity` (364,814 rows) — same bug class, added to the table in `00_START_HERE.md`.

Every other bare/unqualified reference found across the 47 M queries was checked individually and confirmed to have **no** `std`/`ref` counterpart at all — i.e. legitimately `dbo`-only, not a bug: `samsara_vehicle`, `vw_samsara_assets_location_unique`, `vw_all_drivers` (verified clean separately), `vw_ev_daily_dispatch`, `vw_fleetio_inspections_carwash`, `vw_vehicles_ancestry`, `vw_paylocity_ev_shift_unified_pacific`, `samsara_driver`, `uber_payment_orders_new`, `dbo.uber_all_drivers`, `dbo.vehicle_snapshot`, `dbo.fleetio_ev_work_orders`. `dbo.uber_ev_auto_pos` and `std.uber_ev_auto_pos` were checked and are in sync (identical row counts) — redundant but not wrong. `kpi_grading` exists in both `dbo` and `stg` with identical row counts (32 rows, a small config table) — also not a divergence issue.

## `'All Drivers'` — full lineage (the single most heavily-referenced table in the model)

Traced 2026-08-26 from its M query. Source: `vw_all_drivers` (bare — resolves to `dbo.vw_all_drivers`, already verified clean/current), enriched with three more joins:

- **`dbo.test_punches`** (alarming name, but verified legitimate — see `_regenerate.md`-adjacent investigation notes below) → `[Last Punch Date]`, `[Last Hours Online Date]`
- **`rpt.DriverTripActivity`** → `[Last Trip Date]` (max trip drop-off per driver)
- **`std.paylocity_ev_shift_unified`** → current/upcoming scheduled shift, via a priority-ordered pick (this week > next week > most-recent-past for active drivers; most-recent-relative-to-termination for terminated ones)
- **`raw.paylocity_car_seat_trained_drivers`** → `car_seat_active` Yes/No flag

**`dbo.test_punches` lineage (verified, not actually test data):** despite the name, this is a legitimate, current, TRUNCATE-and-reload materialized cache — `dbo.usp_refresh_test_punches` runs `TRUNCATE TABLE dbo.test_punches; INSERT INTO dbo.test_punches SELECT * FROM dbo.vw_paylocity_ev_punches`, and that view correctly sources `std.Paylocity_ev_Punches`/`std.paylocity_ev_shift_unified` with a punch-interval-merging algorithm (adjacent punches with no gap get merged into one continuous work block) and computes `[Hours Variance]` (actual vs. scheduled hours). Confirmed current through today (338K+ rows). The name is just poorly chosen, not a sign of stale/fake data — but if a `std`-only equivalent ever gets built, prefer it and flag `dbo.test_punches` for cleanup.

**⚠️ `'All Drivers'` is a misleading name — despite it, this table is EV-only.** Confirmed with the user 2026-08-26: it's **all and only EV drivers, for now** (not WAV, not AV) — consistent with its source view only joining `std.paylocity_ev_employees_detail`/`std.paylocity_ev_punches`/`std.uber_ev_driver_activity`, never any WAV/AV table. "For now" implies this is a known, intentional current scope rather than a bug — WAV/AV may be added later, but as of this writing every measure built on `'All Drivers'` (essentially the entire grading/turnover/attendance system) reports on EV only, with nothing in the measure names to signal that.

On top of the EV-only scope, the query's final `WHERE` clause also excludes San Francisco specifically: `AND d.[Location] <> '200SFO0101'`. So the true scope of `'All Drivers'` and everything built on it is **EV fleet, minus San Francisco** — not "all drivers," not even "all EV drivers."

**Exact formulas for columns referenced throughout the grading/turnover measures but not stored in any single SQL table:**
```sql
-- [Last Active Date]: most recent of trip/punch/online-hours activity, in priority order
CASE
    WHEN [Last Trip Date] IS NOT NULL
     AND [Last Trip Date] >= ISNULL([Last Punch Date], '1900-01-01')
     AND [Last Trip Date] >= ISNULL([Last Hours Online Date], '1900-01-01')
    THEN [Last Trip Date]
    WHEN [Last Punch Date] IS NOT NULL
     AND [Last Punch Date] >= ISNULL([Last Hours Online Date], '1900-01-01')
    THEN [Last Punch Date]
    WHEN [Last Hours Online Date] IS NOT NULL THEN [Last Hours Online Date]
    ELSE NULL
END

-- [Last Active Minus Terminated At]: the "ghosting" metric behind the whole turnover cluster
CASE
    WHEN [Last Active Date] IS NULL OR [Termination Date] IS NULL THEN 0
    WHEN ([Termination Date] > latest_hire_date OR [Last Active Date] < CAST([Termination Date] AS date))
    THEN DATEDIFF(DAY, [Last Active Date], [Termination Date])
    ELSE 0
END

-- [Veteran Status]: tenure bucketing
CASE
    WHEN [Hire Date] IS NULL THEN NULL
    WHEN DATEDIFF(DAY, [Hire Date], GETDATE()) < 14 THEN 'New Driver'
    WHEN DATEDIFF(DAY, [Hire Date], GETDATE()) < 30 THEN 'Somewhat New'
    ELSE 'Veteran'
END

-- [Hire Type]
CASE WHEN [Rehire Date] > [Hire Date] THEN 'Re-hire' ELSE 'New Hire' END

-- [Locations] (matches the Mission/Douglas cost-center mapping in 00_START_HERE.md, confirms it)
CASE
    WHEN [Location] = '200LAX0103' THEN 'Mission'
    WHEN [Location] = '200LAX0104' THEN 'Douglas'
    ELSE [Location Name]
END
```

## Two different "shift" concepts — don't conflate them

"Shift" means two genuinely different things depending which measure you're looking at:

1. **Trip-gap shifts** (`rpt.DriverTripActivity`, feeds `Uber Trip Activity`): a new shift starts whenever the gap since the driver's last trip drop-off exceeds **4 hours**. Purely inferred from trip timestamps.
2. **AM/PM cycle shifts** (`audit.vw_driver_shifts`, feeds `Uber Driver Activity`'s `dispatch_type`): a fixed daily cycle — login between 04:00–14:59 = `AM`, 15:00–03:59 = `PM` (a pre-4am login counts toward the *previous* day's PM shift). Used specifically to detect **`dispatch_type = 'Re-dispatched'`**: a driver assigned to a second (or later) vehicle within the same AM/PM cycle.

These are not interchangeable, and neither matches Paylocity's own scheduled shifts (`std.paylocity_ev_shift_unified`) — three distinct "shift" definitions coexist in this system depending which table you're near.

## `Uber Driver Payments` — a mid-year fare methodology change

`[Actual Net Fare]` is not computed the same way across all dates:
```sql
CASE
    WHEN TRY_CAST(StartTime AS date) < '2025-12-01' THEN ISNULL(NetFare, 0)
    ELSE ISNULL(TotalEarnings, 0) - ISNULL(Tip, 0) + ISNULL(RefundsAndExpenses, 0)
END
```
Anything before December 2025 uses the raw `NetFare` field; from Dec 1 2025 onward it's computed from `TotalEarnings`/`Tip`/`RefundsAndExpenses` instead. **Comparing net-fare figures across that boundary without accounting for the methodology change will produce a misleading trend.** Also: driver UUID `9b63e6e2-16f8-4224-9d77-fd731eb51fec` is explicitly excluded from this table (likely a shared/test/dummy Uber account — the same UUID appears as the supplier-portal org ID in `alert_operations.py`'s link-building code, worth reconciling if it matters). `[Pay Date]` = the Monday starting the `StartTime`'s week, plus 11 days (an ~11-day payment-lag convention).

## `Report Rows` — three measures are unimplemented stubs

`Funding ACH`, `Funding Credit Card`, and `Funding Needed` are all literally `BLANK() /* TODO: source not yet identified */` in the live model — they will always render blank/zero wherever used, not because of missing data but because they were never built. If a report appears to show $0 funding needed, this is why. Separately, `OOS Glass` filters `vendor_type = "Mobile Mechanic"` and `OOS Mechanical` filters `vendor_type = "Repair Shop"` — the measure names don't match their filter values, which could confuse whoever's maintaining this later.

## `Summary` table — a second, less-verified turnover/attrition layer

Distinct from the `terminated_paylocity*`/`turnover_recently_active_drivers` cluster documented above, the `Summary` measure group (`Active Drivers (Daily)`, `Average Daily Attrition`, `Net Attrition %`, `Cumulative Net Hire`, `Total Hired`/`Total Terminated`) works off a **calculated table** called `Summary`, pre-aggregated by Location + Date. Its `Hired` and `Terminated` calculated columns contain literal developer comments — `-- adjust column names if needed` / `-- adjust column names as needed` — suggesting this layer may not be fully verified. `Terminated` also joins against a `'Terminations - EV'` table (separate from `'All Drivers'`) on `[Termination Date] = Summary[Date]`, while `Terminated by Driver Activity` joins `'All Drivers'` on `[Last Active Date] = Summary[Date]` instead — two different date bases for what sound like similar "terminated" concepts. **If weekly attrition numbers from this layer disagree with the driver-level `real turnover rate`, trust the driver-level one** (it's been directly confirmed with the user; this one hasn't).

## `zeem` — EV battery health tracking

Sources from `vw_zeem_battery_degradation` (bare, `dbo`-only — no `std` equivalent checked). Tracks per-vehicle battery State of Health (`state_of_health_pct`), charge session efficiency (`kwh_per_mile`/`miles_per_kwh`), and a `health_status` field with at least `Dispose`/`Plan Replacement` values feeding the `Vehicles to dispose now`/`Vehicles to plan replacement`/`Vehicles under 75% SoH` fleet-lifecycle-planning measures. Distinct from `std.charging_sessions` (documented in `06_external_misc.md`) — that one is OCPP charging-session protocol data; `zeem` is battery-health/degradation tracking, apparently a different vendor integration ("Zeem" — see `zeem_charging.py` in the repo).

---

## Coverage note

This pass reviewed: all measure display folders (`_fleetio`, `_measuresTable`, `_safety_measures`, `_scheduling_measures`, `_zeem_measures`), the Freshsales hiring-funnel measures in `Date_table`, the remaining ungrouped measure tables (`Summary`, `Report Rows`, `Vehicle Inventory Status`, `Vehicle Status Change`, `Targets`/What-If groups, etc.), the Calculated Columns section (found: 71 of 79 are unusable placeholders — "derived from calculated table" — the extraction tool didn't capture DAX-calculated-table expressions; the 8 that did have real formulas are folded into the sections above), and all 47 Power Query M table-load definitions (table/schema lineage extracted for every one; full formula-level detail captured for the highest-traffic tables — `All Drivers`, `Uber Trip Activity`, `Uber Driver Activity`, `Uber Driver Payments`, `Vehicle Inventory Status`, `Vehicle Status Change`, `fleetio_ev_work_orders`, `fleetio_inspections`).

**Genuinely still open:**
- `Total Crashes` orphaned reference (referenced by `Accidents per 30k miles` and `Driver Rank`, defined nowhere) — needs checking directly in Power BI Desktop/Tabular Editor, not resolvable from a static export
- The exact mapping of `rpt.vehicle_status_shift`'s `Active`/`OSS` values back to Fleetio's full status vocabulary — what populates that table wasn't traced
- Fully line-by-line formula detail for the lower-traffic M queries (`parking_tickets`, `Samsara Vehicles`, `samsara_trips`, `Uber Payment Orders`, `uber_teens`, `userm`, etc.) — schema/table lineage is captured for all of them, but not every WHERE-clause business rule was transcribed
6. `Vehicle Status Change`'s `Active`/`OSS` vocabulary vs. Fleetio's `Road Ready`/`Out of service` — same states or different?
