---
type: regex
pattern: '^(?=[\s\S]*\b30\s?(?:วัน|days?|-day))[\s\S]*\b7\s?(?:วัน|days?|-day)'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: แจ้งเตือนล่วงหน้า 30 วัน และ 7 วัน ก่อนแต้มหมดอายุ
# must-pass: Reminders at 30 days and 7 days before expiry.
# must-fail: แจ้งล่วงหน้า 30 วัน
---
There are two reminders: 30 days and 7 days before expiry.
