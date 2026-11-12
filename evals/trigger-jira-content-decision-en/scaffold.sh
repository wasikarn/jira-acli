#!/usr/bin/env bash
# Plants issue.txt (RPT-412 summary), meeting-notes.md and followup-thread.txt about CSV export timeouts.
# Facts only the fixture holds: decided 2026-11-11 to move to an async export: POST /v1/reports/{reportId}/exports
# returns 202 + exportId, a worker on the report-export queue builds the file, users get an emailed link;
# the old GET stays one release behind flag reports.sync_export_enabled.
# Traps: link expiry written as 24 hours in the notes, corrected to 72 hours in the follow-up thread; raising the
# gateway timeout to 120s was rejected (and pagination dropped); the EXPORT_MAX_ROWS value was never given (must
# stay unknown); the escalating merchant (Siam Freight, may churn) is a side note "not for the ticket".
cat > issue.txt <<'EOF'
RPT-412  Monthly sales report CSV export times out for large merchants
Type: Bug   Status: In Progress   Component: reporting-api
Description (short): GET /v1/reports/monthly/export returns 504 after 60s for merchants with very large reports.
EOF

cat > meeting-notes.md <<'EOF'
# Reporting sync - 2026-11-11
Attendees: Arm (BE lead), June (PM), Pete (SRE), Fah (FE)

## RPT-412 export timeouts
Options discussed:
1. Raise the gateway timeout for /v1/reports/monthly/export from 60s to 120s.
   - Pete: no. The 60s limit is org-wide on the API gateway; raising it for one route needs a security
     exception and would still fail for the biggest merchants.
2. Paginate the CSV into several files.
   - June: merchants open the file in Excel and want one file. Dropped.
3. Async export: POST /v1/reports/{reportId}/exports returns 202 with an exportId; a worker on the
   report-export queue builds the file; we email the user a signed download link.
   - Agreed.

Decision: option 3. Arm owns the backend, Fah the "export is being prepared" UI state.
Download link expiry: 24 hours.
The old GET endpoint stays for one release behind flag reports.sync_export_enabled, then it is removed.
Open: Arm says we need a cap on rows per export via EXPORT_MAX_ROWS.

(side note, not for the ticket: Siam Freight is the merchant escalating this; their account manager says they may churn.)
EOF

cat > followup-thread.txt <<'EOF'
[2026-11-11 16:20] June: Correction to the notes: link expiry is 72 hours, not 24. Merchants download on Monday what they requested on Friday.
[2026-11-11 16:24] Arm: OK, 72h.
[2026-11-11 16:31] Pete: For the record, the gateway timeout stays at 60s.
[2026-11-11 16:40] Fah: Do we have the EXPORT_MAX_ROWS value yet?
[2026-11-11 16:41] Arm: not yet
EOF
