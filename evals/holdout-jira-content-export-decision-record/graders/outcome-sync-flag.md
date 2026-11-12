---
type: regex
pattern: 'reports\.sync_export_enabled'
match: contains
target: {source: file, path: comment.md}
# must-pass: The old GET stays for one release behind `reports.sync_export_enabled`.
# must-pass: Flag reports.sync_export_enabled keeps the sync export for one more release.
# must-fail: The old endpoint stays behind a feature flag for one release.
---
The record names the flag that keeps the old endpoint for one release.
