---
type: regex
pattern: '^(?![^\n]*\b12\s?(?:เดือน|months?))[^\n]*\b24\s?(?:เดือน|months?)'
flags: mi
match: not_contains
target: {source: file, path: spec.md}
# must-pass: แต้มมีอายุ 12 เดือน (draft v0.1 เขียน 24 เดือน ซึ่งผิด)
# must-pass: อายุแต้ม: 12 เดือน
# must-fail: แต้มมีอายุ 24 เดือนนับจากวันที่ได้รับ
---
24 months is the old, wrong value; it is never given as the expiry period.
