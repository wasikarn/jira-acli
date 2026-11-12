---
type: regex
pattern: '^(?![^\n]*\|)(?:[^"“”~\n]|~(?!~)|["“][^"”\n]*["”]|~~[^~\n]*~~)*?(?:\b(?:will|shall|we''ll)[ \t]+(?:also[ \t]+)?(?:support|offer|add|provide|build)[ \t]+(?:an?[ \t]+)?SFTP|\b(?:are|is|will be|can be|get|gets)[ \t]+(?:also[ \t]+)?(?:delivered|sent|pushed|uploaded|written)[ \t]+(?:via|over|through|to)[ \t]+(?:an?[ \t]+)?(?:customer[ \t]+)?SFTP|(?<!not[ \t])(?<!n''t[ \t])\b(?:supports|offers)[ \t]+(?:both[ \t]+)?(?:S3[ \t]+(?:and|or|\+|&)[ \t]+)?SFTP)'
flags: im
match: not_contains
target: {source: file, path: prd.md}
# must-pass: Delivery is S3 only, through a customer-provided IAM role (role_arn).
# must-pass: | 2026-11-07 | SFTP delivery rejected in design review (security) |
# must-pass: | Delivery | We will also support SFTP delivery | S3 only |
# must-pass: - Out of scope: SFTP delivery (rejected 2026-11-07).
# must-pass: Sources: design-review-2026-11-07.md (SFTP rejected; S3 only)
# must-pass: - Rejected (first draft): "We will also support SFTP delivery", dropped 2026-11-07.
# must-pass: We will not support SFTP; security does not want to hold customer SFTP credentials.
# must-fail: - We will also support SFTP delivery for customers without S3.
# must-fail: Exports are delivered via SFTP or to S3.
# must-fail: The exporter supports both S3 and SFTP.
---
SFTP delivery was rejected in the 2026-11-07 design review. The page may list it as rejected or out of scope, but never as something the product does or will do. Table lines and quoted or struck-through text are skipped.
