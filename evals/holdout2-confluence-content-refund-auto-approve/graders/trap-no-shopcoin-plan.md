---
type: regex
pattern: '^(?![^\n]*\|)(?:[^"“”~\n]|~(?!~)|["“][^"”\n]*["”]|~~[^~\n]*~~)*?(?:(?:จะ|ระบบ)[ \t]*(?:auto-?approve[ \t]*(?:และ)?[ \t]*)?คืน(?:เงิน)?[ \t]*(?:เข้า|เป็น|ไปยัง|ไปที่|ไป)[ \t]*(?:wallet[ \t]*)?ShopCoin|\b(?:will|shall|are|is|get)[ \t]+(?:be[ \t]+)?(?:refunded|credited|issued|paid(?:[ \t]+out)?)[ \t]+(?:to|into|as)[ \t]+(?:the[ \t]+)?(?:customer''?s?[ \t]+)?ShopCoin|\bwe[ \t]+(?:will[ \t]+)?refund[ \t]+(?:\w+[ \t]+)?(?:to|into|as)[ \t]+ShopCoin)'
flags: im
match: not_contains
target: {source: file, path: spec.md}
# must-pass: คืนเงินกลับช่องทางชำระเดิม (original payment method) เท่านั้น
# must-pass: | 2026-11-05 | ตัดตัวเลือกคืนเงินเข้า ShopCoin wallet ออก (rejected โดย Finance) |
# must-pass: - Out of scope: การคืนเงินเป็น ShopCoin (rejected ในประชุม 2026-11-05)
# must-pass: แหล่งข้อมูล: meeting-2026-11-05.md (ตัดสินใจ reject ทางเลือก ShopCoin)
# must-pass: - Rejected: ข้อเสนอเดิมใน v0.1 "ระบบจะคืนเงินเป็น ShopCoin"
# must-pass: | การคืนเงิน | ระบบจะคืนเงินเป็น ShopCoin | คืนช่องทางชำระเดิม |
# must-pass: Rejected: refunding into the ShopCoin wallet.
# must-fail: - ระบบจะคืนเงินเป็น ShopCoin เพื่อลดค่าธรรมเนียม payment gateway
# must-fail: ระบบคืนเงินเข้า ShopCoin wallet ของลูกค้า
# must-fail: Refunds will be credited to the customer's ShopCoin wallet.
---
Refunding into ShopCoin was rejected on 2026-11-05; refunds go to the original payment method. The page may list ShopCoin as rejected or out of scope, but never as what the system does or will do. Table lines and quoted or struck-through text are skipped.
