---
type: regex
pattern: '^(?![^\n]*(?:reject|\bnot\b|\bno\b|declin|drop|instead|rather|considered|alternative|option|stays|remain|won)|[^\n]*\n[^\n]*(?:reject|\bnot\b|\bno\b|declin|drop|instead|rather|considered|alternative|option|stays|remain|won))[^\n]*\b120\s?(?:s\b|sec|seconds?)'
flags: mi
match: not_contains
target: {source: file, path: comment.md}
# must-pass: Rejected: raising the gateway timeout to 120s (org-wide 60s limit, needs a security exception).
# must-pass: Option 1, raise the timeout to 120 seconds, was rejected.
# must-fail: We will raise the gateway timeout to 120s for this route.
---
Raising the gateway timeout to 120s was rejected; it only appears as a rejected option.
