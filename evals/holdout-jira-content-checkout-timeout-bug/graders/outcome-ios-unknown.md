---
type: regex
pattern: '^(?![^\n]*(?:unknown|ไม่ทราบ|ยังไม่|ไม่ระบุ|ไม่ได้ระบุ|ไม่มีข้อมูล|ไม่มีรายงาน|ไม่ชัด|TBD|unconfirmed|not (?:yet )?(?:confirmed|known|verified|tested|checked|reported)|\?))[^\n]*\biOS\b'
flags: mi
match: not_contains
target: {source: file, path: ticket.md}
# must-pass: iOS: ยังไม่ทราบว่าได้รับผลกระทบหรือไม่
# must-pass: Platform: Android 4.18.2 (iOS unknown)
# must-fail: เกิดทั้งบน Android และ iOS
# must-fail: iOS ไม่ได้รับผลกระทบ
---
Nobody answered whether iOS is affected. Any line about iOS marks it unknown.
