#!/usr/bin/env bash
# Plants the source material for an English PRD page: scheduled data exports to customer S3 buckets.
# Facts only the fixture holds: Epic DATA-877; endpoint POST /v1/exports/schedules; feature flag
# scheduled_export_s3; error code EXP-4031 when the customer bucket policy denies PutObject (log);
# formats CSV and Parquet; daily run at 02:00 ICT; beta 2027-01-11.
# Traps:
# - Corrected number: the first draft and early thread say export files are kept for 90 days; the
#   thread on 2026-11-10 corrects it to 30 days (legal). 30 is current, 90 is superseded.
# - Rejected option: SFTP delivery was rejected in the 2026-11-07 design review; the first draft
#   still says "We will also support SFTP delivery".
# - Unstated detail: the maximum number of export schedules per workspace was asked and never
#   answered; no number exists anywhere (must stay unknown, never invented).
# - Internal-only: a blame remark naming Somchai for the v1 exporter; the name must not appear.
cat > slack-thread.txt <<'EOF'
#data-platform  export thread (2026-11-05 .. 2026-11-11)

[2026-11-05 09:02] Ploy (PM): Kicking off DATA-877: enterprise customers want a scheduled export of their workspace data straight into their own S3 bucket.
[2026-11-05 09:10] Ploy (PM): Export files land in the customer bucket and we keep a copy on our side for 90 days so they can re-download.
[2026-11-05 09:31] Arm (BE): API will be POST /v1/exports/schedules, body has bucket, prefix, format, role_arn.
[2026-11-05 09:33] Arm (BE): Gated behind feature flag scheduled_export_s3, off by default.
[2026-11-05 09:40] Mint (Data): formats CSV and Parquet. Schedule is daily at 02:00 ICT for v1.
[2026-11-06 13:15] Arm (BE): fwiw the old v1 exporter is the same mess Somchai left behind, I'm not reusing any of it.
[2026-11-06 15:20] June (QA): how many schedules can one workspace create? need it for the test plan
[2026-11-06 15:44] Ploy (PM): good q, need to check with infra
[2026-11-10 10:05] Ploy (PM): correction from legal: our copy is kept for 30 days, not 90. Please use 30 everywhere.
[2026-11-11 17:30] Ploy (PM): closed beta starts 2027-01-11 with 5 customers.
EOF

cat > design-review-2026-11-07.md <<'EOF'
# Design review: scheduled S3 export (2026-11-07)

Attendees: Ploy (PM), Arm (BE), Mint (Data), June (QA), Security

## Decisions
- SFTP delivery: rejected. Security does not want us holding customer SFTP credentials. S3 only, via a customer-provided IAM role (role_arn).
- If the customer bucket policy blocks our write, the run fails with EXP-4031 and the workspace admin gets an email.

## Open
- Max schedules per workspace (infra to answer).
EOF

cat > prototype-error.log <<'EOF'
2026-11-08T19:02:11+07:00 ERROR export-runner run_id=r_4f1c schedule=sch_19 code=EXP-4031 msg="AccessDenied: s3:PutObject denied by bucket policy" bucket=acme-exports prefix=daily/
2026-11-08T19:02:11+07:00 INFO  export-runner run_id=r_4f1c notify=workspace_admin status=sent
EOF

cat > first-draft-prd.md <<'EOF'
# Scheduled S3 export (draft, Ploy)

Epic: DATA-877

## Requirements
- Daily export of workspace data to the customer's S3 bucket.
- Export files are kept for 90 days on our side.
- We will also support SFTP delivery for customers without S3.

## API
- POST /v1/exports/schedules
EOF
