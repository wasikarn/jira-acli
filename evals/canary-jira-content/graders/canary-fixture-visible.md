---
type: regex
pattern: 'CANARY-7731'
match: contains
target: {source: file, path: notes.txt}
---
File-target graders read the scaffolded working directory.
