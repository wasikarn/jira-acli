---
type: regex
pattern: '(?<![\d,.])300(?![\d,])'
match: contains
target: {source: file, path: spec.md}
# must-pass: อนุมัติอัตโนมัติเมื่อยอด refund ไม่เกิน 300 บาท
# must-pass: Threshold: ฿300 (finance sign-off 2026-11-06)
# must-fail: Threshold: ยังไม่สรุป
# must-fail: ยอด refund ไม่เกิน 3,000 บาท
---
The current threshold is 300 baht, set in the chat on 2026-11-06. The page states it.
