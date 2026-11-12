---
type: regex
pattern: '\b3\.4\s?%'
match: contains
target: {source: file, path: ticket.md}
# must-pass: checkout fail 3.4% ของ request ตั้งแต่ 20:05
# must-pass: Failure rate: 3.4 % of checkout requests
# must-fail: error rate ของ checkout ขึ้นไป 12%
---
The corrected checkout failure rate is 3.4%.
