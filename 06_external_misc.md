# External Systems & Misc

Assorted external-system integrations that don't fit the core HR/Uber/Fleetio/Samsara domains.

## Tables

- **`ref.freshsales_contacts`** — Tower's CRM (Freshsales), used for the **recruiting/hiring pipeline**, not general sales. 228 columns — the vast majority are `custom_field_cf_*` recruiting-workflow fields: background-check status (`cf_uber_bgc_*`, `cf_lyft_bgc_*`, `cf_wmata_bgc_*`), interview scheduling (`cf_phone_interview_*`, `cf_inperson_interview_*`), driving test results (`cf_drive_test_*`), onboarding milestones (`cf_onboarded_date`, `cf_hired_date`, `cf_real_onboarded_date`), and per-platform account status (`cf_uber_status`, `cf_uber_dl_status`). Core CRM fields (`email`, `first_name`/`last_name`, `job_title`, `tags`, `lead_score`) are also present. This is the richest source for "where is this candidate in the hiring funnel" questions — the equivalent isn't tracked in Paylocity until after hire.
- **`ref.driver_emails`** / **`ref.mail_domains`** — Tower's internal email server (Zimbra-style, based on column names like `quota_used`, `authsource`, `last_imap_login`) — mailbox and domain administration data, not message content. `mail_domains` lists the actual email domains Tower operates.
- **`ref.weather`** / **`ref.weather_codes`** — historical/forecast weather by lat/lng and time (Open-Meteo-style API fields — `temperature_2m`, `precipitation`, `wind_speed_10m`, etc.), with `weather_codes` translating the numeric `weather_code` into a text `meaning`. Likely joined to trip or safety-event data for weather-conditioned analysis (e.g. "were more safety events flagged during rain") — not confirmed as actively used this session.
- **`ref.FuelAndEnergy`** (+ `WAV` variant) — per-vehicle daily energy/fuel consumption from Samsara (`energyUsedKwh`, `fuelConsumedMl`, `distanceTraveledMeters`, `estCarbonEmissionsKg`, `efficiencyMpge`) — note the **unusual dotted column names** (`vehicle.energyType`, `estFuelEnergyCost.amount`) reflecting an unflattened nested API response; bracket-quote these (`[vehicle.energyType]`) when querying.
- **`std.charging_sessions`** — EV charging-station session log (OCPP protocol fields — `chargeBoxSerialNumber`, `meterStart`/`meterStop`, `energyDelivered`, `startedStateOfCharge`/`stoppedStateOfCharge`, `stoppedReason`) — the charging-infrastructure counterpart to `FuelAndEnergy`'s vehicle-side consumption data.
- **`std.epn_review`** — driver license/compliance violation review tracking (`DL Number`, `Violation Date`, `Conviction Date`, `Section(s) Violated`, `Management Decision`/`Recommendation`, linked to `Employee ID`/`Uber ID`). Currently empty (0 rows) — either a new/unused feature or populated ad hoc outside the normal ETL cadence; don't assume it's kept current.

<!-- AUTO:BEGIN tables (regenerated daily by scripts/regenerate.py — do not hand-edit below this line) -->
### `ref.freshsales_contacts`  (rows: 235,598 | cols: 228)

