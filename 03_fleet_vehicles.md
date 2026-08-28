# Fleet & Vehicles (Fleetio)

Fleetio is Tower's fleet-management system — the vehicle-centric counterpart to Paylocity (people) and Uber (trips). Covers the vehicle registry, vehicle-associated contacts, parts inventory, renewals, and inspections.

### The `dbo` rule for Fleetio specifically (confirmed 2026-08-26)

The general rule in `00_START_HERE.md` is "avoid `dbo`, use `std`" — for Fleetio, refine that to: **use `std.fleetio_*` when it exists; only fall back to `dbo.fleetio_*` when no `std` copy exists at all.** Not every Fleetio table has been migrated into `std` — many legitimately live in `dbo` only, and that's correct, not a bug:

Confirmed `dbo`-only (no `std` equivalent — using `dbo` here is required, not a mistake): `fleetio_vendors`, `fleetio_all_service_reminders` (+ `_staging`), `fleetio_all_vehicles_staging`, `fleetio_inspection_records_copy`, `fleetio_service_tasks_staging`, `fleetio_vehicle_acquisitions_staging`, `fleetio_vehicle_purchase_details_staging`, and the work-order table `fleetio_ev_work_orders` (lives in `dbo`/`raw`, no `std` copy — `alert_fleet.py` correctly uses `dbo.fleetio_ev_work_orders`).

