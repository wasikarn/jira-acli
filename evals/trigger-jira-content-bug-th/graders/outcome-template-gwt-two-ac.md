---
type: regex
pattern: '(?:กำหนดให้|Given)\s*[:：][\s\S]*?(?:เมื่อ|When)\s*[:：][\s\S]*?(?:ผลลัพธ์|Then)\s*[:：][\s\S]*?(?:กำหนดให้|Given)\s*[:：][\s\S]*?(?:เมื่อ|When)\s*[:：][\s\S]*?(?:ผลลัพธ์|Then)\s*[:：]'
flags: i
match: contains
target: {source: file, path: ticket.md}
# must-pass: **AC1** * กำหนดให้: มีตะกร้า * เมื่อ: กดชำระ * ผลลัพธ์: สำเร็จ **AC2** * กำหนดให้: ปกติ * เมื่อ: กดชำระ * ผลลัพธ์: ทำงานแบบเดิม
# must-pass: AC1 Given: a cart When: I pay Then: it succeeds. AC2 Given: other flow When: I pay Then: unchanged
# must-fail: - [ ] ยืนยันว่า checkout สำเร็จ
# must-fail: AC1 กำหนดให้: a เมื่อ: b ผลลัพธ์: c
---
At least two Given/When/Then acceptance criteria (the template's Bug minimum: fix verified + regression).
