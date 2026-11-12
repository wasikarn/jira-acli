---
type: regex
pattern: '\bSHOP-2141\b'
match: contains
target: {source: file, path: spec.md}
# must-pass: Epic: SHOP-2141
# must-pass: หน้านี้เป็น spec ของ Epic SHOP-2141 (refund auto-approve)
# must-fail: Epic: SHOP-214
---
The page links back to the Epic named in the chat and the old draft.
