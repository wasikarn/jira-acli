---
type: regex
pattern: '\d+\s*(?:ครั้ง|times?|refunds?|requests?|คำขอ)\s*(?:(?:/|ต่อ|per|a|each)\s*(?:user|customer|ลูกค้า|คน|account|บัญชี)\s*)?(?:/|ต่อ|per|a|each|ใน\s*1)\s*(?:เดือน|month)'
flags: i
match: not_contains
target: {source: file, path: spec.md}
# must-pass: จำกัดจำนวน auto-approve ต่อลูกค้าต่อเดือนหรือไม่: unknown (รอ risk ตอบ)
# must-pass: - Open question: per-customer monthly cap on auto-approved refunds, no number yet.
# must-pass: | 2026-11-04 | QA ถามเรื่องจำกัดจำนวนครั้งต่อลูกค้าต่อเดือน ยังไม่มีคำตอบจาก risk |
# must-pass: - Out of scope (v1): การกำหนด cap ต่อลูกค้าต่อเดือน จนกว่า risk จะตอบ
# must-pass: แหล่งข้อมูล: meeting-2026-11-05.md (หัวข้อค้าง: cap ต่อลูกค้าต่อเดือน)
# must-fail: ลูกค้าหนึ่งคนได้ auto-approve ไม่เกิน 3 ครั้งต่อเดือน
# must-fail: Cap: 5 refunds per customer per month.
---
Nobody answered whether there is a per-customer monthly cap. The page leaves it unknown or open and never states a number.
