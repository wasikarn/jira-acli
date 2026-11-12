---
type: regex
pattern: '2026-12-15|15\s?(?:ธ\.ค\.|ธันวาคม|Dec)'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: เป้า launch: 2026-12-15
# must-pass: Launch target: 15 ธันวาคม 2026
# must-fail: เป้า launch: กลางเดือนธันวาคม
---
The page carries the launch target date.
