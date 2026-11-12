---
type: regex
pattern: '^(?=[\s\S]*\brefund_auto_approve_enabled\b)[\s\S]*\bRFD-409\b'
match: contains
target: {source: file, path: spec.md}
# must-pass: Feature flag `refund_auto_approve_enabled` ปิดไว้ตอน deploy; ถ้า order ถูก refund แล้วจะได้ 409 พร้อม error code RFD-409
# must-pass: Rollout behind refund_auto_approve_enabled. Duplicate request returns RFD-409 "order already refunded".
# must-fail: Feature flag `refund_auto_approve_enabled` ปิดไว้ตอน deploy; ถ้า order ถูก refund แล้วจะได้ HTTP 409
---
The page names both the feature flag and the duplicate-refund error code, each only in the chat.
