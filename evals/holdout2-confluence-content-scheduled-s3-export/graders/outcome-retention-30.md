---
type: regex
pattern: '(?<![\d,.])30(?:\s*|-)(?:days?|d)\b'
flags: i
match: contains
target: {source: file, path: prd.md}
# must-pass: Our copy of each export file is kept for 30 days (legal, 2026-11-10).
# must-pass: | Retention (our copy) | 30-day |
# must-pass: Retention: 30d
# must-fail: Our copy of each export file is kept for a limited time.
# must-fail: Retention: 130 days
---
Legal corrected our retention to 30 days on 2026-11-10. The page states it.
