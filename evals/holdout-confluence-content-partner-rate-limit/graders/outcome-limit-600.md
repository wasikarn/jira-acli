---
type: regex
pattern: '\b600\b'
match: contains
target: {source: file, path: spec.md}
# must-pass: Each API key may send 600 requests per minute.
# must-pass: Limit: 600 req/min per API key
# must-fail: Each API key may send 1000 requests per minute.
---
The agreed limit is 600 requests per minute per API key.
