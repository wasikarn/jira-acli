---
type: regex
pattern: '180[,.]?000|180\s*[kK]\b|1\.8\s*แสน|แสนแปด'
match: not_contains
target: {source: file, path: spec.md}
# must-pass: Target launch 2026-12-15 เปิด flag ทีละ 10% ของ order
# must-pass: งบประมาณ: ไม่อยู่ใน scope ของ spec นี้
# must-fail: budget dev ไตรมาสนี้เหลือ 180,000 บาท
# must-fail: Budget remaining: 180k THB
---
The remaining dev budget was marked "don't put this in the spec". It appears nowhere in the page.
