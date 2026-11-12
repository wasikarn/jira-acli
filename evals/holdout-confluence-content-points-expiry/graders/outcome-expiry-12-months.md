---
type: regex
pattern: '\b12\s?(?:เดือน|months?)|(?:\b1|หนึ่ง)\s?ปี|one year|\b1[- ]year'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: แต้มมีอายุ 12 เดือนนับจากวันที่ได้รับ
# must-pass: Points expire 12 months after they are earned.
# must-fail: แต้มมีอายุ 24 เดือนนับจากวันที่ได้รับ
---
Points expire after 12 months (the meeting corrected the old draft).