| Column | Type | Null? |
|---|---|---|
| active_sales_sequences | nvarchar(50) | Y |
| address | nvarchar(100) | Y |
| amb_subscription_status | nvarchar(max) | Y |
| avatar | nvarchar(max) | Y |
| city | nvarchar(50) | Y |
| completed_sales_sequences | nvarchar(200) | Y |
| country | nvarchar(50) | Y |
| created_at | nvarchar(50) | Y |
| custom_field_cf_able_to_lift_up_to_40_pounds | nvarchar(50) | Y |
| custom_field_cf_able_to_pass_drug_test | nvarchar(50) | Y |
| custom_field_cf_actual_training_date | nvarchar(50) | Y |
| custom_field_cf_ampm | nvarchar(50) | Y |
| custom_field_cf_are_you_at_least_21_years_old_wav | nvarchar(50) | Y |
| custom_field_cf_are_you_at_least_23_years_old_ev | nvarchar(50) | Y |
| custom_field_cf_assigner | nvarchar(max) | Y |
| custom_field_cf_assigner_lead | nvarchar(max) | Y |
| custom_field_cf_bgc_approved_date | nvarchar(50) | Y |
| custom_field_cf_buisness | nvarchar(50) | Y |
| custom_field_cf_can_you_share_a_time_when_you_did_something_extra_to_make_sure_a_customer_was_really_happy | bigint | Y |
| custom_field_cf_comments | nvarchar(4000) | Y |
| custom_field_cf_communication_skills | bigint | Y |
| custom_field_cf_conditional_offer_sent_date | nvarchar(50) | Y |
| custom_field_cf_confidence | bigint | Y |
| custom_field_cf_confirmed_meeting | nvarchar(50) | Y |
| custom_field_cf_contact_lyfecycle_1 | nvarchar(100) | Y |
| custom_field_cf_daaa_received_date | nvarchar(50) | Y |
| custom_field_cf_daaa_sent_date | nvarchar(50) | Y |
| custom_field_cf_date_applied | nvarchar(50) | Y |
| custom_field_cf_date_of_birth | nvarchar(50) | Y |
| custom_field_cf_days_available_to_work | nvarchar(200) | Y |

