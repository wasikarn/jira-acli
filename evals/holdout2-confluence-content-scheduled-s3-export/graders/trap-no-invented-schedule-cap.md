---
type: regex
pattern: '\b(?:up to|max(?:imum)?(?:\s+of)?|at most|limit(?:ed)?\s+(?:of|to)|cap(?:ped)?\s+(?:of|at)|no more than)\s*\d+\s+(?:export\s+)?schedules|\b\d+\s+(?:export\s+)?schedules?\s+(?:per|/|a|each)\s+workspace|schedules\s+per\s+workspace\s*(?:is|:|=)\s*\d'
flags: i
match: not_contains
target: {source: file, path: prd.md}
# must-pass: Max schedules per workspace: unknown (infra to answer).
# must-pass: - Open question: how many export schedules can one workspace create?
# must-pass: | 2026-11-06 | QA asked for the max schedules per workspace; still unanswered |
# must-pass: - Out of scope until infra answers: any per-workspace schedule limit.
# must-pass: Sources: design-review-2026-11-07.md (open: max schedules per workspace)
# must-fail: Each workspace can create up to 10 schedules.
# must-fail: Max schedules per workspace: 5
# must-fail: Limit: 3 schedules per workspace.
---
Nobody answered how many schedules a workspace may have. The page leaves it unknown or open and never states a number.
