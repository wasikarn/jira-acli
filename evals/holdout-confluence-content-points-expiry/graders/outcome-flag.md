---
type: regex
pattern: 'loyalty_expiry_notify'
match: contains
target: {source: file, path: spec.md}
# must-pass: เปิดผ่าน feature flag `loyalty_expiry_notify` เริ่มที่ 10% ของสมาชิก
# must-pass: Rollout flag: loyalty_expiry_notify
# must-fail: เปิดผ่าน feature flag เริ่มที่ 10% ของสมาชิก
---
The page names the rollout flag.
