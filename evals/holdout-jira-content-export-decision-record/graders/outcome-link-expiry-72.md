---
type: regex
pattern: '\b72\s?(?:h\b|hours?|-hour)|\b(?:3|three)[- ]days?\b'
flags: i
match: contains
target: {source: file, path: comment.md}
# must-pass: Download links expire after 72 hours.
# must-pass: Signed link valid for 72h.
# must-fail: Download links expire after 24 hours.
---
Link expiry was corrected to 72 hours.
