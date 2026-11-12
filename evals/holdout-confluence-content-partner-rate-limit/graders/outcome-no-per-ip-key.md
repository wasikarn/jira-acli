---
type: regex
pattern: '^(?![^\n]*(?:reject|\bnot\b|\bno\b|instead|rather|out of scope|non-goal|drop|because|NAT|alternative|considered|won|exclud)|[^\n]*\n[^\n]*(?:reject|\bnot\b|\bno\b|instead|rather|out of scope|non-goal|drop|because|NAT|alternative|considered|won|exclud))[^\n]*(?:per[- ]IP|source IP|IP[- ]based|by IP|client IP)'
flags: mi
match: not_contains
target: {source: file, path: spec.md}
# must-pass: The limit is keyed on the API key, not the source IP, because many partners share one NAT egress IP.
# must-pass: Rejected: per-IP limits (partners share NAT IPs).
# must-fail: Key the limit on source IP.
# must-fail: Limits are applied per-IP.
---
Keying on source IP was rejected; it only appears as rejected.
