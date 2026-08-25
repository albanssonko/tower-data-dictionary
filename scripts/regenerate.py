"""
Daily regeneration of the auto-generated column-reference tables in
data_dictionary/01_*.md through 06_*.md.

Only the content between the markers
    <!-- AUTO:BEGIN tables ... -->
    <!-- AUTO:END tables -->
in each file is replaced. Everything else (narrative, "Notes on specific
tables" sections, etc.) is hand-written and left untouched.

Requires: pip install python-tds certifi pyOpenSSL
Env vars (read-only DB login — do not point this at a write-capable account):
    DB_SERVER    e.g. towermobility.database.windows.net
    DB_DATABASE  e.g. tower_mobility_db1
    DB_USER      e.g. svc_claude_desktop_ro
    DB_PASSWORD

TLS note: connects with cafile=certifi.where() (TLS required by Azure SQL) and
validate_host=False. Encryption stays on either way; validate_host=False only
skips pytds's own post-handshake hostname re-check, which currently crashes
(AttributeError: 'X509' object has no attribute 'get_extension') against
current pyOpenSSL — a pytds/pyOpenSSL API-compat bug, not something fixable
here. DB_SERVER is a hardcoded, known endpoint, never user input, so skipping
that specific re-check was judged an acceptable tradeoff (confirmed with the
user 2026-08-25) rather than disabling TLS itself.
"""
import os
import re
import sys
import certifi
import pytds

