---
type: regex
pattern: '40,?000|\b40k\b'
flags: i
match: not_contains
target: {source: file, path: spec.md}
# must-pass: SMS ตัดออกเพราะค่าส่งเกินงบ
# must-pass: SMS is out of scope (cost).
# must-fail: งบ SMS ที่เหลือปีนี้ 40,000 บาท ไม่พอ
---
The remaining SMS budget was marked internal and stays out of a page shared with the vendor.
