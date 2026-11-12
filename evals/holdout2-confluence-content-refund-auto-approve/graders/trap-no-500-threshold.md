---
type: regex
pattern: '^(?![^\n]*\|)(?:[^"“”~\n]|~(?!~)|["“][^"”\n]*["”]|~~[^~\n]*~~)*?(?:อนุมัติ|approv(?:e|es|ed|al))[^\n|"“()]*?(?:ไม่เกิน|ต่ำกว่า|น้อยกว่า|≤|<=|<|under|below|up to|at most|not exceeding)\s*(?:฿\s*)?500(?![\d,])(?!\s*(?:บาท|THB|฿)?\s*(?:→|->|=>|(?:เปลี่ยน|ลด)?\s*เป็น|(?:changed |reduced |lowered )?to\b))|^[ \t]*(?:[-*+][ \t]+|\d+[.)][ \t]+)?(?:\*\*)?(?:auto-?approve[ \t]+)?(?:threshold|เพดาน(?:ยอด)?|วงเงิน)(?:[ \t]*auto-?approve)?(?:\*\*)?[ \t]*[:=][ \t]*(?:\*\*)?[ \t]*(?:ไม่เกิน[ \t]*|≤[ \t]*|<=?[ \t]*)?(?:฿[ \t]*)?500(?![\d,])(?![ \t]*(?:บาท|THB|฿)?[ \t]*(?:→|->|=>))'
flags: im
match: not_contains
target: {source: file, path: spec.md}
# must-pass: อนุมัติอัตโนมัติเมื่อยอด refund ไม่เกิน 300 บาท
# must-pass: | 2026-11-06 | ลด threshold จาก 500 บาท เป็น 300 บาท ตาม finance |
# must-pass: | 2026-11-03 | เงื่อนไขตั้งต้น: ยอดไม่เกิน 500 บาท | superseded 2026-11-06 |
# must-pass: | เงื่อนไขยอด refund | ไม่เกิน 500 บาท | ไม่เกิน 300 บาท |
# must-pass: - threshold เดิม 500 บาท (v0.1) ถูกแทนด้วย 300 บาท แล้ว
# must-pass: - Out of scope: threshold 500 → 300 ถูกยกเลิกไปแล้ว ไม่ใช้ค่าเดิม
# must-pass: แหล่งข้อมูล: old-draft-spec.md (v0.1, ใช้ค่า 500 บาท ซึ่ง superseded แล้ว)
# must-pass: Threshold was 500 baht in v0.1 and changed to 300 baht on 2026-11-06.
# must-pass: Auto-approve refunds up to ฿300 (was up to ฿500 in v0.1).
# must-pass: - ~~ระบบอนุมัติอัตโนมัติเมื่อยอดไม่เกิน 500 บาท~~ (superseded)
# must-pass: Threshold: 500 → 300 บาท
# must-fail: - ระบบอนุมัติ refund อัตโนมัติเมื่อยอดคืนไม่เกิน 500 บาท
# must-fail: Threshold: 500 บาท
# must-fail: - **Threshold:** ≤ ฿500
# must-fail: Auto-approve refunds under ฿500.
---
The 500-baht threshold was superseded by 300 baht on 2026-11-06. The page may name 500 as old, replaced or superseded (history or before/after table, out-of-scope item, sources line, strikethrough, quote), but never states it as the current rule: an approve rule capped at 500, or a line that leads with `threshold: 500`. Table lines and quoted or struck-through text are skipped.
