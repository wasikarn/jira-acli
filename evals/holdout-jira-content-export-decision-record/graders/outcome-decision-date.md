---
type: regex
pattern: '2026-11-11|11 Nov(?:ember)?,? 2026|Nov(?:ember)? 11,? 2026'
match: contains
target: {source: file, path: comment.md}
# must-pass: Decided 2026-11-11 in the reporting sync.
# must-pass: Decision date: 11 November 2026
# must-fail: Decided in this week's reporting sync.
---
The decision record carries the decision date.
