# Uber Trips & Drivers

Covers trip activity, driver activity/quality/performance, payments/transactions, and Uber-side driver/org/vehicle reference data, for the EV and WAV fleets.

See [`00_START_HERE.md`](00_START_HERE.md) for join keys and the AV/EV/WAV convention.

## Table families

- **`*_trip_activity`** — one row per completed trip: `trip_uuid`, `driver_uuid`, `vehicle_uuid`, **`license_plate`** (the join key to Fleetio/Samsara vehicle data), `trip_request_time`/`trip_drop_off_time`, `pickup_address`/`drop_off_address`, `trip_distance`, `product_type` (e.g. `Electric`, `Pocket Dispatch` — different Uber product lines dispatched to the same driver/vehicle), `trip_date`. **This is the table used to reconcile Samsara safety events to a driver** — match on `license_plate` + a time window around the event (see `alert_operations.py`'s `cd` subquery pattern: prefer a trip where the event time falls strictly between request/drop-off, fall back to closest-by-time within a window otherwise).
- **`*_driver_activity`** — per-driver-per-period online/trip summary (`TripsCompleted`, `TimeOnline_Days_hours_mins`, `TimeOnTrip__Days_hours_mins`, `StartTime`/`EndTime` bounding the period).
- **`*_driver_quality`** — per-driver-per-period rating/reliability metrics (`acceptance_rate`, `cancellation_rate`, `completion_rate`, `driver_ratings_last_4_weeks`, etc.). Note `start_time`/`end_time` are stored as `nvarchar`, not a date type — cast before comparing/sorting.
- **`*_driver_payments`** — per-driver-per-period earnings breakdown (`TotalEarnings`, `NetFare`, `Payouts`, `Tip`, `BookingFee`, etc.) — a rollup, less granular than `uber_driver_trip_payments` below.
- **`std.uber_ev_driver_performance`** (EV only) — similar earnings/hours metrics but sourced from a different report (all columns `nvarchar(500)` — cast before doing math), keyed by internal `_id` rather than driver UUID directly (driver identified via `Driver_Email`/name columns instead).
- **`std.uber_ev_driver_locations`** / **`std.uber_ev_timeline`** (EV only) — granular ping-level driver GPS/status history, epoch-millisecond timestamped (`LocationEpochMs`/`EventEpochMs`) alongside a converted UTC/Pacific pair (`LocationUtc`/`LocationPt`, `EventUtc`/`EventPt`). `uber_ev_driver_locations` currently has very few rows (175) — likely a newer/lightly-used feed; `uber_ev_timeline` is large (3.6M rows) and is the richer of the two.
- **`*_driver_transactions`** / **`std.uber_driver_trip_payments`** / **`std.uber_org_payments`** — the most granular financial detail, transaction- and trip-level. `uber_driver_trip_payments` (5.1M rows, 68 columns, PK `transaction_UUID`) is the widest table in the whole database's analysis layer — nearly every column is a specific Uber pay-component breakdown (`Paid_to_you_Your_earnings_Fare_Surge`, `..._Promotion_Boost`, `..._Refunds_Toll`, etc.). Reach for `PaidToYou`/`YourEarnings`/`Tip` on the narrower `*_driver_transactions` tables for a quick total; use `uber_driver_trip_payments` only when a specific pay-component breakdown is actually needed.
- **`*_auto_pos`** (auto-repositioning) — records of Uber's automatic driver-repositioning prompts (`Repositioning_Prompt_Outcome`, `Navigation_Outcome`, source/destination lat-lng). Niche/operational, not typically needed for HR or safety analysis.
- **`std.uber_ev_rtd_offers`** (EV only, "ride type dispatch" offers) — per-offer detail including whether the driver took the trip (`driver_took_trip`), cancellation reason, and **shift/clock-out context** (`shift_start_time`, `shift_end_time`, `clock_out`) — useful for offer-acceptance analysis tied to shift timing.

## Reference tables

- **`ref.uber_drivers`** — the driver roster/profile directory: `driverUuid`, name, `phone`/`email`, `licensePlate`, `onboardingStatus`, `latestStatus`, and **`org_name`**/`source_org_id`. This is the table that resolves a `driver_uuid` to a human-readable Uber org — join to `ref.uber_orgs` on `org_name` = `Org Name` to get the org's short ID for building supplier-portal links (`https://supplier.uber.com/orgs/{Org ID}/drivers/{driverUuid}`).
- **`ref.uber_orgs`** — tiny lookup (7 rows): `Org Name`, `Org ID`, `Org Branch`. Note the column names contain spaces — bracket-quote them (`[Org Name]`).
- **`ref.uber_vehicles`** — Uber's own vehicle registry (separate from Fleetio) — VIN, make/model/year, `license_plate`, `owner_id`, `compliance`/`assignments` (raw JSON-ish text, not further decomposed).
- **`ref.uber_shift_logs`** (+ `_wav` variant) — a log of shift start/end postings to Uber's API (`shift.start_time_utc`/`shift.end_time_utc`, plus `uber_post_status`/`uber_get_status` HTTP-style status codes) — this looks like an integration/sync audit trail rather than a business fact table; useful for debugging why a shift didn't sync, less useful for driver-activity analysis (use `*_driver_activity` for that).

<!-- AUTO:BEGIN tables (regenerated daily by scripts/regenerate.py — do not hand-edit below this line) -->
### `std.uber_ev_trip_activity`  (rows: 7,149,709 | cols: 21 | PK: trip_uuid)

| Column | Type | Null? |
|---|---|---|
| **trip_uuid** | nvarchar(36) | N |
| driver_uuid | nvarchar(36) | Y |
| driver_first_name | nvarchar(100) | Y |
| driver_last_name | nvarchar(100) | Y |
| vehicle_uuid | nvarchar(36) | Y |
| license_plate | nvarchar(50) | Y |
| service_type | nvarchar(100) | Y |
| product_type | nvarchar(100) | Y |
| trip_request_time | datetime2 | Y |
| trip_drop_off_time | datetime2 | Y |
| pickup_address | nvarchar(500) | Y |
| drop_off_address | nvarchar(500) | Y |
| trip_distance | float | Y |
| trip_status | nvarchar(50) | Y |
| trip_date | date | Y |
| lat | float | Y |
| lng | float | Y |
| lat2 | float | Y |
| lng2 | float | Y |
| _sync_year | int | Y |
| is_teen_trip | nvarchar(10) | Y |

### `std.uber_wav_trip_activity`  (rows: 432,191 | cols: 22 | PK: trip_uuid)

| Column | Type | Null? |
|---|---|---|
| **trip_uuid** | nvarchar(36) | N |
| driver_uuid | nvarchar(36) | Y |
| driver_first_name | nvarchar(100) | Y |
| driver_last_name | nvarchar(100) | Y |
| vehicle_uuid | nvarchar(36) | Y |
| license_plate | nvarchar(50) | Y |
| service_type | nvarchar(100) | Y |
| product_type | nvarchar(100) | Y |
| trip_request_time | datetime2 | Y |
| trip_drop_off_time | datetime2 | Y |
| pickup_address | nvarchar(500) | Y |
| drop_off_address | nvarchar(500) | Y |
| trip_distance | float | Y |
| trip_status | nvarchar(50) | Y |
| trip_date | date | Y |
| lat | float | Y |
| lng | float | Y |
| lat2 | float | Y |
| lng2 | float | Y |
| _sync_year | int | Y |
| source_org_id | nvarchar(50) | Y |
| is_teen_trip | nvarchar(10) | Y |

### `std.uber_ev_driver_activity`  (rows: 506,532 | cols: 8 | PK: DriverUUID, StartTime)

| Column | Type | Null? |
|---|---|---|
| **DriverUUID** | nvarchar(255) | N |
| FirstName | nvarchar(50) | Y |
| LastName | nvarchar(50) | Y |
| TripsCompleted | int | Y |
| TimeOnline_Days_hours_mins | nvarchar(50) | Y |
| TimeOnTrip__Days_hours_mins | nvarchar(50) | Y |
| **StartTime** | datetime2 | N |
| EndTime | datetime2 | Y |

### `std.uber_wav_driver_activity`  (rows: 41,638 | cols: 9 | PK: DriverUUID, StartTime)

| Column | Type | Null? |
|---|---|---|
| **DriverUUID** | nvarchar(255) | N |
| FirstName | nvarchar(100) | Y |
| LastName | nvarchar(100) | Y |
| TripsCompleted | int | Y |
| TimeOnline_Days_hours_mins | nvarchar(50) | Y |
| TimeOnTrip__Days_hours_mins | nvarchar(50) | Y |
| **StartTime** | datetime2 | N |
| EndTime | datetime2 | Y |
| source_org_id | nvarchar(50) | Y |

### `std.uber_ev_driver_quality`  (rows: 515,320 | cols: 13 | PK: driver_uuid, start_time)

| Column | Type | Null? |
|---|---|---|
| **driver_uuid** | nvarchar(255) | N |
| **start_time** | nvarchar(50) | N |
| end_time | nvarchar(50) | N |
| driver_first_name | nvarchar(50) | Y |
| driver_last_name | nvarchar(50) | Y |
| trips_completed | float | Y |
| acceptance_rate | float | Y |
| cancellation_rate | float | Y |
| completion_rate | float | Y |
| driver_ratings_last_4_weeks | float | Y |
| driver_ratings_previous_500_trips | float | Y |
| drivers_current_acceptance_rate | float | Y |
| drivers_current_cancellation_rate | float | Y |

### `std.uber_wav_driver_quality`  (rows: 30,202 | cols: 14 | PK: driver_uuid, start_time)

| Column | Type | Null? |
|---|---|---|
| **driver_uuid** | nvarchar(255) | N |
| **start_time** | nvarchar(50) | N |
| end_time | nvarchar(50) | N |
| driver_first_name | nvarchar(255) | Y |
| driver_last_name | nvarchar(255) | Y |
| trips_completed | float | Y |
| acceptance_rate | float | Y |
| cancellation_rate | float | Y |
| completion_rate | float | Y |
| driver_ratings_last_4_weeks | float | Y |
| driver_ratings_previous_500_trips | float | Y |
| drivers_current_acceptance_rate | float | Y |
| drivers_current_cancellation_rate | float | Y |
| source_org_id | nvarchar(50) | Y |

### `std.uber_ev_driver_payments`  (rows: 636,196 | cols: 16 | PK: DriverUUID, StartTime)

| Column | Type | Null? |
|---|---|---|
| **DriverUUID** | nvarchar(255) | N |
| DriverFirstName | nvarchar(50) | Y |
| DriverLastName | nvarchar(50) | Y |
| TotalEarnings | float | Y |
| NetFare | float | Y |
| RefundsAndExpenses | float | Y |
| Payouts | float | Y |
| PromotionsAdvantangeMode | float | Y |
| BookingFee | float | Y |
| Tip | float | Y |
| LostItemReturn | float | Y |
| PaymentforInprogresseatsorderPromotions | float | Y |
| RefundsAirportFee | float | Y |
| **StartTime** | datetime2 | N |
| EndTime | datetime2 | N |
| ReportId | nvarchar(100) | Y |

### `std.uber_wav_driver_payments`  (rows: 27,762 | cols: 17 | PK: DriverUUID, StartTime)

| Column | Type | Null? |
|---|---|---|
| **DriverUUID** | nvarchar(255) | N |
| DriverFirstName | nvarchar(100) | Y |
| DriverLastName | nvarchar(100) | Y |
| TotalEarnings | float | Y |
| NetFare | float | Y |
| RefundsAndExpenses | float | Y |
| Payouts | float | Y |
| PromotionsAdvantangeMode | float | Y |
| BookingFee | float | Y |
| Tip | float | Y |
| LostItemReturn | float | Y |
| PaymentforInprogresseatsorderPromotions | float | Y |
| RefundsAirportFee | float | Y |
| **StartTime** | datetime2 | N |
| EndTime | datetime2 | N |
| ReportId | nvarchar(100) | Y |
| source_org_id | nvarchar(50) | Y |

### `std.uber_ev_driver_locations`  (rows: 95 | cols: 11 | PK: DriverUuid, LocationEpochMs)

| Column | Type | Null? |
|---|---|---|
| **DriverUuid** | nvarchar(64) | N |
| Latitude | float | Y |
| Longitude | float | Y |
| Bearing | float | Y |
| Speed | float | Y |
| Status | nvarchar(64) | Y |
| **LocationEpochMs** | bigint | N |
| LocationUtc | datetime2 | Y |
| LocationPt | datetime2 | Y |
| OrgId | nvarchar(255) | Y |
| FetchedAt | datetime2 | N |

### `std.uber_ev_driver_performance`  (rows: 204,240 | cols: 18 | PK: _id)

| Column | Type | Null? |
|---|---|---|
| **_id** | int | N |
| StartTime | datetime2 | N |
| EndTime | datetime2 | N |
| Organization | nvarchar(255) | N |
| Driver_First_Name | nvarchar(500) | Y |
| Driver_Last_Name | nvarchar(500) | Y |
| Driver_Email | nvarchar(500) | Y |
| Driver_Phone | nvarchar(500) | Y |
| Total_Earnings | nvarchar(500) | Y |
| Earnings_per_hr | nvarchar(500) | Y |
| Cash_Collected | nvarchar(500) | Y |
| Trips_per_hr | nvarchar(500) | Y |
| Hours_Online | nvarchar(500) | Y |
| Hours_On_Trip | nvarchar(500) | Y |
| Hours_On_Job | nvarchar(500) | Y |
| Trips_Taken | nvarchar(500) | Y |
| Acceptance_Rate | nvarchar(500) | Y |
| Cancellation_Rate | nvarchar(500) | Y |

### `std.uber_ev_driver_transactions`  (rows: 1,340,763 | cols: 11)

| Column | Type | Null? |
|---|---|---|
| TransactionUuid | nvarchar(max) | Y |
| TripUuid | nvarchar(max) | Y |
| ProcessedAt | datetimeoffset | Y |
| Description | nvarchar(50) | Y |
| DriverUuid | nvarchar(max) | Y |
| FirstName | nvarchar(50) | Y |
| LastName | nvarchar(50) | Y |
| PaidToYou | float | Y |
| YourEarnings | float | Y |
| Tip | float | Y |
| Organization | nvarchar(50) | Y |

### `std.uber_wav_driver_transactions`  (rows: 98,660 | cols: 12)

| Column | Type | Null? |
|---|---|---|
| TransactionUuid | nvarchar(max) | Y |
| TripUuid | nvarchar(max) | Y |
| ProcessedAt | datetimeoffset | Y |
| Description | nvarchar(max) | Y |
| DriverUuid | nvarchar(max) | Y |
| FirstName | nvarchar(max) | Y |
| LastName | nvarchar(max) | Y |
| PaidToYou | float | Y |
| YourEarnings | float | Y |
| Tip | float | Y |
| Organization | nvarchar(max) | Y |
| source_org_id | nvarchar(50) | Y |

### `std.uber_ev_auto_pos`  (rows: 177,762 | cols: 19 | PK: _id)

| Column | Type | Null? |
|---|---|---|
| **_id** | int | N |
| Driver_UUID | nvarchar(500) | Y |
| Driver_name | nvarchar(100) | Y |
| Repositioning_Prompt_Timestamp | nvarchar(50) | Y |
| Repositioning_Prompt_Outcome | nvarchar(50) | Y |
| Navigation_Outcome | nvarchar(200) | Y |
| Actual_Distance_Traveled__km | nvarchar(50) | Y |
| Actual_Time_Traveled__min | nvarchar(50) | Y |
| Recommended_Navigation_Distance__km | nvarchar(50) | Y |
| Source_Latitude | nvarchar(50) | Y |
| Source_Longitude | nvarchar(50) | Y |
| Destination_Latitude | nvarchar(50) | Y |
| Destination_Longitude | nvarchar(50) | Y |
| Trip_Before_Repositioning_Timestamp | nvarchar(50) | Y |
| Trip_Before_Repositioning_UUID | nvarchar(500) | Y |
| Next_Dispatch_Sent_Timestamp | nvarchar(50) | Y |
| Next_Dispatch_Send_UUID | nvarchar(500) | Y |
| Next_Dispatch_Accepted_Timestamp | nvarchar(50) | Y |
| Next_Dispatch_Accepted_Trip_UUID | nvarchar(500) | Y |

### `std.uber_wav_auto_pos`  (rows: 2,277 | cols: 20 | PK: _id)

| Column | Type | Null? |
|---|---|---|
| **_id** | int | N |
| source_org_id | nvarchar(500) | Y |
| Driver_UUID | nvarchar(500) | Y |
| Driver_name | nvarchar(500) | Y |
| Repositioning_Prompt_Timestamp | nvarchar(500) | Y |
| Repositioning_Prompt_Outcome | nvarchar(500) | Y |
| Navigation_Outcome | nvarchar(500) | Y |
| Actual_Distance_Traveled__km | nvarchar(500) | Y |
| Actual_Time_Traveled__min | nvarchar(500) | Y |
| Recommended_Navigation_Distance__km | nvarchar(500) | Y |
| Source_Latitude | nvarchar(500) | Y |
| Source_Longitude | nvarchar(500) | Y |
| Destination_Latitude | nvarchar(500) | Y |
| Destination_Longitude | nvarchar(500) | Y |
| Trip_Before_Repositioning_Timestamp | nvarchar(500) | Y |
| Trip_Before_Repositioning_UUID | nvarchar(500) | Y |
| Next_Dispatch_Sent_Timestamp | nvarchar(500) | Y |
| Next_Dispatch_Send_UUID | nvarchar(500) | Y |
| Next_Dispatch_Accepted_Timestamp | nvarchar(500) | Y |
| Next_Dispatch_Accepted_Trip_UUID | nvarchar(500) | Y |

### `std.uber_ev_rtd_offers`  (rows: 14,766 | cols: 22 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | bigint | N |
| datestr | date | Y |
| driver_uuid | uniqueidentifier | Y |
| rtd_offer_created_at | datetime2 | Y |
| driver_lat_at_offer | float | Y |
| driver_lng_at_offer | float | Y |
| driver_took_trip | bit | Y |
| pickup_request_lat | float | Y |
| pickup_request_lng | float | Y |
| pickup_actual_lat | float | Y |
| pickup_actual_lng | float | Y |
| dropoff_lat | float | Y |
| dropoff_lng | float | Y |
| offer_state | varchar(30) | Y |
| driver_cancelled | varchar(20) | Y |
| canceled_reason | varchar(30) | Y |
| trip_status | varchar(30) | Y |
| shift_start_time | datetimeoffset | Y |
| shift_end_time | datetimeoffset | Y |
| end_shift_fleetio_started | datetimeoffset | Y |
| end_shift_fleetio_submitted | datetimeoffset | Y |
| clock_out | datetime2 | Y |

### `std.uber_ev_timeline`  (rows: 3,642,269 | cols: 10 | PK: DriverUuid, Event, EventEpochMs)

| Column | Type | Null? |
|---|---|---|
| **DriverUuid** | nvarchar(64) | N |
| **Event** | nvarchar(64) | N |
| Status | nvarchar(64) | Y |
| Latitude | float | Y |
| Longitude | float | Y |
| **EventEpochMs** | bigint | N |
| EventUtc | datetime2 | Y |
| EventPt | datetime2 | Y |
| OrgId | nvarchar(255) | Y |
| FetchedAt | datetime2 | N |

### `std.uber_driver_trip_payments`  (rows: 5,141,346 | cols: 68 | PK: transaction_UUID)

| Column | Type | Null? |
|---|---|---|
| **transaction_UUID** | nvarchar(450) | N |
| DriverUUID | nvarchar(max) | Y |
| StartTime | datetime2 | Y |
| EndTime | datetime2 | Y |
| ReportId | nvarchar(max) | Y |
| Driver_first_name | nvarchar(max) | Y |
| Driver_last_name | nvarchar(max) | Y |
| Trip_UUID | nvarchar(max) | Y |
| Description | nvarchar(max) | Y |
| Organization_name | nvarchar(max) | Y |
| Org_alias | nvarchar(max) | Y |
| vs_reporting | nvarchar(max) | Y |
| Paid_to_you | nvarchar(max) | Y |
| Paid_to_you___Your_earnings | nvarchar(max) | Y |
| Paid_to_you___Trip_balance___Payouts___Cash_Collected | nvarchar(max) | Y |
| Paid_to_you___Your_earnings___Fare | nvarchar(max) | Y |
| Paid_to_you___Your_earnings___Taxes | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Fare | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Promotion_Commercial_Supplement | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Promotion_Advantage_Mode | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Tip | nvarchar(max) | Y |
| Paid_to_you_Trip_balance_Refunds_Airport_Fee | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Wait_Time_at_Pickup | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Delayed_ride_guarantee | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Time_at_Stop | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Surge | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_UberX_Priority | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Cancellation | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Promotion_Driver_Event_Surcharge | nvarchar(max) | Y |
| Paid_to_you_Your_earnings_Fare_Fare_Adjustment | nvarchar(max) | Y |

_+ 38 more columns (truncated for brevity):_ Paid_to_you_Your_earnings_Fare_Additional_cancellation_fee_for_extended_wait_time, Paid_to_you_Your_earnings_Service_Fee, Paid_to_you_Your_earnings_Fare_Adjustment, Paid_to_you_Trip_balance_Refunds_Cleaning___Repairs, Paid_to_you_Your_earnings_Promotion_Promotion, Paid_to_you_Trip_balance_Expenses_Airport_Fee, Paid_to_you_Trip_balance_Payouts_Transferred_To_Bank_Account, Paid_to_you_Your_earnings_Other_earnings_Payment_for_past_trip, Paid_to_you_Your_earnings_Other_earnings_Cancellation_Charges, Paid_to_you_Trip_balance_Refunds_Customer_Support_Miscellaneous_Payment, Paid_to_you_Your_earnings_Other_earnings_Lost_Item_Return, Paid_to_you_Your_earnings_Fare_Package_Fare, Paid_to_you_Your_earnings_Fare_Additional_distance_charges, Paid_to_you_Your_earnings_Fare_Additional_time_charges, Paid_to_you_Your_earnings_Fare_Reserve_Fare_Premium, Paid_to_you_Your_earnings_Other_earnings_Adjustment, Paid_to_you_Your_earnings_Fare_Trip_Supplement, Paid_to_you_Your_earnings_Other_earnings_Non_trip_earnings_misc, Paid_to_you_Your_earnings_Other_earnings_Other, Paid_to_you_Your_earnings_Other_earnings_Prop_22_earnings_guarantee, Paid_to_you_Trip_balance_Refunds_Non_trip_balance_misc, Paid_to_you_Your_earnings_Fare_Booking_Fee, Paid_to_you_Your_earnings_Fare_Reservation_Fee, Paid_to_you_Your_earnings_Other_earnings_Pet_Surcharge, Paid_to_you_Your_earnings_Promotion_Boost, Paid_to_you_Your_earnings_Promotion_Quest, Paid_to_you_Trip_balance_Refunds_Toll, Paid_to_you_Your_earnings_Other_earnings_Healthcare_Stipend, Paid_to_you_Your_earnings_Fare_Shared_Rides_Match_Savings, Paid_to_you_Your_earnings_Other_earnings_Shared_Rides_Service_Fee_Adjustment, Paid_to_you_Your_earnings_Promotion_Commission_for_platform_promotion_and_development_granted_by_Uber_BV, Paid_to_you_Your_earnings_Other_earnings_Payment_for_In_progress_eats_order, Paid_to_you_Your_earnings_Taxes_Withholding_Tax, Paid_to_you_Your_earnings_Other_fees_Pet_Surcharge, Paid_to_you_Your_earnings_Other_fees_Adjustment, Paid_to_you_Your_earnings_Promotion_Comfort___XL_Fee, Paid_to_you_Trip_balance_Refunds_Upside_Cashback, Paid_to_you_Your_earnings_Fare_Intercity_Surcharge

### `std.uber_org_payments`  (rows: 610 | cols: 51 | PK: Organization_UUID, StartTime)

| Column | Type | Null? |
|---|---|---|
| **Organization_UUID** | nvarchar(255) | N |
| **StartTime** | datetime2 | N |
| EndTime | datetime2 | N |
| ReportId | nvarchar(100) | Y |
| Organization_name | nvarchar(500) | Y |
| Org_alias | nvarchar(500) | Y |
| Driver_first_name | nvarchar(500) | Y |
| Driver_last_name | nvarchar(500) | Y |
| Start_of_period_balance | float | Y |
| End_of_period_balance | float | Y |
| Total_Earnings | float | Y |
| Total_Earnings___Net_Fare | float | Y |
| Refunds___Expenses | float | Y |
| Payouts | nvarchar(500) | Y |
| Total_Earnings_Promotions | float | Y |
| Total_Earnings_Tip | float | Y |
| Refunds___Expenses_Refunds_Airport_Fee | float | Y |
| Refunds___Expenses_Refunds_Cleaning___Repairs | float | Y |
| Total_Earnings_Net_Fare_Booking_Fee | float | Y |
| Total_Earnings_Other_earnings_Lost_Item_Return | float | Y |
| Total_Earnings_Other_earnings_Pet_Surcharge | float | Y |
| Payouts_Transferred_To_Bank_Account | float | Y |
| Total_Earnings_Other_earnings_Adjustment | float | Y |
| Total_Earnings_Other_earnings_Other | float | Y |
| Total_Earnings_Other_earnings_Payment_for_past_trip | float | Y |
| Payouts_Cash_Collected | float | Y |
| Refunds___Expenses_Refunds_Customer_Support_Miscellaneous_Payment | float | Y |
| Refunds___Expenses_Refunds_Non_trip_balance_misc | float | Y |
| Total_Earnings_Promotions_Advantage_Mode | float | Y |
| Total_Earnings_Other_earnings_Prop_22_earnings_guarantee | float | Y |

_+ 21 more columns (truncated for brevity):_ Total_Earnings_Other_earnings_Non_trip_earnings_misc, Total_Earnings_Other_earnings_Cancellation_Charges, Total_Earnings_Other_earnings_Payment_for_In_progress_eats_order, Total_Earnings_Taxes, Total_Earnings_Other_fees_Pet_Surcharge, Refunds___Expenses_Refunds_Toll, Total_Earnings_Other_earnings_Shared_Rides_Service_Fee_Adjustment, Total_Earnings_Other_earnings_Healthcare_Stipend, payouts_date, DriverUUID, DriverFirstName, DriverLastName, TotalEarnings, NetFare, RefundsAndExpenses, PromotionsAdvantangeMode, BookingFee, Tip, LostItemReturn, PaymentforInprogresseatsorderPromotions, RefundsAirportFee

### `ref.uber_drivers`  (rows: 63,880 | cols: 11)

| Column | Type | Null? |
|---|---|---|
| onboardingStatus | nvarchar(100) | Y |
| driverUuid | nvarchar(100) | Y |
| firstName | nvarchar(100) | Y |
| lastName | nvarchar(100) | Y |
| phone | nvarchar(50) | Y |
| email | nvarchar(200) | Y |
| licensePlate | nvarchar(50) | Y |
| latestStatus | nvarchar(50) | Y |
| latestStatusTimestamp | nvarchar(50) | Y |
| org_name | nvarchar(100) | Y |
| source_org_id | nvarchar(max) | Y |

### `ref.uber_orgs`  (rows: 7 | cols: 3)

| Column | Type | Null? |
|---|---|---|
| Org Name | nvarchar(50) | Y |
| Org ID | nvarchar(50) | Y |
| Org Branch | nvarchar(50) | Y |

### `ref.uber_vehicles`  (rows: 684 | cols: 15 | PK: _id)

| Column | Type | Null? |
|---|---|---|
| **_id** | int | N |
| id | nvarchar(max) | Y |
| owner_id | nvarchar(max) | Y |
| make | nvarchar(max) | Y |
| model | nvarchar(max) | Y |
| year | bigint | Y |
| last_updated | datetime2 | Y |
| license_plate | nvarchar(max) | Y |
| color_name | nvarchar(max) | Y |
| color_hex_code | nvarchar(max) | Y |
| vin | nvarchar(max) | Y |
| compliance | nvarchar(max) | Y |
| assignments | nvarchar(max) | Y |
| inserted_at | datetime2 | Y |
| source_org_id | nvarchar(max) | Y |

### `ref.uber_shift_logs`  (rows: 1,371,868 | cols: 16)

| Column | Type | Null? |
|---|---|---|
| driver_id | nvarchar(100) | Y |
| employeeId | int | Y |
| cost_center | nvarchar(50) | Y |
| shift.start_time_utc | datetime | Y |
| shift.end_time_utc | datetime | Y |
| startDateTime | datetime | Y |
| durationMinutes | int | Y |
| shift.metadata.start_location.latitude | float | Y |
| shift.metadata.start_location.longitude | float | Y |
| shift.metadata.end_location.latitude | float | Y |
| shift.metadata.end_location.longitude | float | Y |
| uber_post_status | int | Y |
| uber_post_response | nvarchar(50) | Y |
| uber_get_status | int | Y |
| uber_get_response | nvarchar(max) | Y |
| logged_at | datetime | Y |

### `ref.uber_shift_logs_wav`  (rows: 7,698 | cols: 16)

| Column | Type | Null? |
|---|---|---|
| driver_id | nvarchar(100) | Y |
| employeeId | int | Y |
| cost_center | nvarchar(50) | Y |
| shift.start_time_utc | datetime | Y |
| shift.end_time_utc | datetime | Y |
| startDateTime | datetime | Y |
| durationMinutes | int | Y |
| shift.metadata.start_location.latitude | float | Y |
| shift.metadata.start_location.longitude | float | Y |
| shift.metadata.end_location.latitude | float | Y |
| shift.metadata.end_location.longitude | float | Y |
| uber_post_status | int | Y |
| uber_post_response | nvarchar(50) | Y |
| uber_get_status | int | Y |
| uber_get_response | nvarchar(max) | Y |
| logged_at | datetime | Y |

<!-- AUTO:END tables -->
