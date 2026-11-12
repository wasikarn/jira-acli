---
type: regex
pattern: 'ในฐานะ[\s\S]{0,160}ฉันต้องการ|\bAs an? [^\n]{0,100}\bI (?:want|need)'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: *ในฐานะ สมาชิก ฉันต้องการ รู้ว่าแต้มจะหมด เพื่อ ใช้ทัน*
# must-pass: As a partner account manager, I want to know the limit
# must-fail: R1: send a reminder
---
Requirements are written as user stories.
