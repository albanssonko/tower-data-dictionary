# Power BI Model Glossary — Common Phrases & KPI Definitions

Companion to [`00_START_HERE.md`](00_START_HERE.md) through [`06_external_misc.md`](06_external_misc.md), which document the raw SQL schema (`std`/`ref`). This file documents the **business/reporting layer** built on top of it: the semantic model in Power BI (Model name: `Model`, 87 tables, 324 measures, 79 calculated columns, 47 Power Query table loads).

Source: `PowerBI_Model_Dictionary.md` (generated 2026-08-26 via Tabular Editor C# script, from `C:\Users\Alban Ssonko\Downloads\extract_model_dictionary (2).csx`), which pulls DAX/M directly from the live model — treat that file's formulas as authoritative when this glossary and the raw DAX ever disagree.

**Status: first pass.** Covers the `_fleetio` and `_measuresTable` display folders (the bulk of the model — driver grading, turnover, gap time, attendance) plus `_safety_measures` in full. **Not yet reviewed**: `_scheduling_measures`, `_zeem_measures` (EV charging fleet health), the HR/hiring-funnel measures in `Date_table` (leads/hired/trained via Freshsales), the 79 Calculated Columns section, the 47 Power Query M table-load definitions, and the What-If/Target/Forecast measure groups. Flag if you want the next pass to prioritize a specific one of these.

---

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

`EPH (No tips)` and `EPH (Uber)` are two distinct, intentionally-both-kept definitions (confirmed 2026-08-26) — `(No tips)` feeds `EPH Grade`; `(Uber)` uses raw `TotalEarnings` (tips included) for a different audience/report. Don't collapse these into one.

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

**Confirmed distinct (2026-08-26):** two separate source tables, not overlapping terminology for the same thing.

**`Accident Data`** (= `rpt.vw_accident_data`, the same table the Collision-Type Front/Rear classifier was built for) — manually-logged accident reports, one row per incident:
- **`Total Accidents`** — `COUNT('Accident Data'[Vehicle Number])`
- **`Collisions`** — `COUNT('Accident Data'[Collision Type])`
- **`at_fault`** / **`AF Accidents`** — count where `At Fault = "Yes"`
- **`NAF Accidents`** — count where `At Fault = "No"`
- **`Daily Average Accidents`**, **`Weekly Average Accidents`** — straightforward date/week-bucketed averages
- **`AverageDailyIncidents`**, **`AverageDailylyIncidentsAtFault`** (note: typo "Dailyly" is in the actual measure name), **`AverageDailylyIncidentsNoAtFault`**, **`AverageWeeklyIncidentsNotAtFault`**, **`LowestAverageWeeklyIncidents`** — all further slice the same `Accident Data[Collision Type]` count by fault/day/week, restricted to `YEAR('Date') >= 2025`
- **`Accidents per 30k miles`** — `(Total Crashes ÷ Miles Driven) × 30,000`. **⚠ `Total Crashes` is referenced here and in `Driver Rank` but has no measure definition anywhere in the model file — likely an orphaned reference to a renamed or deleted measure. Worth checking in Power BI Desktop directly (this would show as a DAX error in the model, not something visible from the exported dictionary alone).**

**`Safety Violations`** (Samsara-sourced automated coaching events — matches `ref.samsara_ev_safety_events` in the SQL layer) — `[Event Type]` values seen: "no seat belt", "harsh brake", "rolling stop", "inattentive driving", "obstructed" (view), "smoking":
- **`Incidents`** — `DISTINCTCOUNT('Safety Violations'[Safety Events ID])`
- **`Total Incidents`** — `COUNT('Safety Violations'[Event Type])` — ⚠ **near-duplicate of `Incidents`, not identical**: COUNT vs DISTINCTCOUNT, and a different column (`Event Type` vs `Safety Events ID`). If a Safety Events ID can have multiple Event Type rows (e.g. a single stop triggering both "harsh brake" and "rolling stop"), these two measures will disagree. Not yet confirmed which is "correct" — flag for a future round if it matters for reporting.
- **`Total Violations`** — literally `[Incidents]` (a pure alias, not a separate definition)
- **`Incidents per 1k miles`** — `(Incidents ÷ Miles Driven) × 1,000`
- **`Action`** — business rule: `IF([Incidents] > 2, "Suspension", "Coach")` — the threshold that turns raw incident counts into an HR/safety action recommendation
- **`Safety KPI Avg`** — a weighted composite safety score per location: starts at 100, subtracts `count(violation type) × weight` for each of the six Event Types above (weights pulled from a `Target Saftey` table [sic — typo in the actual table name, not fixed here] indexed 2–7), then caps the result at 85 if there's been any at-fault accident (`at_fault > 0`) in the current filter context
- **`Safety KPI_Target`** — the target line itself, `Target Saftey[Index] = 1`

---

## Fleet / vehicle status terms (`_fleetio` measure folder)

Vehicle status values seen across measures (from `'fleetio-vehicle-export'[vehicle_status_name]`, i.e. `std.fleetio_all_vehicles` — see `03_fleet_vehicles.md`): `Road Ready`, `Biohazard`, `Out of service`. Separately, `'Vehicle Status Change'` table uses **`Active`**/**`OSS`** as its own from/to status values — **not yet confirmed whether `OSS` = `Out of service` and `Active` = `Road Ready` are the same underlying states under different labels, or a genuinely separate status vocabulary** tracked by whatever populates `Vehicle Status Change`. Worth a targeted question if this table gets used for anything beyond the `Active to OOS Count`/`OOS to Active Count` transition-counting measures.

- **`Total Vehicles (Fleetio)`** — `DISTINCTCOUNT(license_plate)`, the base denominator most other fleet measures build on
- **`Purchased Vehicles`** — same distinct-plate count, different name — check whether this is meant to be identical to `Total Vehicles (Fleetio)` or intentionally scoped differently (e.g. includes retired vehicles that `Total Vehicles` might exclude via a status filter elsewhere in the report)
- **`Road Ready`**, **`Biohazard`**, **`Road Ready + Biohazard`** — vehicle counts filtered to those specific status values
- **`Active Vehicles`** — `Road Ready` status, distinct plate count (functionally same filter as `[Road Ready]` — check if these two should be merged)
- **`Percentage Active`** — `Active Vehicles ÷ Purchased Vehicles`
- **`Avg_MTTR_work_orders`** — Mean Time To Repair, in days: total OOS hours on completed work orders ÷ completed work order count ÷ 24
- **`Overall Car Score`** — average of `(exterior_score + interior_score) / 2` from `fleetio_inspections`

---

## Open items for the next pass

1. `_scheduling_measures`, `_zeem_measures` folders — not reviewed
2. Hiring/recruiting funnel measures in `Date_table` (`hired_paylocity`, `leads_freshsales`, `scheduled_interview_freshsales`, `trained_freshsales`, etc.) — ties to the Freshsales recruiting-pipeline domain in `06_external_misc.md`, not cross-referenced yet
3. Calculated Columns section (79 columns) — entirely unreviewed
4. Power Query M table-load definitions (47 queries) — entirely unreviewed; this is where the actual `rpt`/`dbo`/`std` source-table lineage for each Power BI table lives, and is worth cross-checking against the `dbo`-shadow-table warning in `00_START_HERE.md`
5. `Total Crashes` orphaned reference (see above) — needs checking directly in Power BI Desktop, not resolvable from the export alone
6. `Vehicle Status Change`'s `Active`/`OSS` vocabulary vs. Fleetio's `Road Ready`/`Out of service` — same states or different?