Confirmed has a **better** `std` copy — use `std`, not `dbo`: `fleetio_all_vehicles` (`dbo` has 676 rows vs `std`'s 851 — see the `dbo`-trap table in `00_START_HERE.md`), `fleetio_contacts` (`std`-only, no `dbo` copy at all), `fleetio_vehicle_renewals`, `fleetio_shift_type_backfill`, `fleetio_vehicle_statuses`, `fleetio_part_location_details`.

**Bug found and fixed 2026-08-26:** `alert_fleet.py` had `FLEET_VEHICLE_STATUS_TABLE = "fleetio_all_vehicles"` (line 44, unqualified — same bug class as the `alert_operations.py` fixes) used in an f-string query, silently resolving to the incomplete `dbo` copy. Fixed to `"std.fleetio_all_vehicles"`. That same file's `dbo.fleetio_vendors` and `dbo.fleetio_ev_work_orders` references are correct as-is (no `std` equivalent exists for either) — not touched.

## Tables

- **`std.fleetio_all_vehicles`** — the vehicle registry, one row per vehicle, 79 columns. Key columns: `license_plate` (universal vehicle join key — see START_HERE), `vin`, `make`/`model`/`year`, **`vehicle_status_name`**/`vehicle_status_id`/`vehicle_status_color` (e.g. `Training Vehicle` is explicitly excluded from several alert checks — see `alert_operations.py`), `group_id`/`group_name`/`group_ancestry` (Fleetio's location/org hierarchy — `group_hierarchy` on `fleetio_contacts` uses a matching prefix convention like `Tower WAV%`), `out_of_service_date`/`cf_out_of_service_reason`/`cf_out_of_service_location` (custom fields tracking OOS vehicles), `cf_car_seat`/`cf_carseat` (note: **two separate, inconsistently-named columns** — check both if querying car-seat equipment), `cf_ramp_entry` (WAV wheelchair-ramp flag), `cf_uuid`, `driver` (currently assigned driver, freeform).
- **`std.fleetio_contacts`** — people known to Fleetio (drivers/technicians), separate from but overlapping with Paylocity employees: `name`/`first_name`/`last_name`, `email`, `employee_number`, `license_number`/`license_class`/`license_state`, `group_id`/`group_name`/`group_hierarchy`, `contact_status`, `custom_fields` (raw JSON — contains a `driver_uuid` accessible via `JSON_VALUE(custom_fields, '$.driver_uuid')`, used to cross-check against Uber's own driver UUID). The "Fleetio contact missing employee_number/license_number/driver_uuid" HR check reads this table filtered to `contact_status = 'active'` and `group_hierarchy LIKE 'Tower WAV%'`.
- **`std.fleetio_vehicle_renewals`** — registration/insurance-type renewal reminders per vehicle: `vehicle_renewal_type_id`/`_name`, `next_due_at`, `due_soon_at`, `last_sent_at`.
- **`std.fleetio_vehicle_statuses`** — tiny lookup (12 rows) of the possible `vehicle_status_name` values and their display color/position — the enum backing `fleetio_all_vehicles.vehicle_status_id`.
- **`std.fleetio_part_location_details`** / **`ref.fleetio_vehicle_purchase_details`** — parts inventory (quantity on hand/allocated/ordered, reorder points) and vehicle purchase/warranty records respectively. Niche, not typically needed for driver/safety analysis.
- **`std.fleetio_shift_type_backfill`** — a thin two-column mapping (`inspection_id` → `shift_type`), looks like a one-off backfill join table rather than an ongoing feed.
- **`std.service_tasks`** — Fleetio's service/work-order task catalog (VMRS classification codes for repair categorization) — the task *types*, not individual work orders (those live in `rpt.fleet_work_orders`, not documented here since `rpt` is the BI layer).
- **`std.vehicle_inspections`** — Tower's own driver vehicle-inspection submissions (not a Fleetio table despite living alongside them) — pre-trip checklist results: cleanliness ratings, car-seat/safety-equipment presence, mechanical checks (`service_brakes`, `horn`, `head_lamps_brake_lights_blinkers`, `windshield`, `wipers_washers`, `tire_pressure`), photo/signature capture metadata. Only 6 rows currently — either a very new feature or narrowly piloted; don't assume this table is comprehensively populated.

<!-- AUTO:BEGIN tables (regenerated daily by scripts/regenerate.py — do not hand-edit below this line) -->
### `std.fleetio_all_vehicles`  (rows: 851 | cols: 79)

| Column | Type | Null? |
|---|---|---|
| id | int | Y |
| vehicle_renewal_reminders_count | int | Y |
| primary_meter_usage_per_day | varchar(50) | Y |
| year | int | Y |
| secondary_meter_usage_per_day | varchar(50) | Y |
| created_at | datetimeoffset | Y |
| fuel_entries_count | int | Y |
| fuel_type_id | int | Y |
| default_image_url_small | varchar(1000) | Y |
| fuel_volume_units | varchar(50) | Y |
| ownership | varchar(50) | Y |
| documents_count | int | Y |
| color | varchar(50) | Y |
| cf_ramp_entry | varchar(50) | Y |
| system_of_measurement | varchar(50) | Y |
| primary_meter_date | varchar(50) | Y |
| registration_state | varchar(50) | Y |
| cf_oos_eta_return | varchar(50) | Y |
| in_service_date | varchar(max) | Y |
| comments_count | int | Y |
| cf_rideshare_partner | varchar(50) | Y |
| vehicle_status_color | varchar(50) | Y |
| estimated_resale_price_cents | int | Y |
| make | varchar(50) | Y |
| cf_ab_title_verification_ | varchar(50) | Y |
| secondary_meter_date | varchar(50) | Y |
| vehicle_status_id | int | Y |
| cf_out_of_service_reason | varchar(50) | Y |
| updated_at | datetimeoffset | Y |
| name | varchar(100) | Y |

_+ 49 more columns (truncated for brevity):_ model, estimated_replacement_mileage, service_entries_count, inserted_at, out_of_service_meter_value, estimated_service_months, cf_fastrak_code, secondary_meter_unit, vin, registration_expiration_month, images_count, specs, group_ancestry, vehicle_type_id, work_orders_count, issues_count, fuel_type_name, in_service_meter_value, group_name, cf_remote, assetable_type, ai_enabled, archived_at, vehicle_status_name, axle_config_id, license_plate, cf_out_of_service_location, is_sample, cf_purchase_entity, vehicle_type_name, secondary_meter_value, cf_oos_description, current_location_entry_id, account_id, out_of_service_date, group_id, service_reminders_count, primary_meter_value, primary_meter_unit, driver, trim, cf_location_of_original_title, cf_gas_card, cf_af_accident_, cf_car_seat, cf_carseat, cf_uuid, cf_panic_button, cf_decommission_

### `std.fleetio_contacts`  (rows: 11,795 | cols: 46)

| Column | Type | Null? |
|---|---|---|
| id | bigint | Y |
| name | nvarchar(200) | Y |
| first_name | nvarchar(50) | Y |
| middle_name | nvarchar(100) | Y |
| group_id | bigint | Y |
| group_name | nvarchar(50) | Y |
| last_name | nvarchar(50) | Y |
| images_count | bigint | Y |
| documents_count | bigint | Y |
| comments_count | bigint | Y |
| group_hierarchy | nvarchar(100) | Y |
| email | nvarchar(100) | Y |
| technician | bit | Y |
| vehicle_operator | bit | Y |
| employee | bit | Y |
| birth_date | nvarchar(50) | Y |
| city | nvarchar(50) | Y |
| country | nvarchar(50) | Y |
| employee_number | nvarchar(50) | Y |
| home_phone_number | nvarchar(50) | Y |
| job_title | nvarchar(100) | Y |
| leave_date | nvarchar(max) | Y |
| license_class | nvarchar(50) | Y |
| license_number | nvarchar(50) | Y |
| license_state | nvarchar(50) | Y |
| mobile_phone_number | nvarchar(50) | Y |
| other_phone_number | nvarchar(max) | Y |
| postal_code | nvarchar(50) | Y |
| region | nvarchar(50) | Y |
| start_date | nvarchar(50) | Y |

_+ 16 more columns (truncated for brevity):_ street_address, street_address_line_2, work_phone_number, last_api_request, last_web_access, last_mobile_app_access, hourly_labor_rate_cents, attachment_permissions, custom_fields, default_image_url, account_membership_id, created_at, updated_at, row_hash, contact_status, account_membership

### `std.fleetio_part_location_details`  (rows: 456 | cols: 46)

| Column | Type | Null? |
|---|---|---|
| id | bigint | Y |
| updated_at | datetime2 | Y |
| synced_at_utc | datetime2 | Y |
| account_id | bigint | Y |
| active | bit | Y |
| aisle | nvarchar(50) | Y |
| available_quantity_updated_at | datetime2 | Y |
| bin | nvarchar(50) | Y |
| created_at | datetime2 | Y |
| last_printed_at | datetime2 | Y |
| part_archived_at | datetime2 | Y |
| part_id | bigint | Y |
| part_location_archived_at | datetime2 | Y |
| part_location_id | bigint | Y |
| reorder_point_enabled | bit | Y |
| reorder_point_lead_time_days | int | Y |
| reorder_quantity_lead_time_days | int | Y |
| row | nvarchar(50) | Y |
| track_inventory | bit | Y |
| watchers_count | int | Y |
| available_quantity | decimal | Y |
| average_unit_cost_cents | decimal | Y |
| quantity_allocated_to_work_orders | decimal | Y |
| quantity_on_hand | decimal | Y |
| quantity_on_order | decimal | Y |
| quantity_requested | decimal | Y |
| reorder_point | decimal | Y |
| reorder_quantity | decimal | Y |
| total_inventory_value_cents | decimal | Y |
| part_description | nvarchar(2000) | Y |

_+ 16 more columns (truncated for brevity):_ part_manufacturer_part_number, part_measurement_unit_id, part_number, part_part_category_id, part_part_manufacturer_id, part_upc, part_unit_cost_cents, part_created_at, part_updated_at, part_location_name, part_location_description, part_location_account_id, part_location_created_at, part_location_updated_at, part_location_metadata_has_work_orders, part_location_metadata_has_active_work_orders

### `std.fleetio_shift_type_backfill`  (rows: 617,759 | cols: 2 | PK: inspection_id)

| Column | Type | Null? |
|---|---|---|
| **inspection_id** | bigint | N |
| shift_type | nvarchar(50) | Y |

### `std.fleetio_vehicle_renewals`  (rows: 1,245 | cols: 22)

| Column | Type | Null? |
|---|---|---|
| id | int | Y |
| active | bit | Y |
| vehicle_renewal_type_id | int | Y |
| license_plate | varchar(50) | Y |
| vin | varchar(50) | Y |
| make | varchar(50) | Y |
| due_soon_time_threshold_interval | int | Y |
| vehicle_name | varchar(100) | Y |
| next_due_at | datetimeoffset | Y |
| due_soon_at | datetimeoffset | Y |
| vehicle_archived_at | varchar(max) | Y |
| inserted_at | datetimeoffset | Y |
| vehicle_id | int | Y |
| due_soon_time_threshold_frequency | varchar(50) | Y |
| last_sent_at | datetimeoffset | Y |
| updated_at | datetimeoffset | Y |
| comments_count | int | Y |
| trim | varchar(50) | Y |
| model | varchar(50) | Y |
| created_at | datetimeoffset | Y |
| vehicle_renewal_reminder_status | varchar(50) | Y |
| vehicle_renewal_type_name | varchar(max) | Y |

### `std.fleetio_vehicle_statuses`  (rows: 12 | cols: 9)

| Column | Type | Null? |
|---|---|---|
| id | nvarchar(20) | N |
| created_at | nvarchar(max) | Y |
| account_id | nvarchar(max) | Y |
| position | nvarchar(max) | Y |
| ingested_at | nvarchar(max) | Y |
| name | nvarchar(150) | Y |
| default | nvarchar(max) | Y |
| updated_at | nvarchar(max) | Y |
| color | nvarchar(max) | Y |

### `ref.fleetio_vehicle_purchase_details`  (rows: 748 | cols: 22)

| Column | Type | Null? |
|---|---|---|
| id | bigint | Y |
| vehicle_vin | varchar(max) | Y |
| price_cents | bigint | Y |
| vehicle_color | varchar(max) | Y |
| inserted_at | datetimeoffset | Y |
| vehicle_id | bigint | Y |
| updated_at | datetimeoffset | Y |
| vehicle_make | varchar(max) | Y |
| warranty_expiration_date | varchar(max) | Y |
| vendor_id | varchar(max) | Y |
| vehicle_default_image_url_small | varchar(max) | Y |
| warranty_expiration_meter_value | varchar(max) | Y |
| vehicle_trim | varchar(max) | Y |
| date | varchar(max) | Y |
| vehicle_license_plate | varchar(max) | Y |
| vehicle_model | varchar(max) | Y |
| vehicle_name | varchar(max) | Y |
| vehicle_year | bigint | Y |
| comment | varchar(max) | Y |
| vehicle_registration_state | varchar(max) | Y |
| created_at | datetimeoffset | Y |
| vehicle_registration_expiration_month | bigint | Y |

### `std.service_tasks`  (rows: 1,846 | cols: 15)

| Column | Type | Null? |
|---|---|---|
| id | bigint | Y |
| name | nvarchar(max) | Y |
| description | nvarchar(max) | Y |
| expected_duration_in_seconds | bigint | Y |
| created_at | nvarchar(max) | Y |
| updated_at | nvarchar(max) | Y |
| archived_at | nvarchar(max) | Y |
| subtasks | nvarchar(max) | Y |
| default_vmrs_reason_for_repair | nvarchar(max) | Y |
| default_vmrs_system_group | nvarchar(max) | Y |
| default_vmrs_system | nvarchar(max) | Y |
| default_vmrs_assembly | nvarchar(max) | Y |
| default_vmrs_component | nvarchar(max) | Y |
| service_task_name | nvarchar(max) | Y |
| default_reason_for_repair_code | nvarchar(max) | Y |

### `std.vehicle_inspections`  (rows: 647 | cols: 53 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | varchar(50) | N |
| inspection_number | varchar(50) | N |
| template_version | smallint | N |
| shift | varchar(50) | N |
| location | varchar(100) | N |
| local_date | date | N |
| device_number_entered | nvarchar(max) | Y |
| device_number_hash | nvarchar(max) | Y |
| driver_paylocity_id_entered | varchar(20) | Y |
| driver_id | varchar(24) | Y |
| driver_employee_id | varchar(20) | Y |
| driver_unresolved | bit | N |
| vehicle_entered | varchar(50) | N |
| vehicle_unresolved | bit | N |
| odometer | int | Y |
| company_phone | varchar(50) | Y |
| exterior_cleanliness_rating | smallint | Y |
| significant_damages | varchar(50) | Y |
| interior_cleanliness_rating | smallint | Y |
| has_car_seat | varchar(20) | Y |
| detachable_headrest | varchar(20) | Y |
| strap_pads | varchar(20) | Y |
| crotch_protection_pad | varchar(20) | Y |
| infant_insert | varchar(20) | Y |
| sudden_impact_padding | varchar(20) | Y |
| phone_charging_cable | varchar(20) | Y |
| service_brakes | varchar(20) | Y |
| horn | varchar(20) | Y |
| head_lamps_brake_lights_blinkers | varchar(20) | Y |
| windshield | varchar(20) | Y |

_+ 23 more columns (truncated for brevity):_ wipers_washers, rearview_mirrors, safety_equipment, uber_sticker, tire_pressure, vehicle_condition, personal_belongings, outcome, failed_item_keys, critical_item_keys, photo_count, signature_pathname, blob_pathnames, status, purge_after, started_at, submitted_at, client_ip, user_agent, created_at, updated_at, schema_version, comments

<!-- AUTO:END tables -->