DB_SERVER = os.environ["DB_SERVER"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # data_dictionary/

BEGIN_RE = re.compile(r"<!-- AUTO:BEGIN tables.*?-->\n")
END_RE = re.compile(r"<!-- AUTO:END tables -->")

PKS = {
    "std.uber_driver_trip_payments": ["transaction_UUID"],
    "std.uber_ev_timeline": ["DriverUuid", "Event", "EventEpochMs"],
    "std.uber_wav_driver_activity": ["DriverUUID", "StartTime"],
    "ref.samsara_assets": ["id"],
    "std.uber_ev_driver_payments": ["DriverUUID", "StartTime"],
    "std.uber_wav_driver_quality": ["driver_uuid", "start_time"],
    "std.uber_ev_driver_locations": ["DriverUuid", "LocationEpochMs"],
    "ref.mail_domains": ["id"],
    "ref.ims_users": ["id"],
    "ref.ims_roles": ["id"],
    "std.uber_ev_driver_performance": ["_id"],
    "std.uber_ev_rtd_offers": ["id"],
    "ref.ims_permissions": ["id"],
    "ref.ims_companies": ["id"],
}

DOMAINS = {
    "01_hr_payroll.md": [
        "std.paylocity_av_employees_detail", "std.paylocity_ev_employees_detail", "std.paylocity_wav_employees_detail",
        "std.paylocity_av_payments", "std.paylocity_ev_payments", "std.paylocity_wav_payments",
        "std.paylocity_ev_paystatements_detail",
        "std.paylocity_av_shift_unified", "std.paylocity_ev_shift_unified", "std.paylocity_wav_shift_unified",
        "std.paylocity_ev_punches", "std.paylocity_wav_punches",
        "ref.paylocity_all_employees_basic", "ref.paylocity_all_employees_detail",
        "ref.paylocity_av_employees_basic", "ref.paylocity_ev_employees_basic", "ref.paylocity_wav_employees_basic",
        "ref.paylocity_deduction_codes", "ref.paylocity_earning_codes", "ref.paylocity_ev_employee_documents",
        "ref.adp_punches", "ref.scheduled_training_verification",
        "std.tower_driver_policies", "std.tower_vehicle_policies", "ref.tower_policies",
    ],
    "02_uber_trips_drivers.md": [
        "std.uber_ev_trip_activity", "std.uber_wav_trip_activity",
        "std.uber_ev_driver_activity", "std.uber_wav_driver_activity",
        "std.uber_ev_driver_quality", "std.uber_wav_driver_quality",
        "std.uber_ev_driver_payments", "std.uber_wav_driver_payments",
        "std.uber_ev_driver_locations",
        "std.uber_ev_driver_performance",
        "std.uber_ev_driver_transactions", "std.uber_wav_driver_transactions",
        "std.uber_ev_auto_pos", "std.uber_wav_auto_pos",
        "std.uber_ev_rtd_offers", "std.uber_ev_timeline",
        "std.uber_driver_trip_payments", "std.uber_org_payments",
        "ref.uber_drivers", "ref.uber_orgs", "ref.uber_vehicles",
        "ref.uber_shift_logs", "ref.uber_shift_logs_wav",
    ],
    "03_fleet_vehicles.md": [
        "std.fleetio_all_vehicles", "std.fleetio_contacts", "std.fleetio_part_location_details",
        "std.fleetio_shift_type_backfill", "std.fleetio_vehicle_renewals", "std.fleetio_vehicle_statuses",
        "ref.fleetio_vehicle_purchase_details",
        "std.service_tasks", "std.vehicle_inspections",
    ],
    "04_telematics_safety.md": [
        "std.samsara_drivers", "std.samsara_trips", "std.samsara_dva",
        "ref.samsara_assets", "ref.samsara_ev_safety_events",
        "ref.samsara_idle_times", "ref.samsara_idle_times_wav",
        "ref.samsara_onsite_location", "ref.samsara_onsite_location_wav",
        "ref.samsara_shift_min_distance", "ref.samsara_shift_min_distance_wav",
        "ref.samsara_tag",
    ],
    "05_ims_internal_ops.md": [
        "std.ims_announcements", "std.ims_drivers", "std.ims_employee_requests", "std.ims_employees",
        "std.ims_facilities_request_comments", "std.ims_facilities_requests", "std.ims_group_meetings",
        "std.ims_hr_clerk_mails", "std.ims_lost_found_items", "std.ims_marketing_request_comments",
        "std.ims_marketing_requests", "std.ims_network_devices", "std.ims_off_cycles", "std.ims_one_on_ones",
        "std.ims_qr_codes", "std.ims_security_alerts", "std.ims_sms_channels", "std.ims_sms_conversations",
        "std.ims_sms_messages", "std.ims_tesla_vehicles", "std.ims_wifi_passwords", "std.ims_work_request_comments",
        "std.ims_work_requests",
        "ref.ims_admin_settings", "ref.ims_companies", "ref.ims_permissions", "ref.ims_roles",
        "ref.ims_system_constants", "ref.ims_system_options", "ref.ims_system_settings", "ref.ims_users",
    ],
    "06_external_misc.md": [
        "ref.freshsales_contacts", "ref.driver_emails", "ref.mail_domains",
        "ref.weather", "ref.weather_codes",
        "ref.FuelAndEnergy", "ref.FuelAndEnergyWAV", "std.charging_sessions",
        "std.epn_review",
    ],
}


def fetch_metadata(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name, t.name, c.column_id, c.name, ty.name, c.max_length, c.is_nullable
        FROM sys.tables t
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        JOIN sys.columns c ON c.object_id = t.object_id
        JOIN sys.types ty ON ty.user_type_id = c.user_type_id
        WHERE s.name IN ('std','ref')
        ORDER BY s.name, t.name, c.column_id
    """)
    cols = {}
    for schema, table, _cid, col, dtype, length, nullable in cur.fetchall():
        key = f"{schema}.{table}"
        cols.setdefault(key, []).append({"col": col, "type": dtype, "len": length, "nullable": bool(nullable)})

    cur.execute("""
        SELECT s.name, t.name, SUM(p.rows)
        FROM sys.tables t
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0,1)
        WHERE s.name IN ('std','ref')
        GROUP BY s.name, t.name
    """)
    rowcounts = {f"{s}.{t}": rc for s, t, rc in cur.fetchall()}

    cur.execute("""
        SELECT s.name, t.name, c.name
        FROM sys.key_constraints kc
        JOIN sys.tables t ON t.object_id = kc.parent_object_id
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        JOIN sys.index_columns ic ON ic.object_id = kc.parent_object_id AND ic.index_id = kc.unique_index_id
        JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
        WHERE kc.type = 'PK' AND s.name IN ('std','ref')
    """)
    pks = {}
    for s, t, c in cur.fetchall():
        pks.setdefault(f"{s}.{t}", []).append(c)

    return cols, rowcounts, pks


def fmt_type(c):
    t, ln = c["type"], c["len"]
    if t in ("nvarchar", "nchar") and ln and ln > 0:
        return f"{t}({ln // 2})"
    if t in ("varchar", "char") and ln and ln > 0:
        return f"{t}({ln})"
    if t in ("nvarchar", "varchar") and ln == -1:
        return f"{t}(max)"
    return t


def format_table(key, cols, rowcounts, pks, max_cols=30):
    table_cols = cols.get(key)
    if not table_cols:
        return f"### `{key}`\n\n_Table not found in live schema — may have been renamed or dropped since this dictionary was written. Not auto-removed; check manually._\n\n"
    rc = rowcounts.get(key, 0) or 0
    pk = pks.get(key, [])
    lines = [f"### `{key}`  (rows: {rc:,} | cols: {len(table_cols)}{' | PK: ' + ', '.join(pk) if pk else ''})", ""]
    show = table_cols if len(table_cols) <= max_cols else table_cols[:max_cols]
    lines += ["| Column | Type | Null? |", "|---|---|---|"]
    for c in show:
        mark = "**" if c["col"] in pk else ""
        lines.append(f"| {mark}{c['col']}{mark} | {fmt_type(c)} | {'Y' if c['nullable'] else 'N'} |")
    if len(table_cols) > max_cols:
        remaining = [c["col"] for c in table_cols[max_cols:]]
        lines += ["", f"_+ {len(remaining)} more columns (truncated for brevity):_ {', '.join(remaining)}"]
    lines.append("")
    return "\n".join(lines)


def main():
    conn = pytds.connect(
        DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD, port=1433,
        cafile=certifi.where(), validate_host=False,
    )
    cols, rowcounts, pks = fetch_metadata(conn)

    all_known = set()
    for keys in DOMAINS.values():
        all_known.update(keys)
    unclassified = set(cols.keys()) - all_known
    if unclassified:
        print("WARNING — tables present in std/ref but not in any domain file's list "
              "(added to the DB since this dictionary was built; classify manually in "
              "regenerate.py's DOMAINS dict and re-run):")
        for t in sorted(unclassified):
            print(f"  - {t}")

    changed = []
    for filename, keys in DOMAINS.items():
        path = os.path.join(HERE, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        begin_m = BEGIN_RE.search(content)
        end_m = END_RE.search(content)
        if not begin_m or not end_m:
            print(f"SKIPPING {filename} — AUTO:BEGIN/END markers not found, won't touch a file I can't safely bound")
            continue

        new_tables = "".join(format_table(k, cols, rowcounts, pks) + "\n" for k in keys)
        new_content = content[:begin_m.end()] + new_tables + content[end_m.start():]

        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            changed.append(filename)

    if changed:
        print(f"Updated: {', '.join(changed)}")
    else:
        print("No changes — dictionary already matches live schema.")

    conn.close()


if __name__ == "__main__":
    sys.exit(main())
