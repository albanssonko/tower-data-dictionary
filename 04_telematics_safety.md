# Telematics & Safety (Samsara)

Samsara provides in-vehicle telematics/dashcam hardware — driver safety events, idle time, and location tracking. This is the primary data source for driver-safety alerting (`alert_operations.py`).

## Tables

- **`std.samsara_drivers`** — the driver-profile registry Samsara knows about: `id`, `name`, `licenseNumber`/`licenseState` (join key to Paylocity's `custom_Driver_License` for identity verification), `driverActivationStatus` (e.g. `active`), **`fleet`** (distinguishes EV vs WAV within this single un-suffixed table), `tag_id`/`tag_name`/`tags_json`. Two dispatch/shared profiles — `'CC LAX'` and `'CC Mission'` — are explicitly excluded from driver-mismatch checks since they represent shared accounts, not individual people.
- **`ref.samsara_ev_safety_events`** — coaching/safety-event log: `id`, `driver_id` (→ `std.samsara_drivers.id`), `driver_name`, **`vehicle_name`** (despite the name, this is actually a **license plate**, not a Samsara asset name — joins to `license_plate` elsewhere), `vehicle_vin`, `event_time`, `behavior_name1` (e.g. `Rolling Stop`), `coaching_state` (events with `coaching_state = 'dismissed'` are excluded from alerting), `max_acceleration_gforce`, dashcam video URLs, lat/lng. **⚠️ There is also a `dbo.samsara_ev_safety_events` that is stale (stopped 2026-08-07) — `alert_operations.py`'s `initialize_queue()` still references this table unqualified and is very likely reading the stale `dbo` copy; this wasn't fixed as part of the earlier `alert_operations.py` schema-qualification fix and is worth checking.**
- **`std.samsara_trips`** — minimal trip-distance rollup (`startDate`, `distanceMiles`, `licenseNumber`) — 9.2M rows but only 3 columns; a lightweight daily-distance feed, not a replacement for Uber's own richer trip_activity tables.
- **`std.samsara_dva`** — currently empty (0 rows, 1 column). Likely "Driver Vehicle Assignment" based on the name, but unconfirmed/unused as of this writing.
- **`ref.samsara_assets`** — the vehicle/asset registry from Samsara's side (separate from both Fleetio's and Uber's vehicle tables): `id` (PK), VIN, `licensePlate`, make/model/year, live telemetry snapshot (`last_latitude`/`last_longitude`/`last_speed_mph`/`last_location_time_utc`), odometer, `engine_state`, `fleet`.
- **`ref.samsara_idle_times`** (+ `_wav`) — idle-event log: asset/VIN/plate, `idle_start_time_local`/`idle_end_time_local`, `duration_minutes`, location.
- **`ref.samsara_onsite_location`** (+ `_wav`) — **by far the largest tables in the database** (143M and 74M rows respectively) — granular location/dwell tracking relative to depot (`distance_to_depot_miles`, `duration_hours`, `event`). Given the scale, always filter by date/vehicle before querying — an unfiltered `SELECT *` here will be very slow and return an enormous result.
- **`ref.samsara_shift_min_distance`** (+ `_wav`) — per-shift minimum-distance-from-depot tracking, joined to a specific `driver_uuid`/`shift_id`/`shift_start_time`/`shift_end_time` and the last trip before the shift ended (`last_trip_uuid`, `last_trip_drop_off_time`) — looks purpose-built for detecting drivers who end a shift far from depot or without a proper trip close-out.
- **`ref.samsara_tag`** — tiny lookup (216 rows) of Samsara's tag/grouping taxonomy (`id`, `name`, `parentTagId` for a hierarchy).

<!-- AUTO:BEGIN tables (regenerated daily by scripts/regenerate.py — do not hand-edit below this line) -->
### `std.samsara_drivers`  (rows: 10,662 | cols: 28)

| Column | Type | Null? |
|---|---|---|
| id | varchar(50) | Y |
| name | varchar(100) | Y |
| username | varchar(100) | Y |
| notes | varchar(50) | Y |
| licenseNumber | varchar(50) | Y |
| licenseState | varchar(50) | Y |
| timezone | varchar(50) | Y |
| updatedAtTime | varchar(50) | Y |
| createdAtTime | varchar(50) | Y |
| driverActivationStatus | varchar(50) | Y |
| phone | varchar(50) | Y |
| profileImageUrl | varchar(4000) | Y |
| hasVehicleUnpinningEnabled | varchar(50) | Y |
| eld_cycle | varchar(50) | Y |
| eld_shift | varchar(50) | Y |
| eld_restart | varchar(50) | Y |
| eld_break | varchar(100) | Y |
| carrierName | varchar(50) | Y |
| mainOfficeAddress | varchar(100) | Y |
| dotNumber | varchar(50) | Y |
| homeTerminalName | varchar(50) | Y |
| homeTerminalAddress | varchar(100) | Y |
| heavyHaulExemptionToggleEnabled | varchar(50) | Y |
| tag_id | varchar(50) | Y |
| tag_name | varchar(50) | Y |
| tags_json | varchar(500) | Y |
| fleet | varchar(50) | Y |
| ingested_at | varchar(50) | Y |

### `std.samsara_trips`  (rows: 9,173,367 | cols: 3)

| Column | Type | Null? |
|---|---|---|
| startDate | date | Y |
| distanceMiles | float | Y |
| licenseNumber | nvarchar(50) | Y |

### `std.samsara_dva`  (rows: 0 | cols: 1)

| Column | Type | Null? |
|---|---|---|
| id | nvarchar(255) | N |

### `ref.samsara_assets`  (rows: 810 | cols: 21 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | bigint | N |
| name | nvarchar(200) | Y |
| type | nvarchar(50) | Y |
| vin | nvarchar(50) | Y |
| licensePlate | nvarchar(50) | Y |
| readingsIngestionEnabled | nvarchar(50) | Y |
| make | nvarchar(50) | Y |
| model | nvarchar(100) | Y |
| year | int | Y |
| regulationMode | nvarchar(50) | Y |
| createdAtTime | datetime2 | Y |
| updatedAtTime | datetime2 | Y |
| last_latitude | float | Y |
| last_longitude | float | Y |
| last_location | nvarchar(200) | Y |
| last_speed_mph | float | Y |
| last_location_time_utc | datetime2 | Y |
| obd_odometer_meters | bigint | Y |
| obd_odometer_time | datetime2 | Y |
| engine_state | varchar(10) | Y |
| fleet | varchar(50) | Y |

### `ref.samsara_ev_safety_events`  (rows: 348,653 | cols: 20 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | varchar(50) | N |
| driver_id | varchar(50) | Y |
| driver_name | varchar(100) | Y |
| vehicle_id | varchar(50) | Y |
| vehicle_name | varchar(100) | Y |
| vehicle_serial | varchar(100) | Y |
| vehicle_vin | varchar(100) | Y |
| vehicle_samsara_serial | varchar(100) | Y |
| vehicle_samsara_vin | varchar(100) | Y |
| event_time | datetime | Y |
| max_acceleration_gforce | float | Y |
| download_forward_video_url | text | Y |
| download_inward_video_url | text | Y |
| location_latitude | float | Y |
| location_longitude | float | Y |
| coaching_state | varchar(50) | Y |
| behavior_label1 | varchar(50) | Y |
| behavior_source1 | varchar(50) | Y |
| behavior_name1 | varchar(100) | Y |
| Organization | varchar(6) | Y |

### `ref.samsara_idle_times`  (rows: 1,244,117 | cols: 10 | PK: Id)

| Column | Type | Null? |
|---|---|---|
| **Id** | int | N |
| asset_id | varchar(50) | Y |
| vin | varchar(50) | Y |
| licensePlate | varchar(50) | Y |
| idle_start_time_local | datetime | Y |
| idle_end_time_local | datetime | Y |
| duration_minutes | float | Y |
| latitude | float | Y |
| longitude | float | Y |
| hash_key | nvarchar(max) | Y |

### `ref.samsara_idle_times_wav`  (rows: 1,922,451 | cols: 10 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| asset_id | nvarchar(50) | Y |
| vin | nvarchar(50) | Y |
| licensePlate | nvarchar(50) | Y |
| idle_start_time_local | datetime2 | Y |
| idle_end_time_local | datetime2 | Y |
| duration_minutes | float | Y |
| latitude | float | Y |
| longitude | float | Y |
| hash_key | nvarchar(64) | Y |

### `ref.samsara_onsite_location`  (rows: 166,498,026 | cols: 12)

| Column | Type | Null? |
|---|---|---|
| id | bigint | N |
| vin | nvarchar(50) | Y |
| licensePlate | nvarchar(50) | Y |
| last_latitude | float | Y |
| last_longitude | float | Y |
| last_location | nvarchar(250) | Y |
| last_speed_mph | float | Y |
| last_location_time_local | datetime2 | Y |
| distance_to_depot_miles | decimal | Y |
| event | varchar(50) | Y |
| duration_hours | decimal | Y |
| hash_key | varchar(64) | Y |

### `ref.samsara_onsite_location_wav`  (rows: 80,281,994 | cols: 12)

| Column | Type | Null? |
|---|---|---|
| id | bigint | N |
| vin | nvarchar(50) | Y |
| licensePlate | nvarchar(50) | Y |
| last_latitude | float | Y |
| last_longitude | float | Y |
| last_location | nvarchar(250) | Y |
| last_speed_mph | float | Y |
| last_location_time_local | datetime2 | Y |
| distance_to_depot_miles | decimal | Y |
| event | varchar(50) | Y |
| duration_hours | decimal | Y |
| hash_key | varchar(64) | Y |

### `ref.samsara_shift_min_distance`  (rows: 370,161 | cols: 20)

| Column | Type | Null? |
|---|---|---|
| id | bigint | N |
| vin | nvarchar(50) | Y |
| licensePlate | nvarchar(50) | Y |
| last_latitude | float | Y |
| last_longitude | float | Y |
| last_location | nvarchar(250) | Y |
| last_speed_mph | float | Y |
| last_location_time_local | datetime2 | Y |
| distance_to_depot_miles | decimal | Y |
| event | varchar(50) | Y |
| duration_hours | decimal | Y |
| last_trip_uuid | nvarchar(100) | Y |
| last_trip_drop_off_time | datetime2 | Y |
| lat2 | float | Y |
| lng2 | float | Y |
| shift_id | int | Y |
| shift_start_time | datetime2 | Y |
| shift_end_time | datetime2 | Y |
| driver_uuid | nvarchar(100) | Y |
| rn | bigint | Y |

### `ref.samsara_shift_min_distance_wav`  (rows: 8,875 | cols: 20)

| Column | Type | Null? |
|---|---|---|
| id | bigint | N |
| vin | nvarchar(50) | Y |
| licensePlate | nvarchar(50) | Y |
| last_latitude | float | Y |
| last_longitude | float | Y |
| last_location | nvarchar(250) | Y |
| last_speed_mph | float | Y |
| last_location_time_local | datetime2 | Y |
| distance_to_depot_miles | decimal | Y |
| event | varchar(50) | Y |
| duration_hours | decimal | Y |
| last_trip_uuid | nvarchar(100) | Y |
| last_trip_drop_off_time | datetime2 | Y |
| lat2 | float | Y |
| lng2 | float | Y |
| shift_id | int | Y |
| shift_start_time | datetime2 | Y |
| shift_end_time | datetime2 | Y |
| driver_uuid | nvarchar(100) | Y |
| rn | bigint | Y |

### `ref.samsara_tag`  (rows: 216 | cols: 3 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | nvarchar(100) | N |
| name | nvarchar(255) | Y |
| parentTagId | nvarchar(100) | Y |

<!-- AUTO:END tables -->
