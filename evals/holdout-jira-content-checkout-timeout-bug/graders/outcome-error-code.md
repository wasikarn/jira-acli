---
type: regex
pattern: 'ERR_PAYMENT_TIMEOUT'
match: contains
target: {source: file, path: ticket.md}
# must-pass: API ตอบ 504 พร้อม error code `ERR_PAYMENT_TIMEOUT`
# must-pass: Error: ERR_PAYMENT_TIMEOUT (HTTP 504)
# must-fail: API ตอบ 504 payment timeout
---
The ticket carries the exact error code from the log.
