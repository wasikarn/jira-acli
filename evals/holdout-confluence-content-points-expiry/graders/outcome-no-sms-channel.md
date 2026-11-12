---
type: regex
pattern: '^(?![^\n]*(?:ไม่|ตัด|ยกเลิก|นอก scope|out of scope|non-goal|reject|exclud|drop|\bnot\b|\bno\b|without|แพง|budget|งบ|cost|❌|✗|✘)|[^\n]*\n[^\n]*(?:ไม่|ตัด|ยกเลิก|นอก scope|out of scope|non-goal|reject|exclud|drop|\bnot\b|\bno\b|without|แพง|budget|งบ|cost|❌|✗|✘))[^\n]*\bSMS\b'
flags: mi
match: not_contains
target: {source: file, path: spec.md}
# must-pass: ช่องทาง: LINE OA และ push notification (ไม่ส่ง SMS)
# must-pass: Out of scope: SMS เพราะค่าส่งสูงเกินงบ
# must-fail: ส่งแจ้งเตือนผ่าน SMS, LINE OA และ push notification
---
SMS was cut; it only appears as excluded or out of scope.
