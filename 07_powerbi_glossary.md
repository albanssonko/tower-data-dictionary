# Power BI Model Glossary — Common Phrases & KPI Definitions

Companion to [`00_START_HERE.md`](00_START_HERE.md) through [`06_external_misc.md`](06_external_misc.md), which document the raw SQL schema (`std`/`ref`). This file documents the **business/reporting layer** built on top of it: the semantic model in Power BI (Model name: `Model`, 87 tables, 324 measures, 79 calculated columns, 47 Power Query table loads).

Source: `PowerBI_Model_Dictionary.md` (generated 2026-08-26 via Tabular Editor C# script, from `C:\Users\Alban Ssonko\Downloads\extract_model_dictionary (2).csx`), which pulls DAX/M directly from the live model — treat that file's formulas as authoritative when this glossary and the raw DAX ever disagree.

**Status: complete pass (2026-08-26), merged with a v2 pass (2026-09-02).** All 324 measures, all 79 calculated columns, and all 47 Power Query M table-load definitions have been read. See the "Coverage note" near the end of this file for exactly what got deep-dived vs. lineage-only, and the small list of genuinely open items (an orphaned `Total Crashes` reference that needs Power BI Desktop to resolve, and a couple of lower-traffic queries not transcribed line-by-line). This pass also found and fixed a real gap from the first pass: `EPM`/`actual_trip_fare` don't exist as SQL columns anywhere (they're computed in Power Query), which caused a live query failure before this file explained why — see the warning section immediately below.

**2026-09-02 v2 merge:** a second, independent pass (`Tower_EV_KPI_Report_Model_Documentation.md`, generated via live Power BI Desktop connection through `powerbi-modeling-mcp` — a different tool than the Tabular Editor script above) wrote a `description` property on every table/measure/column directly in-model and re-verified the DAX/M. Its findings are folded into this file below (new DAX issues, hardcoded constants, and — most useful for query-writing — the full per-table SQL source mapping in the new appendix near the end). One unresolved discrepancy between the two passes, noted rather than silently picked: this pass counted **324** measures, the 2026-09-02 pass counted **323** — a one-measure drift (rename or deletion) that neither pass traces to a specific measure; worth a quick recount in Power BI Desktop if it matters for something.

---

## ✅ SQL views now exist for the Power-Query-only logic below — query these directly, don't recompute

**Created 2026-08-26**, so the formulas below are queryable from any device via the same read-only `mssql` connector, not dependent on this glossary being loaded as local context. All three are plain views (`SELECT` only needed, `db_datareader` already covers them) — additive, don't touch any table Power BI depends on, and are trivially reversible (`DROP VIEW`) if anything about them needs revisiting:

| View | Wraps | Adds |
|---|---|---|
| **`rpt.vw_driver_trip_activity`** | `rpt.DriverTripActivity` | `EPM`, `actual_trip_fare` |
| **`rpt.vw_all_drivers_enriched`** | `dbo.vw_all_drivers` + `dbo.test_punches` + `rpt.DriverTripActivity` + `raw.paylocity_car_seat_trained_drivers` | `[Locations]` (Mission/Douglas mapping), `[Last Active Date]`, `[Last Active Minus Terminated At]` (the ghosting formula), `[Veteran Status]`, `[Hire Type]`, `[Length of Service (Days)]`, `car_seat_active` |
| **`rpt.vw_uber_ev_driver_activity_hours`** | `std.uber_ev_driver_activity` | `[Hours On Trip]`/`[Hours Online]` parsed to decimal (base table stores them as `'DD:HH:MM'` text) — **fast, no date filter needed** |
| **`rpt.fn_uber_ev_driver_activity_dispatch_type(@StartDate, @EndDate)`** | `std.uber_ev_driver_activity` + `audit.vw_driver_shifts` | `dispatch_type` (`Re-dispatched`/`Regular`) — **table-valued function, always slow, see performance note below** |
| **`rpt.vw_uber_ev_driver_payments_enriched`** | `std.uber_ev_driver_payments` | `[Actual Net Fare]` (the date-dependent methodology switch at 2025-12-01), `[Pay Date]`, excludes the dummy driver UUID `9b63e6e2-16f8-4224-9d77-fd731eb51fec` |

