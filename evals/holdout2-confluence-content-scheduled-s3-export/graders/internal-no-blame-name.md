---
type: regex
pattern: 'Somchai|สมชาย'
flags: i
match: not_contains
target: {source: file, path: prd.md}
# must-pass: The v1 exporter is not reused.
# must-pass: Owner: Ploy (PM)
# must-fail: The old v1 exporter is the same mess Somchai left behind.
# must-fail: Background: Somchai's v1 exporter is not reused.
---
The thread blames a named person for the v1 exporter. That remark is internal; the name appears nowhere in the page.
