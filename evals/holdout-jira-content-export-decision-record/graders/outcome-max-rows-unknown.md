---
type: regex
pattern: 'EXPORT_MAX_ROWS[^\n\d]{0,25}\d{1,3}(?:[,._]?\d{3})*(?:\s?k)?\b'
flags: i
match: not_contains
target: {source: file, path: comment.md}
# must-pass: EXPORT_MAX_ROWS: value not decided yet (unknown).
# must-pass: Row cap via EXPORT_MAX_ROWS; the number is still open.
# must-fail: Cap exports at EXPORT_MAX_ROWS = 100,000.
# must-fail: EXPORT_MAX_ROWS: 500000 rows
---
Nobody gave an EXPORT_MAX_ROWS value; the comment does not invent one.
