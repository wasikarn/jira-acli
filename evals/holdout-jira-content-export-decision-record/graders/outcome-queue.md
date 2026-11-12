---
type: regex
pattern: 'report-export\b'
match: contains
target: {source: file, path: comment.md}
# must-pass: A worker on the `report-export` queue builds the CSV.
# must-pass: Jobs go to the report-export queue.
# must-fail: A background worker builds the CSV.
---
The decision names the queue the worker reads.
