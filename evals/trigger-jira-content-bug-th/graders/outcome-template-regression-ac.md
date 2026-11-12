---
type: regex
pattern: 'Regression|ทำงานแบบเดิม|ไม่ได้รับผลกระทบ'
flags: i
match: contains
target: {source: file, path: ticket.md}
# must-pass: **AC2 — ตรวจ Regression**
# must-pass: ผลลัพธ์: ทำงานแบบเดิม ไม่ได้รับผลกระทบจากการแก้ไข
# must-fail: ผลลัพธ์: ชำระเงินสำเร็จ
---
One acceptance criterion checks that unaffected flows still work.
