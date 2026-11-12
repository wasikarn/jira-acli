---
type: regex
pattern: 'Siam\s?Freight|churn'
flags: i
match: not_contains
target: {source: file, path: comment.md}
# must-pass: Large merchants are affected.
# must-pass: Escalated by merchants via account management.
# must-fail: Siam Freight is escalating and may churn.
---
The escalating merchant was a side note marked not for the ticket.
