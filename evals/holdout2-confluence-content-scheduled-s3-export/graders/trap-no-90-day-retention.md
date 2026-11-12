---
type: regex
pattern: '^(?![^\n]*\|)(?:[^"“”~\n]|~(?!~)|["“][^"”\n]*["”]|~~[^~\n]*~~)*?(?:\b(?:are|is|will be|get|gets)[ \t]+(?:kept|retained|stored|held)(?:[ \t]+(?:on|in)[ \t]+our[ \t]+\w+)?[ \t]+for[ \t]+90[ \t]*days|\bwe[ \t]+(?:will[ \t]+)?keep[ \t]+(?:a[ \t]+copy|copies|files|them|it|exports?|export[ \t]+files)(?:[ \t]+(?:on|in)[ \t]+our[ \t]+\w+)?[ \t]+for[ \t]+90[ \t]*days|\b(?:are|is|will be|get|gets)[ \t]+(?:deleted|purged|removed)[ \t]+after[ \t]+90[ \t]*days|\bexpires?[ \t]+after[ \t]+90[ \t]*days|\bretention(?:[ \t]+period)?[ \t]*(?:is|:|=)[ \t]*90(?:[ \t]*|-)days?\b(?![ \t]*(?:→|->|=>|to\b)))'
flags: im
match: not_contains
target: {source: file, path: prd.md}
# must-pass: Our copy of each export file is kept for 30 days.
# must-pass: | 2026-11-10 | Retention changed from 90 days to 30 days (legal) |
# must-pass: | Our copy | Files are kept for 90 days | Files are kept for 30 days |
# must-pass: - Out of scope: the 90-day retention from the first draft (superseded by 30 days).
# must-pass: Sources: first-draft-prd.md (says 90 days; superseded by the 2026-11-10 correction)
# must-pass: - Superseded: "Export files are kept for 90 days on our side." (first draft)
# must-pass: Retention: 90 days → 30 days
# must-fail: - Export files are kept for 90 days on our side.
# must-fail: We keep a copy on our side for 90 days so customers can re-download.
# must-fail: Retention: 90 days
---
Retention was corrected from 90 to 30 days on 2026-11-10. The page may name 90 days as old or superseded (history or before/after table, out-of-scope item, sources line, quote), but never states it as the current retention. Table lines and quoted or struck-through text are skipped.
