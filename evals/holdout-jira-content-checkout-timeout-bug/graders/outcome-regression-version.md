---
type: regex
pattern: '\b3\.7\.0\b'
match: contains
target: {source: file, path: ticket.md}
# must-pass: เริ่มเกิดหลัง deploy order-svc 3.7.0 เมื่อ 2026-11-10 20:02
# must-pass: Regression in order-svc 3.7.0
# must-fail: เริ่มเกิดหลัง deploy ล่าสุด บน Android 4.18.2
---
The failures start with the order-svc 3.7.0 deploy; the ticket says which version.
