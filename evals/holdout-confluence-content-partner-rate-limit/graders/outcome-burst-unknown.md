---
type: regex
pattern: 'burst[^\n\d/]{0,30}(?!600\b|20\d\d\b)\d'
flags: i
match: not_contains
target: {source: file, path: spec.md}
# must-pass: Burst allowance above 600/min: unknown, depends on the Kong plugin options (open question).
# must-pass: Open question: do we allow short bursts above the limit? Not decided.
# must-pass: A few partners send bursts that slow /v2/partner/* for everyone.
# must-fail: Bursts of up to 100 extra requests are allowed for 10 seconds.
# must-fail: Burst allowance: 1200 requests.
---
Nobody answered the burst question; the page does not invent a burst size.
