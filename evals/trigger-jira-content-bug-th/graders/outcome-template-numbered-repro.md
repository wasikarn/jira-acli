---
type: regex
pattern: '^\s*1[.)]\s'
flags: m
match: contains
target: {source: file, path: ticket.md}
# must-pass: 1. เปิดแอป
# must-pass:   1) Open the app
# must-fail: - เปิดแอป
---
Reproduction is a numbered list.
