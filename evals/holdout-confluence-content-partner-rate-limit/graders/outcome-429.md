---
type: regex
pattern: '\b429\b'
match: contains
target: {source: file, path: spec.md}
# must-pass: Over the limit, the API returns HTTP 429.
# must-pass: Status 429 Too Many Requests
# must-fail: Over the limit, requests are rejected.
---
The page gives the status code returned over the limit.
