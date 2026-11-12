---
type: regex
pattern: 'partner_rate_limit_enforce'
match: contains
target: {source: file, path: spec.md}
# must-pass: Rollout is gated by `partner_rate_limit_enforce`.
# must-pass: เปิดใช้ผ่าน flag partner_rate_limit_enforce ใน shadow mode ก่อน
# must-fail: Rollout is gated by a feature flag.
---
The page names the rollout flag.
