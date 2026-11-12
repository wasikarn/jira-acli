---
type: regex
pattern: 'ผู้ตัดสินใจ|Decided by|Decision makers?|Approved by|Owners?\s*\**\s*[:：]'
flags: i
match: contains
target: {source: file, path: comment.md}
# must-pass: **ผู้ตัดสินใจ:** Arm (BE lead), June (PM)
# must-pass: Decided by: Reporting sync (Arm, June, Pete, Fah)
# must-fail: Decision: async export.
---
The comment names who decided or owns it.
