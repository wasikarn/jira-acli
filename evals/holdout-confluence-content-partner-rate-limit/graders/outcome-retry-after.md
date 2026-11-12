---
type: regex
pattern: 'Retry-After'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: Every 429 carries a `Retry-After` header in seconds.
# must-pass: 429 responses include Retry-After.
# must-fail: 429 responses tell the client when to retry.
---
The 429 response carries a Retry-After header.
