---
type: regex
pattern: 'canary-bash-ok'
match: contains
target: {source: file, path: bash-ok.txt}
---
A plain Bash call succeeded with the plugin's hooks loaded.
