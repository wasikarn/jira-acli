---
type: regex
pattern: '^(?![^\n]*3\.4)[^\n]*\b12\s?%'
flags: m
match: not_contains
target: {source: file, path: ticket.md}
# must-pass: Failure rate 3.4% (ตัวเลข 12% ที่โพสต์ก่อนหน้ารวม 5xx ทุก endpoint)
# must-pass: อัตรา error เฉพาะ checkout คือ 3.4%
# must-fail: error rate ของ checkout ขึ้นไป 12%
# must-fail: Impact: 12% of checkouts fail
---
12% was all 5xx on every endpoint and was corrected; it is never given as the checkout failure rate (a line that also gives 3.4% may mention it as the old figure).
