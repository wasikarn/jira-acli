---
type: regex
pattern: 'points-expiry-notifier[^\n]{0,60}(?:\d{1,2}[:.]\d{2}|\d\s?(?:โมง|am\b|pm\b|น\.)|ตี\s?\d)|\b[0-5]?\d\s+(?:[01]?\d|2[0-3])\s+\*\s+\*\s+\*'
flags: i
match: not_contains
target: {source: file, path: spec.md}
# must-pass: job points-expiry-notifier รันวันละครั้ง (เวลารัน: ยังไม่ได้กำหนด)
# must-pass: points-expiry-notifier runs once a day; the run time is unknown.
# must-fail: job points-expiry-notifier รันทุกวันเวลา 09:00 น.
# must-fail: Cron: 0 9 * * *
---
The job runs daily but nobody gave a time; the page does not invent one.
