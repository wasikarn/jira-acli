---
type: regex
pattern: '(?:อาการที่พบ|สิ่งที่เกิดขึ้นจริง|Actual)[\s\S]*(?:สิ่งที่ควรเป็น|ผลลัพธ์ที่ถูกต้อง|Expected)'
flags: i
match: contains
target: {source: file, path: ticket.md}
# must-pass: ## อาการที่พบ ... ## สิ่งที่ควรเป็น
# must-pass: Actual result: 504. Expected result: payment succeeds.
# must-fail: ## Summary: Checkout fails.
---
The bug states what happens and what should happen, in that order.
