# IMS — Internal Management System

**Confidence note: lower than other sections.** IMS is Tower's own internal ops/HR-ticketing platform. Every table here carries a `mongo_id` and `backup_synced_at` column, indicating this SQL data is a **backup mirror of a MongoDB-backed internal app**, not a primary analytics source — treat it as directionally useful but verify before relying on it for anything load-bearing. Only `std.ims_employees` was directly exercised by scripts read this session (used to cross-check active non-driver WAV/EV employees against the internal directory, with fuzzy name matching for near-misses).

## Tables (grouped by apparent function — inferred from naming, not verified usage)

**People/directory:**
- `std.ims_employees` — internal-app user directory: `employee_name`, `email_address`, `job_title`, `department`, `account_status`, `paylocity_employee_id` (join key back to Paylocity), `badge_number`, `assigned_asset`.
- `std.ims_drivers` — a driver-specific view: `employee_id`, `custom_uber_id`, `employee_status`, `work_location`, `cost_center`, `hire_date`/`termination_date` — largely mirrors Paylocity driver fields, likely synced from there (`sync_source` column suggests as much).

**Request/workflow tables** (each paired with a `*_comments` table for threaded discussion): `ims_employee_requests` (hiring requisitions — position, pay type, HR approval workflow), `ims_facilities_requests`, `ims_marketing_requests`, `ims_work_requests`.

**Operational/misc:** `ims_announcements` (in-app banner messages), `ims_group_meetings`, `ims_hr_clerk_mails`, `ims_lost_found_items`, `ims_network_devices`, `ims_off_cycles`, `ims_one_on_ones`, `ims_qr_codes`, `ims_security_alerts`, `ims_sms_channels`/`ims_sms_conversations`/`ims_sms_messages` (an in-app SMS/messaging feature), `ims_tesla_vehicles` (a company Tesla fleet — likely staff/exec vehicles, separate from the commercial Fleetio/Samsara fleet), `ims_wifi_passwords`.

**Reference/admin** (`ref` schema): `ims_companies`, `ims_permissions`, `ims_roles`, `ims_users`, `ims_admin_settings`, `ims_system_constants`, `ims_system_options`, `ims_system_settings` — role-based access control and app configuration for the IMS platform itself, not business data.

Full column lists below are the raw schema — no per-column business notes are given here since this domain wasn't directly used this session; treat column names as a starting hypothesis and verify against a live sample before building anything on top of them.

