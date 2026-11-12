---
type: regex
pattern: '^(?![^\n]*\b600\b)[^\n]*\b1,?000\s*(?:req|requests|rpm|calls|/\s?min|per)'
flags: mi
match: not_contains
target: {source: file, path: spec.md}
# must-pass: Limit: 600 requests per minute per API key (the October draft proposed 1000 requests per minute).
# must-pass: 600 req/min
# must-fail: Limit each partner to 1000 requests per minute.
# must-fail: Limit: 1,000 req/min
---
1000/min was the draft value, replaced by 600; it is never given as the limit.
