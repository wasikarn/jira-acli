---
type: regex
pattern: '^(?![^\n]*\b72)[^\n]*\b24\s?(?:h\b|hours?|-hour)'
flags: mi
match: not_contains
target: {source: file, path: comment.md}
# must-pass: Link expiry: 72 hours (the meeting notes said 24 hours; corrected the same day).
# must-pass: Links expire after 72h.
# must-fail: Download link expiry: 24 hours.
---
24 hours was corrected to 72; it is never given as the expiry (a line that also gives 72 may mention it).