_+ 198 more columns (truncated for brevity):_ custom_field_cf_did_dapta_call_the_candidate, custom_field_cf_drive_test_result, custom_field_cf_drive_test_score, custom_field_cf_drive_tester, custom_field_cf_driver_license_state, custom_field_cf_drivers_license_issue_date, custom_field_cf_drivers_license_name, custom_field_cf_drivers_license_number, custom_field_cf_driving_test_result_date, custom_field_cf_drug_test_candidate_request, custom_field_cf_drug_test_information_sent, custom_field_cf_drug_test_result_date, custom_field_cf_drug_test_status, custom_field_cf_emailed_arbitration_agreement, custom_field_cf_fail_screening_reason_lost_reason, custom_field_cf_first_interaction_white_gloves, custom_field_cf_have_you_ever_been_hired_by_tower_wav_or_tower_ev, custom_field_cf_have_you_ever_driven_with_lyft, custom_field_cf_have_you_ever_driven_with_uber, custom_field_cf_have_you_ever_taken_an_uber_black_trip, custom_field_cf_have_you_previously_completed_a_trustline_certification, custom_field_cf_hired_date, custom_field_cf_hired_nondriver, custom_field_cf_hour_ipi_scheduled, custom_field_cf_how_do_you_handle_tough_situations_like_traffic_or_difficult_passengers_while_driving, custom_field_cf_hr_coordinator, custom_field_cf_hrc_inputter, custom_field_cf_hrc_reviewer, custom_field_cf_in_person_interview_add_any_special_requests, custom_field_cf_inperson_interview_agenda_date2, custom_field_cf_inperson_interview_result, custom_field_cf_inperson_interview_result_date, custom_field_cf_inperson_interview_schedule_day, custom_field_cf_inperson_interview_schedule_month, custom_field_cf_inperson_interview_scheduled_date, custom_field_cf_insurance_result_date, custom_field_cf_insurance_status, custom_field_cf_interview_scheduled, custom_field_cf_interviewer_attendance, custom_field_cf_invoice_date, custom_field_cf_ipi_scheduled_time, custom_field_cf_ipi_team_member_scheduled, custom_field_cf_last_interaction_white_gloves, custom_field_cf_lyft_bgc_approved_date, custom_field_cf_lyft_bgc_pending, custom_field_cf_lyft_onboard_date, custom_field_cf_number, custom_field_cf_ok_working_with_wheelchairs, custom_field_cf_onboarded, custom_field_cf_onboarded_date, custom_field_cf_p1_how_would_you_deal_with_passengers_who_are_upset_or_dont_agree_with_you_while_staying_calm_and_profes, custom_field_cf_parttimefull_time, custom_field_cf_pass_screening, custom_field_cf_pbot_registration_id, custom_field_cf_personal_email, custom_field_cf_phone_interview_agenda_date, custom_field_cf_phone_interview_candidate_attended, custom_field_cf_phone_interview_candidate_attended_date, custom_field_cf_phone_interview_candidate_rescheduled_attended_date, custom_field_cf_phone_interview_day, custom_field_cf_phone_interview_month, custom_field_cf_phone_interview_schedule_time, custom_field_cf_phoone_interview_candidate_rescheduled_attended, custom_field_cf_prescreening_pass, custom_field_cf_professional_attire, custom_field_cf_punctuality, custom_field_cf_qa_puntuality_date, custom_field_cf_real_onboarded_date, custom_field_cf_reapply_date, custom_field_cf_reapply_source, custom_field_cf_recruiter_2, custom_field_cf_recruiter_who_sents_to_drug_test, custom_field_cf_rehire_date, custom_field_cf_schedule_training_day, custom_field_cf_schedule_training_moth, custom_field_cf_schedule_training_time, custom_field_cf_scheduled_training_date, custom_field_cf_secondary_source, custom_field_cf_signon_bonus, custom_field_cf_site, custom_field_cf_source_new, custom_field_cf_team, custom_field_cf_termination_date, custom_field_cf_total_score, custom_field_cf_tower_wav_email, custom_field_cf_tower_wav_email_password, custom_field_cf_training_comments, custom_field_cf_transit_bgc_pending, custom_field_cf_transit_medical_registration, custom_field_cf_uber_bgc_approved_date, custom_field_cf_uber_bgc_consent_status, custom_field_cf_uber_bgc_pending, custom_field_cf_uber_dl_status, custom_field_cf_uber_dl_update_timestamp, custom_field_cf_uber_last_status_update_timestamp, custom_field_cf_uber_mvr_bgc_status, custom_field_cf_uber_onboarded_date, custom_field_cf_uber_password, custom_field_cf_uber_phone_number, custom_field_cf_uber_prof_pic_status, custom_field_cf_uber_prosource, custom_field_cf_uber_signup_timestamp, custom_field_cf_uber_status, custom_field_cf_uber_totaltrips, custom_field_cf_waymo_onboarded_date, custom_field_cf_what_email_is_associated_with_your_uber_black_account_please_note_you_can_only_be_part_of_one_uber_black, custom_field_cf_what_is_your_experience_with_technology, custom_field_cf_wmata_bgc_approved_date, custom_field_cf_wmata_medical_qualification_result_date, custom_field_cf_wmata_onboarded_date, custom_field_cf_wmata_registration_sent_date, custom_field_cf_zip_code, customer_fit, description, display_name, email, emails, external_id, facebook, first_campaign, first_medium, first_name, first_seen_chat, first_source, id, is_deleted, job_title, keyword, last_assigned_at, last_campaign, last_contacted, last_contacted_mode, last_contacted_sales_activity_mode, last_contacted_via_sales_activity, last_medium, last_name, last_seen, last_seen_chat, last_source, latest_campaign, latest_medium, latest_source, lead_score, linkedin, links_appointments, links_connections, links_conversations, links_document_associations, links_duplicates, links_notes, links_reminders, links_tasks, links_timeline_feeds, locale, mcr_id, medium, mobile_number, open_deals_amount, open_deals_count, other_unsubscription_reason, phone_numbers, recent_note, sms_subscription_status, state, subscription_status, subscription_types, system_tags, tags, team_user_ids, time_zone, total_sessions, twitter, unsubscription_reason, updated_at, web_form_ids, whatsapp_subscription_status, won_deals_amount, won_deals_count, work_email, work_number, zipcode, page, custom_field_cf_fully_onboarded, custom_field_cf_site_, updated_at_dt, custom_field_cf_docs_to_be_uploaded_at_inperson_interview, custom_field_cf_what_email_is_associated_with_your_uber_black_account_please_note_you_can_only_be_part_of_one_uber_black_fleet_a, custom_field_cf_driving_test_agenda_month, custom_field_cf_driving_test_agenda_day, custom_field_cf_driving_test_agenda_time, custom_field_cf_driving_test_date, custom_field_cf_non_driver_candidate, custom_field_cf_mvr, custom_field_cf_p1_how_would_you_deal_with_passengers_who_are_upset_or_dont_agree_with_you_while_staying_calm_and_professional, custom_field_cf_drive_test_fail_reason, custom_field_cf_driving_test2_score, custom_field_cf_driving_test_result_2, custom_field_cf_driving_test2_result_date

