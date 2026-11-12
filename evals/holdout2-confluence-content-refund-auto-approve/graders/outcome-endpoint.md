---
type: regex
pattern: '/v2/refunds/\S*auto-approve'
match: contains
target: {source: file, path: spec.md}
# must-pass: | POST | /api/v2/refunds/{orderId}/auto-approve | อนุมัติ refund อัตโนมัติ |
# must-pass: BE เพิ่ม endpoint `POST /api/v2/refunds/{order_id}/auto-approve` แยกจาก flow manual
# must-fail: BE เพิ่ม endpoint ใหม่สำหรับ auto-approve แยกจาก flow manual
---
The page names the new endpoint from the chat.
