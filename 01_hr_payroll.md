# HR & Payroll (Paylocity)

Covers Paylocity data (Tower's HR/payroll system of record) for all three fleets, plus small adjacent lookup sets: pay/deduction code glossaries, Tower's own insurance policy rosters, and pre-hire training-verification tracking.

See [`00_START_HERE.md`](00_START_HERE.md) for the AV/EV/WAV convention, universal join keys, and status/position code glossary — those apply throughout this file and aren't repeated per table.

**For turnover/attrition/tenure questions (EV only)**, use **`rpt.vw_all_drivers_enriched`** instead of querying `*_employees_detail` directly — it adds the "ghosting"-aware `[Last Active Minus Terminated At]` formula that the confirmed-accurate `real turnover rate` metric is built on, plus `[Last Active Date]`, `[Veteran Status]`, `[Hire Type]`, and the Mission/Douglas `[Locations]` mapping. See `07_powerbi_glossary.md`'s "SQL views now exist" section and its Turnover cluster writeup for what these mean and why the ghosting distinction matters.

## Table families

- **`*_employees_detail`** — one row per employee, the full Paylocity API "detail" record flattened (nested JSON like `departmentPosition.jobTitle` becomes `departmentPosition_jobTitle`). This is the record HR alert scripts iterate over. Key columns to reach for: `employeeId`, `firstName`/`lastName`, `status_employeeStatus`, `status_hireDate`/`status_terminationDate`/`status_reHireDate`, `departmentPosition_positionCode`/`costCenter2`/`jobTitle`, `workAddress_location`, `custom_Uber_ID`(`_guid`), `custom_Driver_License`. **AV's version is entirely untyped** (`nvarchar(max)` throughout) — the other two have mostly `varchar(50)`.
- **`*_employees_basic`** (in `ref`) — a thin lookup (`id`, `displayName`, `status`, `statusType`) from a different, lighter Paylocity API endpoint than `*_employees_detail`. Use `_detail` for anything beyond a quick name/status check.
- **`*_payments`** — one row per pay-stub line item (`amount`, `checkDate`, `detCode`/`detType`, `hours`, `rate`, `transactionType`). `detCode` joins to `ref.paylocity_earning_codes`/`ref.paylocity_deduction_codes` for a human-readable label. AV has a payments table shell (`std.paylocity_av_payments`) but it's currently empty (0 rows).
- **`*_shift_unified`** — scheduled shifts: `shiftId`, `startDateTime`, `duration`, and a `segment_*` breakdown of regular/OT1/OT2/non-work/unpaid time. EV/WAV are properly typed; **AV's shift table is entirely untyped** like its employee table.
- **`*_punches`** — actual clock-in/out events: `clock_in`/`clock_out`, `lunch_start_time`/`lunch_end_time`, `total_hours`, `total_earnings`, plus a `driver_uuid` column as an alternate join to Uber data. No AV punches table exists yet (fleet is small/new enough that it may not be tracked this way, or just not yet built).

## Tables

<!-- AUTO:BEGIN tables (regenerated daily by scripts/regenerate.py — do not hand-edit below this line) -->
### `std.paylocity_av_employees_detail`  (rows: 48 | cols: 104)

| Column | Type | Null? |
|---|---|---|
| employeeId | nvarchar(20) | N |
| _payload_hash | nvarchar(40) | Y |
| birthDate | nvarchar(max) | Y |
| coEmpCode | nvarchar(max) | Y |
| firstName | nvarchar(max) | Y |
| lastName | nvarchar(max) | Y |
| gender | nvarchar(max) | Y |
| ssn | nvarchar(max) | Y |
| currency | nvarchar(max) | Y |
| taxSetup_suiState | nvarchar(max) | Y |
| taxSetup_taxForm | nvarchar(max) | Y |
| benefitSetup_benefitClass | nvarchar(max) | Y |
| benefitSetup_benefitClassEffectiveDate | nvarchar(max) | Y |
| benefitSetup_benefitSalary | nvarchar(max) | Y |
| benefitSetup_doNotApplyAdministrativePeriod | nvarchar(max) | Y |
| benefitSetup_isMeasureAcaEligibility | nvarchar(max) | Y |
| departmentPosition_costCenter1 | nvarchar(max) | Y |
| departmentPosition_costCenter2 | nvarchar(max) | Y |
| departmentPosition_effectiveDate | nvarchar(max) | Y |
| departmentPosition_employeeType | nvarchar(max) | Y |
| departmentPosition_equalEmploymentOpportunityClass | nvarchar(max) | Y |
| departmentPosition_isMinimumWageExempt | nvarchar(max) | Y |
| departmentPosition_isOvertimeExempt | nvarchar(max) | Y |
| departmentPosition_isSupervisorReviewer | nvarchar(max) | Y |
| departmentPosition_isUnionDuesCollected | nvarchar(max) | Y |
| departmentPosition_isUnionInitiationCollected | nvarchar(max) | Y |
| departmentPosition_jobTitle | nvarchar(max) | Y |
| departmentPosition_positionCode | nvarchar(max) | Y |
| departmentPosition_workersCompensation | nvarchar(max) | Y |
| federalTax_amount | nvarchar(max) | Y |

_+ 74 more columns (truncated for brevity):_ federalTax_filingStatus, federalTax_percentage, federalTax_taxCalculationCode, federalTax_w4FormYear, primaryPayRate_annualSalary, federalTax_dependentsAmount, primaryPayRate_baseRate, primaryPayRate_changeReason, primaryPayRate_defaultHours, primaryPayRate_effectiveDate, primaryPayRate_beginCheckDate, primaryPayRate_isAutoPay, primaryPayRate_payFrequency, primaryPayRate_payType, primaryPayRate_ratePer, primaryPayRate_salary, primaryStateTax_amount, primaryStateTax_exemptions, primaryStateTax_exemptions2, primaryStateTax_filingStatus, primaryStateTax_percentage, primaryStateTax_specialCheckCalc, primaryStateTax_taxCalculationCode, primaryStateTax_taxCode, primaryStateTax_w4FormYear, status_changeReason, status_effectiveDate, status_employeeStatus, status_beginCheckDate, status_hireDate, status_isEligibleForRehire, status_statusType, homeAddress_address1, homeAddress_address2, homeAddress_city, homeAddress_country, homeAddress_emailAddress, homeAddress_mobilePhone, homeAddress_state, homeAddress_postalCode, webTime_isTimeLaborEnabled, webTime_badgeNumber, companyName, companyFEIN, isRothCatchupRequiredEmployee, emergencyContacts, federalTax_deductionsAmount, departmentPosition_reviewerCompanyNumber, departmentPosition_reviewerEmployeeId, departmentPosition_supervisorCompanyNumber, departmentPosition_supervisorEmployeeId, status_terminationDate, ethnicity, maritalStatus, departmentPosition_changeReason, middleName, workAddress_location, workAddress_address1, priorLastName, workAddress_city, workAddress_country, workAddress_state, workAddress_postalCode, webTime_chargeRate, workEligibility_isI9Verified, workEligibility_isSsnVerified, preferredName, federalTax_higherRate, homeAddress_phone, workEligibility_foreignPassportNumber, workEligibility_i94AdmissionNumber, workEligibility_workAuthorization, workEligibility_alienOrAdmissionDocumentNumber, status_reHireDate

### `std.paylocity_ev_employees_detail`  (rows: 8,187 | cols: 136)

| Column | Type | Null? |
|---|---|---|
| birthDate | varchar(50) | Y |
| custom_Uber_ID | varchar(100) | Y |
| employeeId | nvarchar(50) | Y |
| coEmpCode | varchar(50) | Y |
| firstName | varchar(50) | Y |
| lastName | varchar(50) | Y |
| gender | varchar(50) | Y |
| ssn | varchar(50) | Y |
| currency | varchar(50) | Y |
| taxSetup_suiState | varchar(50) | Y |
| taxSetup_taxForm | varchar(50) | Y |
| departmentPosition_costCenter1 | varchar(50) | Y |
| departmentPosition_costCenter2 | varchar(50) | Y |
| departmentPosition_effectiveDate | varchar(50) | Y |
| departmentPosition_employeeType | varchar(50) | Y |
| departmentPosition_isMinimumWageExempt | varchar(50) | Y |
| departmentPosition_isOvertimeExempt | varchar(50) | Y |
| departmentPosition_isSupervisorReviewer | varchar(50) | Y |
| departmentPosition_isUnionDuesCollected | varchar(50) | Y |
| departmentPosition_isUnionInitiationCollected | varchar(50) | Y |
| departmentPosition_supervisorCompanyNumber | varchar(50) | Y |
| departmentPosition_supervisorEmployeeId | varchar(50) | Y |
| departmentPosition_workersCompensation | varchar(50) | Y |
| federalTax_amount | varchar(50) | Y |
| federalTax_filingStatus | varchar(50) | Y |
| federalTax_percentage | varchar(50) | Y |
| federalTax_taxCalculationCode | varchar(50) | Y |
| federalTax_w4FormYear | varchar(50) | Y |
| federalTax_dependentsAmount | varchar(50) | Y |
| primaryPayRate_annualSalary | varchar(50) | Y |

_+ 106 more columns (truncated for brevity):_ primaryPayRate_baseRate, primaryPayRate_changeReason, primaryPayRate_defaultHours, primaryPayRate_effectiveDate, primaryPayRate_beginCheckDate, primaryPayRate_isAutoPay, primaryPayRate_payFrequency, primaryPayRate_payType, primaryPayRate_ratePer, primaryPayRate_salary, primaryStateTax_amount, primaryStateTax_exemptions, primaryStateTax_exemptions2, primaryStateTax_filingStatus, primaryStateTax_percentage, primaryStateTax_specialCheckCalc, primaryStateTax_taxCalculationCode, primaryStateTax_taxCode, primaryStateTax_w4FormYear, status_changeReason, status_effectiveDate, status_employeeStatus, status_beginCheckDate, status_hireDate, status_isEligibleForRehire, status_statusType, status_terminationDate, workAddress_location, workAddress_address1, workAddress_city, workAddress_country, workAddress_state, workAddress_postalCode, homeAddress_address1, homeAddress_city, homeAddress_country, homeAddress_county, homeAddress_emailAddress, homeAddress_mobilePhone, homeAddress_state, homeAddress_postalCode, webTime_isTimeLaborEnabled, webTime_chargeRate, companyName, companyFEIN, benefitSetup_benefitClass, benefitSetup_benefitClassEffectiveDate, benefitSetup_benefitSalary, benefitSetup_doNotApplyAdministrativePeriod, benefitSetup_isMeasureAcaEligibility, departmentPosition_jobTitle, departmentPosition_positionCode, departmentPosition_reviewerCompanyNumber, departmentPosition_reviewerEmployeeId, federalTax_deductionsAmount, workAddress_emailAddress, webTime_badgeNumber, homeAddress_address2, custom_Driver_License, departmentPosition_equalEmploymentOpportunityClass, workAddress_phone, customBooleanFields, federalTax_higherRate, middleName, preferredName, maritalStatus, status_reHireDate, homeAddress_phone, emergencyContacts, departmentPosition_changeReason, ethnicity, workAddress_county, primaryPayRate_payRateNote, federalTax_otherIncomeAmount, priorLastName, statusCode, statusTypeCode, status_adjustedSeniorityDate, veteranDescription, workAddress_mobilePhone, custom_Expiration_Date, customDropDownFields, lat, lng, federalTax_exemptions, customNumberFields, departmentPosition_clockBadgeNumber, custom_Exclude_from_ADP, taxSetup_fitwExemptReason, taxSetup_futaExemptReason, taxSetup_medExemptReason, taxSetup_sitwExemptReason, taxSetup_ssExemptReason, taxSetup_suiExemptReason, custom_Tower_Email_Address, custom_Uber_Teens, isRothCatchupRequiredEmployee, _payload_hash, salutation, workEligibility_isI9Verified, workEligibility_isSsnVerified, workEligibility_foreignPassportNumber, workEligibility_alienOrAdmissionDocumentNumber, workEligibility_i94AdmissionNumber, workEligibility_workAuthorization, workEligibility_workUntil

### `std.paylocity_wav_employees_detail`  (rows: 2,910 | cols: 140)

| Column | Type | Null? |
|---|---|---|
| employeeId | varchar(50) | Y |
| birthDate | varchar(50) | Y |
| coEmpCode | varchar(50) | Y |
| ethnicity | varchar(50) | Y |
| firstName | varchar(50) | Y |
| lastName | varchar(50) | Y |
| custom_Exclude_from_ADP | varchar(50) | Y |
| custom_Driver_License | varchar(50) | Y |
| maritalStatus | varchar(50) | Y |
| middleName | varchar(50) | Y |
| gender | varchar(50) | Y |
| ssn | varchar(50) | Y |
| currency | varchar(50) | Y |
| preferredName | varchar(50) | Y |
| taxSetup_suiState | varchar(50) | Y |
| priorLastName | varchar(50) | Y |
| taxSetup_taxForm | varchar(50) | Y |
| benefitSetup_benefitClass | varchar(50) | Y |
| benefitSetup_benefitClassEffectiveDate | varchar(50) | Y |
| benefitSetup_benefitSalary | varchar(50) | Y |
| benefitSetup_doNotApplyAdministrativePeriod | varchar(50) | Y |
| benefitSetup_isMeasureAcaEligibility | varchar(50) | Y |
| departmentPosition_costCenter1 | varchar(50) | Y |
| departmentPosition_costCenter2 | varchar(50) | Y |
| departmentPosition_effectiveDate | varchar(50) | Y |
| departmentPosition_employeeType | varchar(50) | Y |
| departmentPosition_equalEmploymentOpportunityClass | varchar(50) | Y |
| departmentPosition_isMinimumWageExempt | varchar(50) | Y |
| departmentPosition_isOvertimeExempt | varchar(50) | Y |
| departmentPosition_isSupervisorReviewer | varchar(50) | Y |

_+ 110 more columns (truncated for brevity):_ departmentPosition_isUnionDuesCollected, departmentPosition_isUnionInitiationCollected, departmentPosition_jobTitle, departmentPosition_positionCode, departmentPosition_reviewerCompanyNumber, departmentPosition_reviewerEmployeeId, departmentPosition_supervisorCompanyNumber, departmentPosition_supervisorEmployeeId, departmentPosition_workersCompensation, federalTax_amount, federalTax_filingStatus, federalTax_percentage, federalTax_taxCalculationCode, federalTax_w4FormYear, primaryPayRate_baseRate, primaryPayRate_annualSalary, federalTax_higherRate, federalTax_exemptions, primaryPayRate_changeReason, primaryPayRate_effectiveDate, primaryPayRate_beginCheckDate, federalTax_dependentsAmount, federalTax_otherIncomeAmount, primaryPayRate_isAutoPay, primaryPayRate_payFrequency, primaryPayRate_payType, federalTax_deductionsAmount, primaryPayRate_ratePer, primaryStateTax_amount, primaryPayRate_defaultHours, primaryStateTax_exemptions, primaryPayRate_payRateNote, primaryStateTax_exemptions2, primaryStateTax_filingStatus, primaryStateTax_percentage, primaryStateTax_specialCheckCalc, primaryStateTax_taxCalculationCode, primaryStateTax_taxCode, primaryStateTax_w4FormYear, status_changeReason, status_effectiveDate, status_employeeStatus, status_beginCheckDate, status_hireDate, status_isEligibleForRehire, status_statusType, status_terminationDate, workAddress_location, workAddress_address1, workAddress_address2, workAddress_city, workAddress_country, workAddress_state, workAddress_postalCode, homeAddress_address1, homeAddress_address2, homeAddress_city, homeAddress_country, status_reHireDate, homeAddress_emailAddress, homeAddress_mobilePhone, homeAddress_phone, homeAddress_state, homeAddress_postalCode, webTime_isTimeLaborEnabled, webTime_chargeRate, companyName, companyFEIN, emergencyContacts, primaryPayRate_salary, departmentPosition_changeReason, homeAddress_county, custom_Uber_ID, localTax, workAddress_mobilePhone, workAddress_emailAddress, workAddress_phone, nonPrimaryStateTax_reciprocityCode, nonPrimaryStateTax_amount, nonPrimaryStateTax_exemptions, nonPrimaryStateTax_exemptions2, nonPrimaryStateTax_filingStatus, nonPrimaryStateTax_percentage, nonPrimaryStateTax_specialCheckCalc, nonPrimaryStateTax_taxCalculationCode, nonPrimaryStateTax_taxCode, nonPrimaryStateTax_w4FormYear, veteranDescription, webTime_badgeNumber, workAddress_county, taxSetup_fitwExemptReason, taxSetup_futaExemptReason, taxSetup_medExemptReason, taxSetup_sitwExemptReason, taxSetup_ssExemptReason, taxSetup_suiExemptReason, status_adjustedSeniorityDate, custom_Expiration_Date, custom_Tower_Email_Address, isRothCatchupRequiredEmployee, _payload_hash, customBooleanFields, customDropDownFields, departmentPosition_clockBadgeNumber, workEligibility_isI9Verified, workEligibility_isSsnVerified, workEligibility_foreignPassportNumber, workEligibility_i94AdmissionNumber, workEligibility_workAuthorization, workEligibility_alienOrAdmissionDocumentNumber

### `std.paylocity_av_payments`  (rows: 0 | cols: 3 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| employeeId | nvarchar(max) | Y |
| _sync_year | int | Y |

### `std.paylocity_ev_payments`  (rows: 2,683,762 | cols: 14 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| employeeId | nvarchar(50) | Y |
| amount | nvarchar(50) | Y |
| checkDate | nvarchar(50) | Y |
| det | nvarchar(50) | Y |
| detCode | nvarchar(50) | Y |
| detType | nvarchar(50) | Y |
| hours | nvarchar(50) | Y |
| rate | nvarchar(50) | Y |
| transactionNumber | nvarchar(50) | Y |
| transactionType | nvarchar(50) | Y |
| year | nvarchar(50) | Y |
| eligibleCompensation | nvarchar(50) | Y |
| _sync_year | nvarchar(50) | Y |

### `std.paylocity_wav_payments`  (rows: 995,100 | cols: 14 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| employeeId | nvarchar(50) | Y |
| amount | nvarchar(50) | Y |
| checkDate | nvarchar(50) | Y |
| det | nvarchar(50) | Y |
| detCode | nvarchar(50) | Y |
| detType | nvarchar(50) | Y |
| hours | nvarchar(50) | Y |
| rate | nvarchar(50) | Y |
| transactionNumber | nvarchar(50) | Y |
| transactionType | nvarchar(50) | Y |
| year | nvarchar(50) | Y |
| eligibleCompensation | nvarchar(50) | Y |
| _sync_year | nvarchar(50) | Y |

### `std.paylocity_ev_paystatements_detail`  (rows: 128,731 | cols: 13 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| amount | nvarchar(50) | Y |
| checkDate | nvarchar(50) | Y |
| det | nvarchar(50) | Y |
| detCode | nvarchar(50) | Y |
| detType | nvarchar(50) | Y |
| hours | nvarchar(50) | Y |
| rate | nvarchar(50) | Y |
| transactionNumber | nvarchar(50) | Y |
| transactionType | nvarchar(50) | Y |
| year | nvarchar(50) | Y |
| employeeId | nvarchar(50) | Y |
| eligibleCompensation | nvarchar(50) | Y |

### `std.paylocity_av_shift_unified`  (rows: 1,058 | cols: 22)

| Column | Type | Null? |
|---|---|---|
| shiftId | nvarchar(max) | Y |
| scheduleId | nvarchar(max) | Y |
| isPublished | nvarchar(max) | Y |
| isDeleted | nvarchar(max) | Y |
| companyId | nvarchar(max) | Y |
| employeeId | nvarchar(20) | Y |
| startDateTime | nvarchar(max) | Y |
| duration | nvarchar(max) | Y |
| hasNote | nvarchar(max) | Y |
| isEmployeeNote | nvarchar(max) | Y |
| costCenters | nvarchar(max) | Y |
| segment_payType | nvarchar(max) | Y |
| segment_actualTimeIn | nvarchar(max) | Y |
| segment_actualTimeOut | nvarchar(max) | Y |
| segment_regDuration | nvarchar(max) | Y |
| segment_ot1Duration | nvarchar(max) | Y |
| segment_ot2Duration | nvarchar(max) | Y |
| segment_nonWorkDuration | nvarchar(max) | Y |
| segment_unpaidDuration | nvarchar(max) | Y |
| segment_cost | nvarchar(max) | Y |
| segment_applyToDate | nvarchar(10) | Y |
| legacyAssignmentId | nvarchar(max) | Y |

### `std.paylocity_ev_shift_unified`  (rows: 342,126 | cols: 25 | PK: shiftId, employeeId)

| Column | Type | Null? |
|---|---|---|
| **shiftId** | int | N |
| scheduleId | int | Y |
| isPublished | bit | Y |
| isDeleted | bit | Y |
| companyId | varchar(50) | Y |
| **employeeId** | varchar(50) | N |
| startDateTime | datetimeoffset | Y |
| duration | int | Y |
| hasNote | bit | Y |
| isEmployeeNote | bit | Y |
| costCenters | nvarchar(max) | Y |
| segment_payType | varchar(50) | Y |
| segment_actualTimeIn | datetimeoffset | Y |
| segment_actualTimeOut | datetimeoffset | Y |
| segment_regDuration | int | Y |
| segment_ot1Duration | int | Y |
| segment_ot2Duration | int | Y |
| segment_nonWorkDuration | int | Y |
| segment_unpaidDuration | int | Y |
| segment_cost | float | Y |
| segment_applyToDate | date | Y |
| legacyAssignmentId | int | Y |
| hash_key | varchar(64) | Y |
| assignedTo_companyId | varchar(max) | Y |
| assignedTo_employeeId | varchar(max) | Y |

### `std.paylocity_wav_shift_unified`  (rows: 79,618 | cols: 25 | PK: shiftId, employeeId)

| Column | Type | Null? |
|---|---|---|
| **shiftId** | int | N |
| scheduleId | int | Y |
| isPublished | bit | Y |
| isDeleted | bit | Y |
| companyId | varchar(50) | Y |
| **employeeId** | varchar(50) | N |
| startDateTime | datetimeoffset | Y |
| duration | int | Y |
| hasNote | bit | Y |
| isEmployeeNote | bit | Y |
| costCenters | nvarchar(max) | Y |
| segment_payType | varchar(50) | Y |
| segment_actualTimeIn | datetimeoffset | Y |
| segment_actualTimeOut | datetimeoffset | Y |
| segment_regDuration | int | Y |
| segment_ot1Duration | int | Y |
| segment_ot2Duration | int | Y |
| segment_nonWorkDuration | int | Y |
| segment_unpaidDuration | int | Y |
| segment_cost | float | Y |
| segment_applyToDate | date | Y |
| legacyAssignmentId | int | Y |
| hash_key | varchar(64) | Y |
| assignedTo_companyId | varchar(max) | Y |
| assignedTo_employeeId | varchar(max) | Y |

### `std.paylocity_ev_punches`  (rows: 1,046,003 | cols: 42)

| Column | Type | Null? |
|---|---|---|
| employeeId | nvarchar(50) | Y |
| driver_uuid | nvarchar(50) | Y |
| date | date | Y |
| clock_in | datetime | Y |
| lunch_start_time | datetime | Y |
| lunch_end_time | datetime | Y |
| clock_out | datetime | Y |
| lunch_hours | decimal | Y |
| total_hours | decimal | Y |
| total_earnings | decimal | Y |
| costCenterId | varchar(50) | Y |
| durationHours | varchar(50) | Y |
| shiftEnd | varchar(max) | Y |
| earnings | varchar(50) | Y |
| isActive | varchar(50) | Y |
| origin | varchar(50) | Y |
| relativeOriginalStart | varchar(50) | Y |
| shiftStart | varchar(max) | Y |
| companyId | varchar(50) | Y |
| previous_origin | varchar(50) | Y |
| relativeStart | varchar(50) | Y |
| name | varchar(100) | Y |
| badgeNumber | varchar(50) | Y |
| relativeEnd | varchar(50) | Y |
| durationSeconds | varchar(50) | Y |
| level | varchar(50) | Y |
| update_count | varchar(50) | Y |
| code | varchar(50) | Y |
| previous_durationSeconds | varchar(50) | Y |
| previous_date | varchar(50) | Y |

_+ 12 more columns (truncated for brevity):_ previous_punchType, last_updated_at, relativeOriginalEnd, previous_relativeOriginalEnd, previous_earnings, id, costCenters, punchID, previous_relativeOriginalStart, punchType, first_seen_at, Light_Duty

### `std.paylocity_wav_punches`  (rows: 335,429 | cols: 42)

| Column | Type | Null? |
|---|---|---|
| employeeId | nvarchar(50) | Y |
| date | date | Y |
| clock_in | datetime | Y |
| lunch_start_time | datetime | Y |
| lunch_end_time | datetime | Y |
| clock_out | datetime | Y |
| lunch_hours | decimal | Y |
| total_hours | decimal | Y |
| total_earnings | decimal | Y |
| costCenterId | varchar(50) | Y |
| durationHours | varchar(50) | Y |
| shiftEnd | varchar(max) | Y |
| earnings | varchar(50) | Y |
| isActive | varchar(50) | Y |
| origin | varchar(50) | Y |
| relativeOriginalStart | varchar(50) | Y |
| shiftStart | varchar(max) | Y |
| companyId | varchar(50) | Y |
| previous_origin | varchar(50) | Y |
| relativeStart | varchar(50) | Y |
| name | varchar(100) | Y |
| badgeNumber | varchar(50) | Y |
| relativeEnd | varchar(50) | Y |
| durationSeconds | varchar(50) | Y |
| level | varchar(50) | Y |
| update_count | varchar(50) | Y |
| code | varchar(50) | Y |
| previous_durationSeconds | varchar(50) | Y |
| previous_date | varchar(50) | Y |
| previous_punchType | varchar(50) | Y |

_+ 12 more columns (truncated for brevity):_ last_updated_at, relativeOriginalEnd, previous_relativeOriginalEnd, previous_earnings, id, costCenters, punchID, previous_relativeOriginalStart, punchType, first_seen_at, driver_uuid, Light_Duty

### `ref.paylocity_all_employees_basic`  (rows: 9,881 | cols: 7)

| Column | Type | Null? |
|---|---|---|
| id | nvarchar(50) | Y |
| companyId | nvarchar(50) | Y |
| relationshipId | nvarchar(50) | Y |
| lastName | nvarchar(50) | Y |
| displayName | nvarchar(50) | Y |
| status | nvarchar(50) | Y |
| statusType | nvarchar(50) | Y |

### `ref.paylocity_all_employees_detail`  (rows: 9,845 | cols: 11 | PK: employeeId)

| Column | Type | Null? |
|---|---|---|
| **employeeId** | varchar(50) | N |
| coEmpCode | varchar(50) | Y |
| firstName | varchar(50) | Y |
| lastName | varchar(50) | Y |
| status_employeeStatus | varchar(50) | Y |
| workAddress_state | varchar(50) | Y |
| homeAddress_emailAddress | varchar(100) | Y |
| companyName | varchar(50) | Y |
| departmentPosition_jobTitle | varchar(100) | Y |
| primaryStateTax_taxCode | varchar(50) | Y |
| preferredName | varchar(50) | Y |

### `ref.paylocity_av_employees_basic`  (rows: 54 | cols: 7)

| Column | Type | Null? |
|---|---|---|
| id | varchar(20) | N |
| companyId | varchar(10) | Y |
| relationshipId | varchar(20) | Y |
| lastName | varchar(100) | Y |
| displayName | varchar(100) | Y |
| status | varchar(20) | Y |
| statusType | varchar(20) | Y |

### `ref.paylocity_ev_employees_basic`  (rows: 8,181 | cols: 7 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | varchar(20) | N |
| companyId | varchar(10) | Y |
| relationshipId | varchar(20) | Y |
| lastName | varchar(100) | Y |
| displayName | varchar(100) | Y |
| status | varchar(20) | Y |
| statusType | varchar(20) | Y |

### `ref.paylocity_wav_employees_basic`  (rows: 2,931 | cols: 7)

| Column | Type | Null? |
|---|---|---|
| id | nvarchar(255) | Y |
| companyId | nvarchar(max) | Y |
| relationshipId | nvarchar(max) | Y |
| lastName | nvarchar(max) | Y |
| displayName | nvarchar(max) | Y |
| status | nvarchar(max) | Y |
| statusType | nvarchar(max) | Y |

### `ref.paylocity_deduction_codes`  (rows: 91 | cols: 33)

| Column | Type | Null? |
|---|---|---|
| row_hash | nvarchar(64) | Y |
| companyId | nvarchar(20) | Y |
| code | nvarchar(50) | Y |
| description | nvarchar(100) | Y |
| checkStubDescription | nvarchar(max) | Y |
| priority | nvarchar(max) | Y |
| w2Box | nvarchar(max) | Y |
| printOnCheckStub | nvarchar(max) | Y |
| payPeriodMaximum | nvarchar(max) | Y |
| payPeriodMinimum | nvarchar(max) | Y |
| annualMaximum | nvarchar(max) | Y |
| rate | nvarchar(max) | Y |
| calculationCode | nvarchar(max) | Y |
| amount | nvarchar(max) | Y |
| kCode | nvarchar(max) | Y |
| takePartial | nvarchar(max) | Y |
| autoMakeup | nvarchar(max) | Y |
| isActive | nvarchar(max) | Y |
| includeOnYtdCompChart | nvarchar(max) | Y |
| source | nvarchar(max) | Y |
| wasUsedInPayroll | nvarchar(max) | Y |
| selfInsured | nvarchar(max) | Y |
| isEmployerPaidMedicalLeave | nvarchar(max) | Y |
| exemptTaxes | nvarchar(max) | Y |
| blockedTaxes | nvarchar(max) | Y |
| type_code | nvarchar(max) | Y |
| type_category | nvarchar(max) | Y |
| type_calculationCode | nvarchar(max) | Y |
| type_overrideCalculationCode | nvarchar(max) | Y |
| type_w2Box | nvarchar(max) | Y |

_+ 3 more columns (truncated for brevity):_ type_isGarnishmentDedType, agency, benefitType

### `ref.paylocity_earning_codes`  (rows: 96 | cols: 33)

| Column | Type | Null? |
|---|---|---|
| row_hash | nvarchar(64) | Y |
| companyId | nvarchar(20) | Y |
| code | nvarchar(50) | Y |
| description | nvarchar(100) | Y |
| checkStubDescription | nvarchar(max) | Y |
| printOnCheckStub | nvarchar(max) | Y |
| payPeriodMaximum | nvarchar(max) | Y |
| payPeriodMinimum | nvarchar(max) | Y |
| annualMaximum | nvarchar(max) | Y |
| overrideRate | nvarchar(max) | Y |
| addToRate | nvarchar(max) | Y |
| rateMultiplier | nvarchar(max) | Y |
| amount | nvarchar(max) | Y |
| rate | nvarchar(max) | Y |
| reduceAutoPay | nvarchar(max) | Y |
| costCenterMatrixId | nvarchar(max) | Y |
| isActive | nvarchar(max) | Y |
| includeInHoursWorked | nvarchar(max) | Y |
| includeOnYtdCompChart | nvarchar(max) | Y |
| source | nvarchar(max) | Y |
| wasUsedInPayroll | nvarchar(max) | Y |
| selfInsured | nvarchar(max) | Y |
| isEmployerPaidMedicalLeave | nvarchar(max) | Y |
| classificationCode | nvarchar(max) | Y |
| type_code | nvarchar(max) | Y |
| type_description | nvarchar(max) | Y |
| type_calculationCode | nvarchar(max) | Y |
| type_overrideCalculationCode | nvarchar(max) | Y |
| type_w2Box | nvarchar(max) | Y |
| type_isFringeBenefit | nvarchar(max) | Y |

_+ 3 more columns (truncated for brevity):_ w2Box, relatedDeductionCode, benefitType

### `ref.paylocity_ev_employee_documents`  (rows: 95,321 | cols: 9)

| Column | Type | Null? |
|---|---|---|
| employeeId | nvarchar(50) | Y |
| category | nvarchar(50) | Y |
| companyConfidential | nvarchar(50) | Y |
| employeeConfidential | nvarchar(50) | Y |
| documentId | nvarchar(100) | Y |
| companyId | nvarchar(50) | Y |
| displayName | nvarchar(500) | Y |
| receivedDate | nvarchar(100) | Y |
| uploadedDate | nvarchar(100) | Y |

### `ref.paylocity_av_employee_documents`  (rows: 0 | cols: 9)

| Column | Type | Null? |
|---|---|---|
| employeeId | nvarchar(50) | Y |
| category | nvarchar(50) | Y |
| companyConfidential | nvarchar(50) | Y |
| employeeConfidential | nvarchar(50) | Y |
| documentId | nvarchar(100) | Y |
| companyId | nvarchar(50) | Y |
| displayName | nvarchar(500) | Y |
| receivedDate | nvarchar(100) | Y |
| uploadedDate | nvarchar(100) | Y |

### `ref.paylocity_wav_employee_documents`  (rows: 26,956 | cols: 9)

| Column | Type | Null? |
|---|---|---|
| employeeId | nvarchar(50) | Y |
| category | nvarchar(50) | Y |
| companyConfidential | nvarchar(50) | Y |
| employeeConfidential | nvarchar(50) | Y |
| documentId | nvarchar(100) | Y |
| companyId | nvarchar(50) | Y |
| displayName | nvarchar(500) | Y |
| receivedDate | nvarchar(100) | Y |
| uploadedDate | nvarchar(100) | Y |

### `ref.paylocity_document_downloads_av`  (rows: 0 | cols: 6 | PK: downloadId)

| Column | Type | Null? |
|---|---|---|
| **downloadId** | int | N |
| documentId | nvarchar(64) | N |
| downloadUrl | nvarchar(max) | N |
| expiresIn | int | N |
| generatedAt | datetime2 | N |
| expiresAt | datetime2 | N |

### `ref.paylocity_document_downloads_ev`  (rows: 1,520 | cols: 6 | PK: downloadId)

| Column | Type | Null? |
|---|---|---|
| **downloadId** | int | N |
| documentId | nvarchar(64) | N |
| downloadUrl | nvarchar(max) | N |
| expiresIn | int | N |
| generatedAt | datetime2 | N |
| expiresAt | datetime2 | N |

### `ref.paylocity_document_downloads_wav`  (rows: 193 | cols: 6 | PK: downloadId)

| Column | Type | Null? |
|---|---|---|
| **downloadId** | int | N |
| documentId | nvarchar(64) | N |
| downloadUrl | nvarchar(max) | N |
| expiresIn | int | N |
| generatedAt | datetime2 | N |
| expiresAt | datetime2 | N |

### `ref.paylocity_document_ocr_rename_av`  (rows: 0 | cols: 13 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| documentId | nvarchar(64) | N |
| sharePointItemId | nvarchar(255) | Y |
| status | nvarchar(20) | N |
| oldFileName | nvarchar(500) | Y |
| newFileName | nvarchar(500) | Y |
| extractedLastName | nvarchar(100) | Y |
| extractedFirstName | nvarchar(100) | Y |
| extractedBirthYear | nvarchar(4) | Y |
| extractedDlFirst4 | nvarchar(10) | Y |
| issuingState | nvarchar(2) | Y |
| processedAt | datetime2 | N |
| rotationApplied | smallint | Y |

### `ref.paylocity_document_ocr_rename_ev`  (rows: 760 | cols: 13 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| documentId | nvarchar(64) | N |
| sharePointItemId | nvarchar(255) | Y |
| status | nvarchar(20) | N |
| oldFileName | nvarchar(500) | Y |
| newFileName | nvarchar(500) | Y |
| extractedLastName | nvarchar(100) | Y |
| extractedFirstName | nvarchar(100) | Y |
| extractedBirthYear | nvarchar(4) | Y |
| extractedDlFirst4 | nvarchar(10) | Y |
| issuingState | nvarchar(2) | Y |
| processedAt | datetime2 | N |
| rotationApplied | smallint | Y |

### `ref.paylocity_document_ocr_rename_wav`  (rows: 191 | cols: 13 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| documentId | nvarchar(64) | N |
| sharePointItemId | nvarchar(255) | Y |
| status | nvarchar(20) | N |
| oldFileName | nvarchar(500) | Y |
| newFileName | nvarchar(500) | Y |
| extractedLastName | nvarchar(100) | Y |
| extractedFirstName | nvarchar(100) | Y |
| extractedBirthYear | nvarchar(4) | Y |
| extractedDlFirst4 | nvarchar(10) | Y |
| issuingState | nvarchar(2) | Y |
| processedAt | datetime2 | N |
| rotationApplied | smallint | Y |

### `ref.paylocity_document_sharepoint_uploads_av`  (rows: 0 | cols: 5 | PK: uploadId)

| Column | Type | Null? |
|---|---|---|
| **uploadId** | int | N |
| documentId | nvarchar(64) | N |
| sharePointFileName | nvarchar(500) | N |
| sharePointItemId | nvarchar(255) | Y |
| uploadedAt | datetime2 | N |

### `ref.paylocity_document_sharepoint_uploads_ev`  (rows: 760 | cols: 5 | PK: uploadId)

| Column | Type | Null? |
|---|---|---|
| **uploadId** | int | N |
| documentId | nvarchar(64) | N |
| sharePointFileName | nvarchar(500) | N |
| sharePointItemId | nvarchar(255) | Y |
| uploadedAt | datetime2 | N |

### `ref.paylocity_document_sharepoint_uploads_wav`  (rows: 191 | cols: 5 | PK: uploadId)

| Column | Type | Null? |
|---|---|---|
| **uploadId** | int | N |
| documentId | nvarchar(64) | N |
| sharePointFileName | nvarchar(500) | N |
| sharePointItemId | nvarchar(255) | Y |
| uploadedAt | datetime2 | N |

### `ref.adp_punches`  (rows: 607,273 | cols: 14)

| Column | Type | Null? |
|---|---|---|
| Uber_Unique_ID | nvarchar(100) | Y |
| First_Name | nvarchar(50) | Y |
| Last_Name | nvarchar(50) | Y |
| Position_ID | time | Y |
| Home_Department_Description | nvarchar(50) | Y |
| Location_Description | nvarchar(50) | Y |
| Location_Code | nvarchar(50) | Y |
| In_Date | date | Y |
| Time_In | time | Y |
| Out_Date | date | Y |
| Time_Out | time | Y |
| Pay_Code_Timecard | nvarchar(50) | Y |
| Hours | float | Y |
| position_id_final | int | Y |

### `ref.scheduled_training_verification`  (rows: 13 | cols: 31 | PK: id)

| Column | Type | Null? |
|---|---|---|
| **id** | int | N |
| first_name | varchar(100) | Y |
| preferred_name | varchar(100) | Y |
| last_name | varchar(100) | Y |
| date_of_birth | datetimeoffset | Y |
| ssn | nvarchar(50) | Y |
| scheduled_training_date | datetimeoffset | Y |
| tower_business | varchar(50) | Y |
| personal_email1 | varchar(100) | Y |
| personal_email2 | varchar(100) | Y |
| tower_email | varchar(100) | Y |
| personal_phone_number | nvarchar(50) | Y |
| uber_phone_number | nvarchar(50) | Y |
| drivers_license_number | varchar(50) | Y |
| driver_license_state | varchar(50) | Y |
| uber_onboarding_status | varchar(50) | Y |
| uber_driver_uuid | varchar(50) | Y |
| driver_status | varchar(50) | Y |
| policy_effective | date | Y |
| policy_ineffective | date | Y |
| job_title | varchar(100) | Y |
| drivers_license_expiration_date | date | Y |
| drivers_license_restrictions | varchar(500) | Y |
| veteran | bit | Y |
| rehire | bit | N |
| documents_verified | bit | Y |
| inserted_at | datetime2 | Y |
| updated_at | datetime2 | Y |
| showed_up | int | N |
| paylocity_employee_id | varchar(20) | Y |

_+ 1 more columns (truncated for brevity):_ paylocity_created_at

### `std.tower_driver_policies`  (rows: 7,272 | cols: 10)

| Column | Type | Null? |
|---|---|---|
| ID | nvarchar(50) | Y |
| FIRSTNAME | nvarchar(50) | Y |
| LASTNAME | nvarchar(50) | Y |
| DOB | nvarchar(50) | Y |
| LICENSENUMBER | nvarchar(50) | Y |
| LICENSESTATE | nvarchar(50) | Y |
| DRIVERSTATUS | nvarchar(50) | Y |
| EFFECTIVE | nvarchar(50) | Y |
| INEFFECTIVE | nvarchar(50) | Y |
| POLICYNUMBER | nvarchar(50) | Y |

### `std.tower_vehicle_policies`  (rows: 363 | cols: 14)

| Column | Type | Null? |
|---|---|---|
| VIN | nvarchar(50) | Y |
| YEAR | nvarchar(50) | Y |
| MAKE | nvarchar(50) | Y |
| MODEL | nvarchar(50) | Y |
| SEATINGCAPACTIY | nvarchar(50) | Y |
| WHEELCHAIRACCESS | nvarchar(50) | Y |
| STATEREGISTERED | nvarchar(50) | Y |
| EFFECTIVE | nvarchar(50) | Y |
| INEFFECTIVE | nvarchar(50) | Y |
| FHV | nvarchar(max) | Y |
| REPLACEMENTVEHICLE | nvarchar(max) | Y |
| LOCATIONID | nvarchar(max) | Y |
| OWNERID | nvarchar(max) | Y |
| POLICYNUMBER | nvarchar(50) | Y |

### `ref.tower_policies`  (rows: 8 | cols: 15)

| Column | Type | Null? |
|---|---|---|
| POLICYNUMBER | nvarchar(50) | Y |
| POLICYSEQ | nvarchar(50) | Y |
| POLICYTYPE | nvarchar(100) | Y |
| POLICYCATEGORY | nvarchar(50) | Y |
| INSURANCECOMPANY | nvarchar(100) | Y |
| INSURANCECOMPANY_ADDR1 | nvarchar(100) | Y |
| INSURANCECOMPANY_ADDR2 | nvarchar(50) | Y |
| INSURANCECOMPANY_CITY | nvarchar(50) | Y |
| INSURANCECOMPANY_STATE | nvarchar(50) | Y |
| INSURANCECOMPANY_POSTALCODE | nvarchar(50) | Y |
| EFFECTIVE | nvarchar(50) | Y |
| EXPIRATION | nvarchar(50) | Y |
| LIMITS | nvarchar(50) | Y |
| DEDUCTIBLE | nvarchar(50) | Y |
| STATUS | nvarchar(50) | Y |

<!-- AUTO:END tables -->

## Notes on specific tables

- **`ref.paylocity_all_employees_basic`/`_detail`** — a company-wide roster. Row counts (9,881 / 9,845) don't cleanly equal the sum of the three fleet `*_basic` tables (8,144 + 2,929 + 51 = 11,124), so this looks like a separately-sourced consolidated feed rather than a strict union of the three — verify before assuming it's exhaustive across fleets.
- **`ref.adp_punches`** — legacy/alternate time data from **ADP**, a different payroll platform than Paylocity. Joins to Uber via `Uber_Unique_ID` directly. **Data quality flag:** `Position_ID` is typed `time` in the live schema, which is almost certainly a load-time type-inference bug (a position ID being cast as a clock time) — treat that column's values with suspicion and check `position_id_final` (typed `int`) instead.
- **`ref.paylocity_deduction_codes`** / **`ref.paylocity_earning_codes`** — glossary tables mapping the short pay codes seen in `*_payments.detCode` to human-readable descriptions (`description`, `checkStubDescription`) and tax/benefit metadata. Use these to translate a payments query's raw codes for a non-technical reader.
- **`ref.paylocity_ev_employee_documents`** — metadata about uploaded HR documents (category, display name, received/uploaded dates) — not the documents themselves.
- **`ref.scheduled_training_verification`** — pre-hire pipeline tracking: candidates scheduled for driver training/onboarding, with license info, Uber onboarding status, and a `showed_up` flag. Likely feeds the recruiting scripts (`employee_paylocity_create.py`, `employee_paylocity_prep.py`) — not directly verified this session.
- **`std.tower_driver_policies`** / **`std.tower_vehicle_policies`** / **`ref.tower_policies`** — Tower's own commercial insurance records (broker/insurer export — note the ALL-CAPS column names, a strong signal this is sourced from a different system than Paylocity's camelCase convention). `tower_driver_policies` = insured-driver roster, `tower_vehicle_policies` = insured-vehicle roster (includes `WHEELCHAIRACCESS`/`FHV` flags — this is where WAV-specific vehicle compliance data lives), `tower_policies` = the master policy documents (insurer, coverage limits, deductible, effective/expiration dates).