### `ref.driver_emails`  (rows: 23,846 | cols: 28 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| active | nvarchar(50) | Y |
| active_int | nvarchar(50) | Y |
| attributes | nvarchar(1000) | Y |
| authsource | nvarchar(50) | Y |
| created | nvarchar(50) | Y |
| custom_attributes | nvarchar(50) | Y |
| domain | nvarchar(50) | Y |
| domain_name | nvarchar(50) | Y |
| is_relayed | nvarchar(50) | Y |
| last_imap_login | nvarchar(50) | Y |
| last_pop3_login | nvarchar(50) | Y |
| last_smtp_login | nvarchar(50) | Y |
| last_sso_login | nvarchar(50) | Y |
| local_part | nvarchar(100) | Y |
| max_new_quota | nvarchar(50) | Y |
| messages | nvarchar(50) | Y |
| modified | nvarchar(50) | Y |
| name | nvarchar(100) | Y |
| percent_class | nvarchar(50) | Y |
| percent_in_use | nvarchar(50) | Y |
| pushover_active | nvarchar(50) | Y |
| quota | nvarchar(50) | Y |
| quota_used | nvarchar(50) | Y |
| rl | nvarchar(50) | Y |
| rl_scope | nvarchar(50) | Y |
| spam_aliases | nvarchar(50) | Y |
| username | nvarchar(100) | Y |

### `ref.mail_domains`  (rows: 10 | cols: 33 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| active | nvarchar(50) | Y |
| active_int | nvarchar(50) | Y |
| aliases_in_domain | nvarchar(50) | Y |
| aliases_left | nvarchar(50) | Y |
| backupmx | nvarchar(50) | Y |
| backupmx_int | nvarchar(50) | Y |
| bytes_total | nvarchar(50) | Y |
| created | nvarchar(50) | Y |
| def_new_mailbox_quota | nvarchar(50) | Y |
| def_quota_for_mbox | nvarchar(50) | Y |
| description | nvarchar(50) | Y |
| domain_admins | nvarchar(1000) | Y |
| domain_h_name | nvarchar(50) | Y |
| domain_name | nvarchar(50) | Y |
| gal | nvarchar(50) | Y |
| gal_int | nvarchar(50) | Y |
| max_new_mailbox_quota | nvarchar(50) | Y |
| max_num_aliases_for_domain | nvarchar(50) | Y |
| max_num_mboxes_for_domain | nvarchar(50) | Y |
| max_quota_for_domain | nvarchar(50) | Y |
| max_quota_for_mbox | nvarchar(50) | Y |
| mboxes_in_domain | nvarchar(50) | Y |
| mboxes_left | nvarchar(50) | Y |
| modified | nvarchar(50) | Y |
| msgs_total | nvarchar(50) | Y |
| quota_used_in_domain | nvarchar(50) | Y |
| relay_all_recipients | nvarchar(50) | Y |
| relay_all_recipients_int | nvarchar(50) | Y |
| relay_unknown_only | nvarchar(50) | Y |

_+ 3 more columns (truncated for brevity):_ relay_unknown_only_int, relayhost, rl

