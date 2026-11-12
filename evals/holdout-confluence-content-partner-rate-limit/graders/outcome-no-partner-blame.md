---
type: regex
pattern: 'Zentra'
flags: i
match: not_contains
target: {source: file, path: spec.md}
# must-pass: A few partners send bursts that slow the API for everyone.
# must-pass: Trigger: INC-2291 on 2026-10-14.
# must-fail: Zentra is the main source of the bursts.
---
The partner named in the thread was marked not for the page.