<!-- AUTO:BEGIN tables (regenerated daily by scripts/regenerate.py — do not hand-edit below this line) -->
### `std.ims_announcements`  (rows: 6 | cols: 15 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| title | nvarchar(500) | Y |
| message | nvarchar(max) | Y |
| style | nvarchar(255) | Y |
| is_active | bit | Y |
| starts_at | datetime2 | Y |
| expires_at | datetime2 | Y |
| action_url | nvarchar(max) | Y |
| action_text | nvarchar(255) | Y |
| created_by_name | nvarchar(500) | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_drivers`  (rows: 10,952 | cols: 19 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| first_name | nvarchar(255) | Y |
| last_name | nvarchar(255) | Y |
| full_name | nvarchar(500) | Y |
| employee_id | nvarchar(255) | Y |
| custom_uber_id | nvarchar(255) | Y |
| employee_status | nvarchar(255) | Y |
| company_name | nvarchar(255) | Y |
| office_location | nvarchar(255) | Y |
| work_location | nvarchar(255) | Y |
| job_title | nvarchar(255) | Y |
| cost_center | nvarchar(255) | Y |
| hire_date | datetime2 | Y |
| termination_date | datetime2 | Y |
| sync_source | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_employee_requests`  (rows: 35 | cols: 33 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| requisition_number | nvarchar(255) | Y |
| position_needed | nvarchar(500) | Y |
| date_of_request | datetime2 | Y |
| employment_type | nvarchar(255) | Y |
| company | nvarchar(255) | Y |
| location | nvarchar(255) | Y |
| reason_for_request | nvarchar(max) | Y |
| quantity | int | Y |
| pay_type | nvarchar(255) | Y |
| shift_type | nvarchar(255) | Y |
| weekend_required | bit | Y |
| anticipated_start_date | datetime2 | Y |
| pay_rate | nvarchar(255) | Y |
| department | nvarchar(255) | Y |
| department_code | nvarchar(255) | Y |
| position_code | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| hiring_manager_name | nvarchar(500) | Y |
| hiring_manager_email | nvarchar(500) | Y |
| hr_approved | bit | Y |
| hr_approved_by | nvarchar(500) | Y |
| hr_approved_date | datetime2 | Y |
| hr_denied | bit | Y |
| hr_denied_by | nvarchar(500) | Y |
| hr_denied_date | datetime2 | Y |
| created_by | nvarchar(255) | Y |
| created_by_name | nvarchar(500) | Y |
| created_at | datetime2 | Y |

_+ 3 more columns (truncated for brevity):_ updated_at, schedule_json, backup_synced_at

### `std.ims_employees`  (rows: 752 | cols: 18 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| user_id | nvarchar(255) | Y |
| employee_name | nvarchar(500) | Y |
| email_address | nvarchar(500) | Y |
| job_title | nvarchar(255) | Y |
| department | nvarchar(255) | Y |
| account_status | nvarchar(255) | Y |
| company_name | nvarchar(255) | Y |
| office_location | nvarchar(255) | Y |
| badge_number | nvarchar(255) | Y |
| paylocity_employee_id | nvarchar(255) | Y |
| assigned_asset | nvarchar(255) | Y |
| last_synced | datetime2 | Y |
| sync_status | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_facilities_request_comments`  (rows: 15 | cols: 11 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| facilities_request_id | nvarchar(255) | Y |
| comment | nvarchar(max) | Y |
| commented_by | nvarchar(255) | Y |
| commented_by_name | nvarchar(500) | Y |
| is_internal | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| attachments_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_facilities_requests`  (rows: 26 | cols: 26 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| request_number | nvarchar(255) | Y |
| title | nvarchar(500) | Y |
| description | nvarchar(max) | Y |
| location | nvarchar(255) | Y |
| priority | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| desired_completion_date | datetime2 | Y |
| company_name | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| department | nvarchar(255) | Y |
| requested_by_name | nvarchar(500) | Y |
| requested_by_email | nvarchar(500) | Y |
| assigned_to_name | nvarchar(500) | Y |
| resolution | nvarchar(max) | Y |
| completed_at | datetime2 | Y |
| completed_by_name | nvarchar(500) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| requestType_json | nvarchar(max) | Y |
| referenceLinks_json | nvarchar(max) | Y |
| attachments_json | nvarchar(max) | Y |
| completedWork_json | nvarchar(max) | Y |
| tags_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_group_meetings`  (rows: 6 | cols: 29 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| title | nvarchar(500) | Y |
| meeting_type | nvarchar(255) | Y |
| department | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| series_id | nvarchar(255) | Y |
| facilitator_id | nvarchar(255) | Y |
| facilitator_name | nvarchar(500) | Y |
| meeting_date | nvarchar(255) | Y |
| start_time | nvarchar(255) | Y |
| end_time | nvarchar(255) | Y |
| duration | int | Y |
| cadence | nvarchar(255) | Y |
| location | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| overall_rating | int | Y |
| meeting_effectiveness | nvarchar(255) | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| attendees_json | nvarchar(max) | Y |
| agendaItems_json | nvarchar(max) | Y |
| actionItems_json | nvarchar(max) | Y |
| kpiEntries_json | nvarchar(max) | Y |
| feedbackEntries_json | nvarchar(max) | Y |
| goals_json | nvarchar(max) | Y |
| notes_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_hr_clerk_mails`  (rows: 1,818 | cols: 26 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| direction | nvarchar(255) | Y |
| category | nvarchar(255) | Y |
| driver_name | nvarchar(500) | Y |
| driver_employee_id | nvarchar(255) | Y |
| driver_id | nvarchar(255) | Y |
| sender | nvarchar(500) | Y |
| recipient | nvarchar(500) | Y |
| reference_number | nvarchar(255) | Y |
| tracking_number | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| date_received | datetime2 | Y |
| date_sent | datetime2 | Y |
| due_date | datetime2 | Y |
| status | nvarchar(255) | Y |
| priority | nvarchar(255) | Y |
| response_method | nvarchar(255) | Y |
| company_name | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| activityLog_json | nvarchar(max) | Y |
| attachments_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_lost_found_items`  (rows: 95 | cols: 23 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| item_number | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| category | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| location_found | nvarchar(500) | Y |
| branch | nvarchar(255) | Y |
| company | nvarchar(255) | Y |
| date_found | datetime2 | Y |
| found_by | nvarchar(500) | Y |
| storage_location | nvarchar(500) | Y |
| retention_deadline | datetime2 | Y |
| claimant_name | nvarchar(500) | Y |
| claimed_date | datetime2 | Y |
| released_date | datetime2 | Y |
| release_method | nvarchar(255) | Y |
| created_by | nvarchar(255) | Y |
| created_by_name | nvarchar(500) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| photos_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_marketing_request_comments`  (rows: 173 | cols: 11 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| marketing_request_id | nvarchar(255) | Y |
| comment | nvarchar(max) | Y |
| commented_by | nvarchar(255) | Y |
| commented_by_name | nvarchar(500) | Y |
| is_internal | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| attachments_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_marketing_requests`  (rows: 39 | cols: 28 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| request_number | nvarchar(255) | Y |
| title | nvarchar(500) | Y |
| description | nvarchar(max) | Y |
| dimensions | nvarchar(255) | Y |
| quantity | int | Y |
| target_audience | nvarchar(max) | Y |
| priority | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| desired_completion_date | datetime2 | Y |
| company_name | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| department | nvarchar(255) | Y |
| requested_by_name | nvarchar(500) | Y |
| requested_by_email | nvarchar(500) | Y |
| assigned_to_name | nvarchar(500) | Y |
| completed_at | datetime2 | Y |
| completed_by_name | nvarchar(500) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| requestType_json | nvarchar(max) | Y |
| platform_json | nvarchar(max) | Y |
| referenceLinks_json | nvarchar(max) | Y |
| attachments_json | nvarchar(max) | Y |
| deliverables_json | nvarchar(max) | Y |
| tags_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_network_devices`  (rows: 50 | cols: 22 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| name | nvarchar(500) | Y |
| type | nvarchar(255) | Y |
| mac_address | nvarchar(255) | Y |
| ip_address | nvarchar(255) | Y |
| model | nvarchar(255) | Y |
| shortname | nvarchar(255) | Y |
| firmware | nvarchar(255) | Y |
| firmware_status | nvarchar(255) | Y |
| product_line | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| site_name | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| startup_time | datetime2 | Y |
| is_console | bit | Y |
| unifi_id | nvarchar(255) | Y |
| unifi_last_sync | datetime2 | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| unifiData_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_off_cycles`  (rows: 140 | cols: 14 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| employeeName_json | nvarchar(max) | Y |
| employeeId_json | nvarchar(max) | Y |
| type_json | nvarchar(max) | Y |
| amount_json | nvarchar(max) | Y |
| reason_json | nvarchar(max) | Y |
| status_json | nvarchar(max) | Y |
| company_json | nvarchar(max) | Y |
| branch_json | nvarchar(max) | Y |
| department_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_one_on_ones`  (rows: 109 | cols: 29 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| manager_id | nvarchar(255) | Y |
| manager_name | nvarchar(500) | Y |
| manager_email | nvarchar(500) | Y |
| employee_id | nvarchar(255) | Y |
| employee_name | nvarchar(500) | Y |
| employee_email | nvarchar(500) | Y |
| department | nvarchar(255) | Y |
| meeting_date | nvarchar(255) | Y |
| start_time | nvarchar(255) | Y |
| end_time | nvarchar(255) | Y |
| duration | int | Y |
| cadence | nvarchar(255) | Y |
| location | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| overall_rating | int | Y |
| meeting_effectiveness | nvarchar(255) | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| agendaItems_json | nvarchar(max) | Y |
| actionItems_json | nvarchar(max) | Y |
| kpiEntries_json | nvarchar(max) | Y |
| feedbackEntries_json | nvarchar(max) | Y |
| goals_json | nvarchar(max) | Y |
| notes_json | nvarchar(max) | Y |
| wellBeing_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_qr_codes`  (rows: 6 | cols: 18 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| name | nvarchar(500) | Y |
| description | nvarchar(max) | Y |
| category | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| target_url | nvarchar(max) | Y |
| short_code | nvarchar(255) | Y |
| total_scans | int | Y |
| unique_scans | int | Y |
| last_scanned_at | datetime2 | Y |
| department | nvarchar(255) | Y |
| expires_at | datetime2 | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| scans_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_security_alerts`  (rows: 445 | cols: 21 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| alert_type | nvarchar(255) | Y |
| severity | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| affected_user | nvarchar(500) | Y |
| affected_user_id | nvarchar(255) | Y |
| source_ip | nvarchar(255) | Y |
| endpoint | nvarchar(500) | Y |
| count | int | Y |
| first_occurrence | datetime2 | Y |
| last_occurrence | datetime2 | Y |
| resolved | bit | Y |
| resolved_at | datetime2 | Y |
| resolved_by | nvarchar(255) | Y |
| resolved_by_name | nvarchar(500) | Y |
| notification_sent | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| details_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_sms_channels`  (rows: 10 | cols: 13 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| name | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| dedicated_number | nvarchar(255) | Y |
| is_active | bit | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| members_json | nvarchar(max) | Y |
| admins_json | nvarchar(max) | Y |
| settings_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_sms_conversations`  (rows: 128 | cols: 16 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| channel_id | nvarchar(255) | Y |
| external_number | nvarchar(255) | Y |
| contact_name | nvarchar(500) | Y |
| status | nvarchar(255) | Y |
| assigned_to | nvarchar(255) | Y |
| last_message_at | datetime2 | Y |
| last_message_preview | nvarchar(500) | Y |
| last_message_direction | nvarchar(255) | Y |
| unread_count | int | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| tags_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_sms_messages`  (rows: 569 | cols: 24 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| message_id | nvarchar(255) | Y |
| conversation_id | nvarchar(255) | Y |
| channel_id | nvarchar(255) | Y |
| direction | nvarchar(255) | Y |
| from_number | nvarchar(255) | Y |
| to_number | nvarchar(255) | Y |
| body | nvarchar(max) | Y |
| media_url | nvarchar(max) | Y |
| media_type | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| clicksend_message_id | nvarchar(255) | Y |
| clicksend_status | nvarchar(255) | Y |
| delivered_at | datetime2 | Y |
| failure_reason | nvarchar(max) | Y |
| sent_by | nvarchar(255) | Y |
| sent_by_name | nvarchar(500) | Y |
| is_broadcast | bit | Y |
| broadcast_group_id | nvarchar(255) | Y |
| cost | decimal | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_tesla_vehicles`  (rows: 430 | cols: 20 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| vehicle_name | nvarchar(500) | Y |
| vin | nvarchar(255) | Y |
| tesla_vehicle_id | nvarchar(255) | Y |
| model | nvarchar(255) | Y |
| year | int | Y |
| color | nvarchar(255) | Y |
| license_plate | nvarchar(255) | Y |
| company | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| state | nvarchar(255) | Y |
| is_reachable | bit | Y |
| last_refreshed_at | datetime2 | Y |
| status | nvarchar(255) | Y |
| created_by | nvarchar(255) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| cachedState_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_wifi_passwords`  (rows: 18 | cols: 16 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| network_name | nvarchar(255) | Y |
| security_type | nvarchar(255) | Y |
| frequency | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| location | nvarchar(255) | Y |
| is_guest | bit | Y |
| is_hidden | bit | Y |
| vlan_id | nvarchar(255) | Y |
| last_rotated | datetime2 | Y |
| status | nvarchar(255) | Y |
| created_by_name | nvarchar(500) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_work_request_comments`  (rows: 0 | cols: 11 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| work_request_id | nvarchar(255) | Y |
| comment | nvarchar(max) | Y |
| commented_by | nvarchar(255) | Y |
| commented_by_name | nvarchar(500) | Y |
| is_internal | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| attachments_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `std.ims_work_requests`  (rows: 7 | cols: 30 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| ticket_number | nvarchar(255) | Y |
| project_title | nvarchar(500) | Y |
| description | nvarchar(max) | Y |
| use_case | nvarchar(max) | Y |
| desired_start_date | datetime2 | Y |
| desired_completion_date | datetime2 | Y |
| requested_by | nvarchar(255) | Y |
| requested_by_name | nvarchar(500) | Y |
| requested_by_email | nvarchar(500) | Y |
| on_behalf_of_name | nvarchar(500) | Y |
| company_name | nvarchar(255) | Y |
| branch | nvarchar(255) | Y |
| department | nvarchar(255) | Y |
| status | nvarchar(255) | Y |
| priority | nvarchar(255) | Y |
| assigned_to | nvarchar(255) | Y |
| assigned_to_name | nvarchar(500) | Y |
| resolution | nvarchar(max) | Y |
| completed_at | datetime2 | Y |
| completed_by_name | nvarchar(500) | Y |
| escalated | bit | Y |
| escalated_at | datetime2 | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| supportTypes_json | nvarchar(max) | Y |
| tags_json | nvarchar(max) | Y |
| attachments_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_admin_settings`  (rows: 2 | cols: 6 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| setting_key | nvarchar(255) | Y |
| updated_at | datetime2 | Y |
| value_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_companies`  (rows: 11 | cols: 12 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| name | nvarchar(255) | Y |
| display_name | nvarchar(255) | Y |
| tax_id | nvarchar(255) | Y |
| is_active | bit | Y |
| is_default | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| address_json | nvarchar(max) | Y |
| contact_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_permissions`  (rows: 700 | cols: 12 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| name | nvarchar(255) | Y |
| display_name | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| resource | nvarchar(255) | Y |
| action | nvarchar(255) | Y |
| category | nvarchar(255) | Y |
| is_system | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_roles`  (rows: 58 | cols: 11 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| name | nvarchar(255) | Y |
| display_name | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| is_system | bit | Y |
| is_active | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| permissions_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_system_constants`  (rows: 0 | cols: 8 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| key_json | nvarchar(max) | Y |
| value_json | nvarchar(max) | Y |
| category_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_system_options`  (rows: 264 | cols: 12 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(255) | N |
| option_key | nvarchar(255) | Y |
| label | nvarchar(255) | Y |
| module | nvarchar(255) | Y |
| description | nvarchar(max) | Y |
| is_protected | bit | Y |
| last_updated_at | datetime2 | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| options_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_system_settings`  (rows: 1 | cols: 6 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| settings_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

### `ref.ims_users`  (rows: 215 | cols: 14 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| mongo_id | nvarchar(50) | Y |
| username | nvarchar(255) | Y |
| email | nvarchar(500) | Y |
| full_name | nvarchar(500) | Y |
| status | nvarchar(255) | Y |
| last_login | datetime2 | Y |
| is_first_login | bit | Y |
| must_change_password | bit | Y |
| created_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| roles_json | nvarchar(max) | Y |
| metadata_json | nvarchar(max) | Y |
| backup_synced_at | datetime2 | N |

<!-- AUTO:END tables -->