### `ref.weather`  (rows: 99,214 | cols: 78 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| latitude | float | Y |
| longitude | float | Y |
| timezone | nvarchar(50) | Y |
| elevation | float | Y |
| granularity | nvarchar(50) | Y |
| time | nvarchar(50) | Y |
| temperature_2m | float | Y |
| relative_humidity_2m | int | Y |
| apparent_temperature | float | Y |
| is_day | int | Y |
| wind_speed_10m | float | Y |
| wind_direction_10m | int | Y |
| wind_gusts_10m | float | Y |
| precipitation | float | Y |
| showers | float | Y |
| rain | float | Y |
| snowfall | float | Y |
| weather_code | int | Y |
| cloud_cover | int | Y |
| dew_point_2m | float | Y |
| visibility | float | Y |
| freezing_level_height | float | Y |
| sunshine_duration | float | Y |
| precipitation_probability | int | Y |
| snow_depth | float | Y |
| temperature_2m_max | float | Y |
| temperature_2m_min | float | Y |
| apparent_temperature_max | float | Y |
| apparent_temperature_min | float | Y |

_+ 48 more columns (truncated for brevity):_ wind_speed_10m_max, wind_gusts_10m_max, wind_direction_10m_dominant, sunrise, sunset, daylight_duration, rain_sum, showers_sum, snowfall_sum, precipitation_sum, precipitation_hours, precipitation_probability_max, uv_index_max, uv_index_clear_sky_max, snowfall_height, evapotranspiration, cloud_cover_low, cloud_cover_mid, cloud_cover_high, uv_index, visibility_min, visibility_max, visibility_mean, uv_index_clear_sky, wet_bulb_temperature_2m, dew_point_2m_min, dew_point_2m_max, cloud_cover_max, cloud_cover_min, relative_humidity_2m_max, relative_humidity_2m_min, wind_speed_10m_min, wind_gusts_10m_min, wet_bulb_temperature_2m_max, wet_bulb_temperature_2m_min, temperature_2m_mean, apparent_temperature_mean, dew_point_2m_mean, cloud_cover_mean, relative_humidity_2m_mean, wind_speed_10m_mean, wind_gusts_10m_mean, winddirection_10m_dominant, wet_bulb_temperature_2m_mean, lightning_potential, updraft_max, pressure_msl, surface_pressure

### `ref.weather_codes`  (rows: 69 | cols: 2 | PK: code)

| Column | Type | Null? |
|---|---|---|
| **code** | int | N |
| meaning | nvarchar(255) | N |

### `ref.FuelAndEnergy`  (rows: 94,166 | cols: 15)

| Column | Type | Null? |
|---|---|---|
| vehicle.energyType | varchar(50) | Y |
| vehicle.id | varchar(50) | N |
| vehicle.name | varchar(100) | Y |
| vehicle.externalIds.samsara.serial | varchar(50) | Y |
| vehicle.externalIds.samsara.vin | varchar(50) | Y |
| efficiencyMpge | float | Y |
| energyUsedKwh | float | Y |
| fuelConsumedMl | bigint | Y |
| distanceTraveledMeters | bigint | Y |
| estCarbonEmissionsKg | float | Y |
| estFuelEnergyCost.amount | float | Y |
| estFuelEnergyCost.currencyCode | varchar(50) | Y |
| engineRunTimeDurationMs | bigint | Y |
| engineIdleTimeDurationMs | bigint | Y |
| date | date | Y |

### `ref.FuelAndEnergyWAV`  (rows: 95,970 | cols: 15)

