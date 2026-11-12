---
type: regex
pattern: '\bDATA-877\b'
match: contains
target: {source: file, path: prd.md}
# must-pass: Epic: DATA-877
# must-pass: This PRD covers DATA-877 (scheduled S3 export).
# must-fail: Epic: DATA-87
---
The page links back to the Epic named in the thread and the first draft.
