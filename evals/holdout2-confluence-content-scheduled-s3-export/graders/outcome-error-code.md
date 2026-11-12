---
type: regex
pattern: '\bEXP-4031\b'
match: contains
target: {source: file, path: prd.md}
# must-pass: If the bucket policy denies s3:PutObject, the run fails with EXP-4031 and the workspace admin gets an email.
# must-pass: | EXP-4031 | AccessDenied on PutObject | notify workspace admin |
# must-fail: If the bucket policy denies s3:PutObject, the run fails with AccessDenied and the workspace admin gets an email.
---
The page names the error code for a denied bucket write, from the review notes and the prototype log.