| Column | Type | Null? |
|---|---|---|
| vehicle.energyType | varchar(50) | Y |
| vehicle.id | varchar(50) | N |
| vehicle.name | varchar(100) | Y |
| vehicle.externalIds.samsara.serial | varchar(50) | Y |
| vehicle.externalIds.samsara.vin | varchar(50) | Y |
| efficiencyMpge | float | Y |
| energyUsedKwh | float | Y |
| fuelConsumedMl | bigint | Y |
| distanceTraveledMeters | bigint | Y |
| estCarbonEmissionsKg | float | Y |
| estFuelEnergyCost.amount | float | Y |
| estFuelEnergyCost.currencyCode | varchar(50) | Y |
| engineRunTimeDurationMs | bigint | Y |
| engineIdleTimeDurationMs | bigint | Y |
| date | date | Y |

### `std.charging_sessions`  (rows: 141,271 | cols: 34)

| Column | Type | Null? |
|---|---|---|
| ts | datetimeoffset | Y |
| targetRef | nvarchar(50) | Y |
| chargeBoxSerialNumber | nvarchar(50) | Y |
| chargePointModel | nvarchar(50) | Y |
| chargePointSerialNumber | nvarchar(50) | Y |
| chargePointVendor | nvarchar(50) | Y |
| clientToken | nvarchar(50) | Y |
| dis | nvarchar(50) | Y |
| energyDelivered | nvarchar(50) | Y |
| errorCode | nvarchar(50) | Y |
| event | nvarchar(max) | Y |
| fault | nvarchar(max) | Y |
| faultReason | nvarchar(50) | Y |
| firmwareVersion | nvarchar(50) | Y |
| lastMeterValuesRecv | datetimeoffset | Y |
| meterSerialNumber | nvarchar(50) | Y |
| meterStart | nvarchar(50) | Y |
| meterStop | nvarchar(50) | Y |
| meterType | nvarchar(50) | Y |
| powerMax | nvarchar(50) | Y |
| spec | nvarchar(100) | Y |
| started | datetimeoffset | Y |
| startedStateOfCharge | nvarchar(50) | Y |
| status | nvarchar(50) | Y |
| stopped | datetimeoffset | Y |
| stoppedClientToken | nvarchar(50) | Y |
| stoppedClientTokenStatus | nvarchar(50) | Y |
| stoppedReason | nvarchar(50) | Y |
| stoppedStateOfCharge | nvarchar(50) | Y |
| txId | nvarchar(50) | Y |

_+ 4 more columns (truncated for brevity):_ vendorErrorCode, row_hash, tsReported, meterTotal

### `std.epn_review`  (rows: 0 | cols: 35)

| Column | Type | Null? |
|---|---|---|
| Driver Name | nvarchar(255) | Y |
| Upload Date | date | Y |
| Uploader | nvarchar(255) | Y |
| Reviewer | nvarchar(255) | Y |
| EPN Record Date | date | Y |
| DL Number | nvarchar(50) | Y |
| DL Expiration Date | date | Y |
| Recommendation | nvarchar(max) | Y |
| Issue Found | nvarchar(max) | Y |
| Management Recommendation | nvarchar(max) | Y |
| Driver Action Needed | nvarchar(255) | Y |
| Violation Date | date | Y |
| Conviction Date | date | Y |
| Section(s) Violated | nvarchar(500) | Y |
| Statute | nvarchar(255) | Y |
| Dept Action | nvarchar(500) | Y |
| Mail Order Date | date | Y |
| Effective Date | date | Y |
| Authority / Section | nvarchar(255) | Y |
| Thru Date / Term | nvarchar(100) | Y |
| Reason for Action | nvarchar(max) | Y |
| FR File Number | nvarchar(100) | Y |
| Records Reviewed | nvarchar(max) | Y |
| Source PDF(s) | nvarchar(max) | Y |
| Management Decision | nvarchar(255) | Y |
| Management Notes | nvarchar(max) | Y |
| Employee ID | nvarchar(50) | Y |
| Driver License (Paylocity) | nvarchar(50) | Y |
| Uber ID | nvarchar(100) | Y |
| Work Location | nvarchar(255) | Y |

_+ 5 more columns (truncated for brevity):_ Employee Status, Hire Date, Birth Date (Paylocity), Last Reviewer, Last Review Date

<!-- AUTO:END tables -->
