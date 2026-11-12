---
type: regex
pattern: '^(?=[\s\S]*/v1/exports/schedules\b)[\s\S]*\bscheduled_export_s3\b'
match: contains
target: {source: file, path: prd.md}
# must-pass: Customers create a schedule with `POST /v1/exports/schedules`; the feature is gated by `scheduled_export_s3` (off by default).
# must-pass: | API | POST /v1/exports/schedules | Flag | scheduled_export_s3 |
# must-fail: Customers create a schedule with `POST /v1/exports/schedules`; the feature sits behind a feature flag.
---
The page names the endpoint and the feature flag from the thread.
