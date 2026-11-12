---
type: regex
pattern: '(?:กำหนดให้|Given)\s*[:：][\s\S]*?(?:เมื่อ|When)\s*[:：][\s\S]*?(?:ผลลัพธ์|Then)\s*[:：][\s\S]*?(?:กำหนดให้|Given)\s*[:：][\s\S]*?(?:เมื่อ|When)\s*[:：][\s\S]*?(?:ผลลัพธ์|Then)\s*[:：][\s\S]*?(?:กำหนดให้|Given)\s*[:：][\s\S]*?(?:เมื่อ|When)\s*[:：][\s\S]*?(?:ผลลัพธ์|Then)\s*[:：]'
flags: i
match: contains
target: {source: file, path: spec.md}
# must-pass: AC1 กำหนดให้: a เมื่อ: b ผลลัพธ์: c AC2 กำหนดให้: d เมื่อ: e ผลลัพธ์: f AC3 กำหนดให้: g เมื่อ: h ผลลัพธ์: i
# must-pass: Given: a When: b Then: c / Given: d When: e Then: f / Given: g When: h Then: i
# must-fail: - The API returns 429 over the limit.
# must-fail: AC1 กำหนดให้: a เมื่อ: b ผลลัพธ์: c AC2 กำหนดให้: d เมื่อ: e ผลลัพธ์: f
---
At least three Given/When/Then acceptance criteria.
