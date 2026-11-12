---
type: regex
pattern: '^(?=[\s\S]*(?:เหตุผลทางธุรกิจ|Business reason|Background|Problem|ปัญหา))(?=[\s\S]*(?:ไม่อยู่ในขอบเขต|Out of scope|Non-goals?))'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: ## เหตุผลทางธุรกิจ ... **ไม่อยู่ในขอบเขตรอบนี้**
# must-pass: ## Business reason ... ### Out of scope
# must-fail: ## Overview ... ## Requirements
---
The page gives the business reason and what is out of scope.
