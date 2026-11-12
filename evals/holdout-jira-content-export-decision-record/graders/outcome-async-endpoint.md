---
type: regex
pattern: '/exports\b'
match: contains
target: {source: file, path: comment.md}
# must-pass: New endpoint: `POST /v1/reports/{reportId}/exports` returns 202 with an exportId.
# must-pass: Clients call POST /v1/reports/123/exports and get the link by email.
# must-fail: We will move the export to an async job.
---
The decision names the new async endpoint.
