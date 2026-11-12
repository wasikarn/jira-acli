---
type: regex
pattern: '(?:2026-12-01|\b1 Dec(?:ember)? 2026|Dec(?:ember)? 1,? 2026)[\s\S]*(?:2026-12-15|15 Dec(?:ember)? 2026|Dec(?:ember)? 15,? 2026)'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: Shadow mode from 2026-12-01; enforcement from 2026-12-15.
# must-pass: Shadow mode starts December 1, 2026 and enforcement December 15, 2026.
# must-fail: Enforcement from 2026-12-15 after a shadow period.
---
The page gives the shadow-mode start date and then the enforcement date.
