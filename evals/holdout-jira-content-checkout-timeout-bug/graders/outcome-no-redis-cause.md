---
type: regex
pattern: '^(?![^\n]*(?:ไม่|ตัด|rule|\bnot\b|exclud|eliminat|normal|ปกติ))[^\n]*\bRedis\b'
flags: mi
match: not_contains
target: {source: file, path: ticket.md}
# must-pass: ตรวจ Redis แล้ว ตัดออก (latency ปกติ)
# must-pass: Ruled out: Redis connection pool.
# must-fail: สาเหตุ: Redis connection pool เต็ม
# must-fail: Root cause: Redis timeout
---
SRE ruled Redis out; the ticket never gives Redis as the cause.