**Deliberately NOT built as views** (scope decision, not an oversight):
- The **`Summary`** weekly-attrition table's own DAX has literal `-- adjust column names if needed` developer comments — replicating unverified logic into a new "official" SQL view would enshrine something the model's own author didn't finish trusting. Use `rpt.vw_all_drivers_enriched` (backing the confirmed-accurate `real turnover rate` metric) for turnover analysis instead.
- **`Vehicle Inventory Status`/`Vehicle Status Change`** (OOS day-tracking) — very complex recursive CTEs, and rebuilding them properly means fixing the `fleetio_all_vehicles` bare-reference bug (see `00_START_HERE.md`) at the same time, not bundling a bug-for-bug replica. Flagged as a larger follow-up, not done here.

**⚠️ `dispatch_type` is fundamentally slow, and this isn't fixable by adding a date filter.** First attempt was a single combined view with no date bound at all — a `SELECT TOP 5` took ~2 minutes. Added a date-parameterized table-valued function expecting that to fix it — it didn't: even filtered to one week, it took 320+ seconds. Root cause, traced 2026-08-26: `audit.vw_driver_shifts` (only 85K rows, so row count isn't it) derives shift boundaries from raw driver status-ping events (`audit.uber_driver_realtime`) using `LAG`/`LEAD`/window-aggregates with `ROWS UNBOUNDED PRECEDING/FOLLOWING` frames, partitioned by driver and computed over **each driver's entire history** — that's inherent to how sequential shift-boundary detection works and cannot have a date predicate pushed into it from a query built on top. **This is a property of `audit.vw_driver_shifts` itself, not something wrappable away.** Given that, the fix was to split what needs it from what doesn't: `[Hours On Trip]`/`[Hours Online]` (the columns that actually feed `EPH`/`Gap Time`/`Idle Hours` above) don't touch `audit.vw_driver_shifts` at all and are back to normal speed (`rpt.vw_uber_ev_driver_activity_hours`, confirmed 0.1s). `dispatch_type` is isolated in its own function, genuinely slow no matter what, and not needed by any measure documented elsewhere in this glossary — only reach for it if you specifically need redispatch analysis, and expect it to take minutes.

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
- **`Count of A/B/C/D Grades`** and **`% (Grade A/B/C/D) Drivers`** — same pattern applied to **`Overall Grade`** / **`Overall Score`**. **Resolved 2026-09-02 (was "not yet reviewed" here):** despite being nominally a composite across all four KPIs, the EPH and Gap Time contribution terms are present in the DAX but **commented out** of both `Overall Grade` and `Overall Score` — so neither currently influences the composite, even though EPH and Gap Time grading are otherwise fully computed elsewhere in the model. Anyone relying on "Overall Grade" as a true all-KPI composite should know it's currently AR/CR/UR only.

**Two more confirmed issues in this family (2026-09-02):** **`% B CR`/`% C CR`** appear swapped — `% B CR` divides by `(C) CR` and vice versa. **`UR Grade`**'s "A" boundary (`<= 5.0`) makes nearly all realistic driver-rating values grade "A", since ratings rarely exceed 5.0 — the band is nominally A/B/C/D but in practice almost never produces anything but A.

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

## Hardcoded business constants across the model (2026-09-02 pass)

None of these live in a parameter table — they're literals baked directly into DAX, so changing the business rule means editing the measure, not a config table:

| Constant | Where |
|---|---|
| 12% acceptable gap-time threshold | `Gap time Variance` (see above) |
| $18/hr gap-time dollar rate | `Gap time Variance ($)` (see above) |
| March 2025 date exclusion | `Gap Hours` (see above) |
| Mission/Douglas-only location list | `avg_dispatch` (`_fleetio`) |
| 3.8 drivers-per-car ratio | `Target Drivers (Based on Cars Active)` (`HR Target`) |
| 90 miles/day (driver) and 100 miles/day (location) mileage expectations | `Driver Rank` / `Table Rank` (`_measuresTable`) |
| `What-if-period` hardcoded to 8, unused | `What if Hire` — a separate hardcode of 40 is used instead by the sibling measure `What-if-Active`, so `What-if-period` currently has no effect |

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

**⚠️ Grading-parameter fallback inconsistency (2026-09-02):** the 19 grade-threshold what-if tables (§ "Fleet / vehicle status terms" note above, and generally) fall back to `Grading Targets[Scale]` when nothing is selected — **except** `Safety Grade B/C Value` (`Violations Grade B/C`), which has no fallback and returns blank if unselected, unlike its sibling grade-parameter measures.

---

## Fleet / vehicle status terms (`_fleetio` measure folder)

Vehicle status values seen across measures (from `'fleetio-vehicle-export'[vehicle_status_name]`, i.e. `std.fleetio_all_vehicles` — see `03_fleet_vehicles.md`): `Road Ready`, `Biohazard`, `Out of service`. Separately, `'Vehicle Status Change'` table uses **`Active`**/**`OSS`** as its own from/to status values — **not yet confirmed whether `OSS` = `Out of service` and `Active` = `Road Ready` are the same underlying states under different labels, or a genuinely separate status vocabulary** tracked by whatever populates `Vehicle Status Change`. Worth a targeted question if this table gets used for anything beyond the `Active to OOS Count`/`OOS to Active Count` transition-counting measures.

- **`Total Vehicles (Fleetio)`** / **`Purchased Vehicles`** — **confirmed duplicates (2026-08-26)**: both `DISTINCTCOUNT(license_plate)`, same meaning under two names. `Total Vehicles (Fleetio)` is the one other measures reference (e.g. `Road Ready + Biohazard`, `Actual Assigned - Target`), so treat it as canonical; `Purchased Vehicles` as the alias.
- **`Road Ready`**, **`Biohazard`**, **`Road Ready + Biohazard`** — vehicle counts filtered to those specific status values
- **`Road Ready`** / **`Active Vehicles`** — **confirmed duplicates (2026-08-26)**: both filter `Total Vehicles (Fleetio)`/`Purchased Vehicles` to `vehicle_status_name = "Road Ready"`. `Road Ready` is the shorter name and the one composed into other measures (`Road Ready + Biohazard`, `road_ready - dispatch_target`); treat it as canonical.
- **`Percentage Active`** — `Active Vehicles ÷ Purchased Vehicles`
- **`Avg_MTTR_work_orders`** — Mean Time To Repair, in days: total OOS hours on completed work orders ÷ completed work order count ÷ 24
- **`Overall Car Score`** — average of `(exterior_score + interior_score) / 2` from `fleetio_inspections`
- **⚠️ `active_11am`/`active_11pm`** (2026-09-02) — inconsistent aggregation: one uses `DISTINCTCOUNT`, the other plain `COUNT`. Don't assume they're computed the same way just because they're a matched AM/PM pair.

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

**⚠️ `Avg session duration (min)`** (2026-09-02) — averages `energy_kwh`, not `duration_minutes`. Looks like a copy-paste bug in the DAX; the measure name and what it actually computes don't match. Don't trust its value for anything duration-related.

## Report-helper / what-if table quirks (2026-09-02)

Two small lookup tables back dropdown-style selectors elsewhere in the model, and both have a gap worth knowing before trusting a selection:

- **`Metrics`** (`Metric`, `Index` columns) → its one local measure, **`Average Metric Value`**, `SWITCH`es on the selected `Metric` value — but the `Metric` column includes an "Uber Logout" option with **no matching case** in the `SWITCH`. Selecting it returns blank, not an error, so a blank result here doesn't necessarily mean no data.
- **`Hours Type`** (`Type` column) → its local measure, **`uber_live_status`**, has an "Online" case written into the formula but **commented out**. If "Online" is a selectable value in the table, choosing it also silently returns blank.

---

## Appendix: Power BI table → SQL source, all 87 tables (2026-09-02 pass)

The `EPM`/`rpt.DriverTripActivity` trap above (and the `dbo` shadow-table bug) are the two examples already called out in depth. This appendix is the same exercise done for **every** Power BI table — so instead of opening Power BI Desktop to check what a table actually queries, check here first. "Bare" means no schema prefix in the M query — per `00_START_HERE.md`'s `dbo` trap, that resolves to whatever the login's default schema is (`dbo`), which may or may not be the live copy.

**Uber Operations**

| Power BI table | SQL source | Load | Notes |
|---|---|---|---|
| Uber Trip Activity | `rpt.DriverTripActivity` (+ `vw_all_drivers` join) | incremental, 4yr rolling/3-day | Full lineage above — recomputes `actual_trip_fare`, `EPM`, `Trip Time (Hours)`; blank `product_type` → `'*Unknown'` |
| Uber Driver Activity | `std.uber_ev_driver_activity` | incremental | Parses `TimeOnTrip`/`TimeOnline` (`'DD:HH:MM'` text) to decimal hours; `Re-dispatched` flag via self-join to `audit.vw_driver_shifts`. Prefer `rpt.vw_uber_ev_driver_activity_hours` — same hours columns, no slow join |
| Uber Driver Payments | `std.uber_ev_driver_payments` | incremental | `Actual Net Fare` methodology switch at 2025-12-01 (below); `Pay Date` = week start + 11 days; excludes `DriverUUID 9b63e6e2-16f8-4224-9d77-fd731eb51fec`. Prefer `rpt.vw_uber_ev_driver_payments_enriched` |
| Uber Driver Quality | `std.uber_ev_driver_quality` | incremental | Straight pull, lowercases `driver_uuid` for joins |
| Uber Driver Shifts | `audit.vw_driver_shifts` | incremental | AM (4am–3pm) / PM bucket by login time; `redispatched_same_shift`/`plate_mismatch` via window functions. Slow — see `dispatch_type` warning above |
| uber_live_driver_status | `audit.vw_driver_shifts` | DirectQuery, incremental window | Live feed |
| Uber Payment Orders | `uber_payment_orders_new` (bare) | incremental | Filtered to `description = 'so.payout'` |
| uber_teens | `raw.uber_reserve_trips` | incremental | Dedup one row per `trip_uuid` |
| car_seat_paired | Uber trip activity + car-seat-trained roster + equipped-vehicle list | DirectQuery | Trips per driver/vehicle/day |
| uber_ev_auto_pos | `dbo.uber_ev_auto_pos` | DirectQuery | Type-safe casts on all timestamp/numeric fields |

**Fleet / Vehicle**

| Power BI table | SQL source | Load | Notes |
|---|---|---|---|
| fleetio-vehicle-export | `std.fleetio_all_vehicles` + most-recent-open-work-order join | DirectQuery | Filtered to 2 Fleetio group IDs |
| fleetio-vehicle-renewals | `vw_vehicles_ancestry` (bare) | — | VIN pull only |
| fleetio_ev_work_orders / fleetio_ev_work_orders (2) | `rpt.fleet_work_orders` | incremental | `(2)` = same source filtered to `Completed`, one row per vehicle (most recent only). Computes `Total Cost`, `hours_oos`/`Service Time (mins)`, `Due Status` |
| fleetio_inspections | `vw_fleetio_inspections_carwash` (bare) | incremental | Most complex M query in the model — multi-step employeeId fallback, joins punches + Uber shifts, ±180min sanity-check guards |
| Vehicle Status Change / Vehicle Inventory Status | `rpt.vehicle_status_shift` | incremental / full snapshot | Day-by-vehicle OOS timeline from status-change gaps; Inventory Status recurses a full date series per vehicle (`OPTION (MAXRECURSION 3660)`). ⚠ both affected by the bare-`fleetio_all_vehicles` bug — see `00_START_HERE.md` |
| Samsara Vehicles | `samsara_vehicle` joined to Fleetio by name-prefix match | — | 2 fleet group IDs |
| samsara_assets | `vw_samsara_assets_location_unique` (bare) | DirectQuery | |
| samsara_trips | `raw.samsara_trips` | incremental | Unix epoch ms → date, meters → miles |
| parking_tickets | `rpt.vw_parking_tickets` | DirectQuery | Straight pull |
| Accident Data | `rpt.vw_accident_data` | incremental | Derives `Collision Type Category` (Front/Rear) from keyword match on `Collision Type` text |

**EV Charging**

| Power BI table | SQL source | Load | Notes |
|---|---|---|---|
| zeem | `vw_zeem_battery_degradation` (bare, `dbo`-only) | full pull | All SoH/efficiency computation happens upstream in the view, not in this query |

**HR / Payroll / Scheduling**

| Power BI table | SQL source | Load | Notes |
|---|---|---|---|
| Paylocity Punches | `dbo.test_punches` | incremental, 21-day window | Computes `Period` (pre/post Oct-2025 cutover), `OT` (hours beyond 8.5), `Meal Premium` (flag if 5+ hrs between shift start and lunch). Name suggests staging but confirmed legitimate — see `'All Drivers'` lineage above |
| paylocity_payments | `std.paylocity_ev_payments` | incremental | |
| schedule-paylocity | `vw_paylocity_ev_shift_unified_pacific` (bare) | incremental | Left-joined to punches for Show/No-Show; This-Week/Next-Week/Other labels, DST-aware AM/PM date-range split |
| schedule-paylocity (off) | `std.paylocity_ev_payments` filtered to PTO/HOL/SICK/UTO/BRVMT etc. | incremental | Saturday dates shifted back 10 days — a payroll-calendar quirk, not a bug |
| schedule Targets | SharePoint `Tower EV - Targets.xlsx`, "Targets Scheduling" sheet | — | Unpivoted from a wide day-by-hour grid |
| freshsales_contacts | `ref.freshsales_contacts` filtered `custom_field_cf_buisness = 'EV'` | incremental | ⚠ pulls the plaintext-password column straight from source — see `06_external_misc.md` |
| Locations | SharePoint `Tower EV - Locations.xlsx` | — | Excludes "Tower WAV" and "WMATA" locations |
| userm | `dbo.uber_all_drivers` filtered `org_name = 'TOWER WAV LLC - W2'` | — | Reformats first/last name into proper-case `Full Name` |
| Grading Targets | a `kpi_grading` table (schema not specified in the M query) | — | `kpi_grading` exists in both `dbo` and `stg`, identical 32 rows (`00_START_HERE.md`) — which one this table reads was not confirmed either pass |
| Survey | SharePoint `Tower EV Driver Exit Survey.xlsx` | — | Normalizes free-text dispatch-communication ratings to a consistent A–F scale |
| Termination Category | SharePoint `Termination_Reasons_List.xlsx` | — | Reason text uppercased/trimmed for join matching |
| Weighted Avg Score, Targets Ops, Target Saftey, Target Dispatch | SharePoint `Tower EV - Targets.xlsx` (other sheets) | — | |

**Calculated in DAX — no external source**

- `Date`, `Date_table` — `CALENDAR()` (2024–2027) + `ADDCOLUMNS` for derived date attributes
- `Metrics`, `Report Rows` — `DATATABLE()` hardcoded lookup lists
- `Summary` — `SELECTCOLUMNS(CROSSJOIN(...))` of every driver location × every date since 2024-09-12
- `license_plate` — `DISTINCT('fleetio-vehicle-export'[license_plate])`
- All 19 grade-threshold tables, plus `Freshsales Hire Target`, `Freshsales Termation Estimate`, `What if Cars`, `What if Hire`, `What-if Drivers Per Car`, `Running Avg Days` — `GENERATESERIES()`; these are report-adjustable what-if slicers, **not** static values, despite some earlier passes characterizing a couple of them that way
- `_measuresTable`, `_fleetio`, `_safety_measures`, `_scheduling_measures`, `_zeem_measures`, `html`, `_freshsales`, `_fleet` — `Row("Column", BLANK())` placeholders; exist only to host measures, not data

## Coverage note

This pass reviewed: all measure display folders (`_fleetio`, `_measuresTable`, `_safety_measures`, `_scheduling_measures`, `_zeem_measures`), the Freshsales hiring-funnel measures in `Date_table`, the remaining ungrouped measure tables (`Summary`, `Report Rows`, `Vehicle Inventory Status`, `Vehicle Status Change`, `Targets`/What-If groups, etc.), the Calculated Columns section (found: 71 of 79 are unusable placeholders — "derived from calculated table" — the extraction tool didn't capture DAX-calculated-table expressions; the 8 that did have real formulas are folded into the sections above), and all 47 Power Query M table-load definitions (table/schema lineage extracted for every one; full formula-level detail captured for the highest-traffic tables — `All Drivers`, `Uber Trip Activity`, `Uber Driver Activity`, `Uber Driver Payments`, `Vehicle Inventory Status`, `Vehicle Status Change`, `fleetio_ev_work_orders`, `fleetio_inspections`).

**Genuinely still open (confirmed still open as of the 2026-09-02 pass too — neither pass resolved these):**
- `Total Crashes` orphaned reference (referenced by `Accidents per 30k miles` and `Driver Rank`, defined nowhere) — needs checking directly in Power BI Desktop/Tabular Editor, not resolvable from a static export
- The exact mapping of `rpt.vehicle_status_shift`'s `Active`/`OSS` values back to Fleetio's full status vocabulary (`Road Ready`/`Out of service`/`Biohazard`) — what populates that table wasn't traced by either pass
- Which schema (`dbo` or `stg`) the `Grading Targets` table's `kpi_grading` source actually reads from (both exist, both 32 rows, M query doesn't say)
- Fully line-by-line formula detail for the lower-traffic M queries (`parking_tickets`, `Samsara Vehicles`, `samsara_trips`, `Uber Payment Orders`, `uber_teens`, `userm`, etc.) — schema/table lineage is captured for all of them (see the appendix above), but not every WHERE-clause business rule was transcribed
- The 324-vs-323 measure count discrepancy between the two passes (see top of file)
