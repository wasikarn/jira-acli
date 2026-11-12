---
type: regex
pattern: '^(?=[\s\S]*(?:ประเด็น|Issue|Context|Problem|Question)\s*\**\s*[:：])(?=[\s\S]*(?:ตัดสินใจ|Decision)\s*\**\s*[:：])(?=[\s\S]*(?:เหตุผล|Reason|Rationale|Why)\s*\**\s*[:：])'
match: contains
target: {source: file, path: comment.md}
# must-pass: **ประเด็น:** x **ตัดสินใจ:** y **เหตุผล:** z
# must-pass: Context: x. Decision: y. Rationale: z
# must-fail: We decided to go async because the gateway limit is fixed.
---
The comment has labelled issue, decision and reason fields.
