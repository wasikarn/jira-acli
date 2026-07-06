# Title / Summary conventions — shared across Bug/Story/Task/Epic/Sub-task

Referenced by every `jira-content` template's Step 1 gather question and every `*.payload.json`'s
`summary` field. Edit here, not per-template — same consolidation reasoning as
[`acceptance-criteria.md`](../../../templates/acceptance-criteria.md): the old scattered-copies setup let rules drift
out of sync, so cross-cutting rules live once, referenced everywhere.

**Grounded in:** Atlassian's own [bug-report template](https://www.atlassian.com/software/jira/templates/bug-report)
guidance ("the summary can be as short as a few words as long as it makes it easy for team members
to identify the bug") and the general issue-title best-practice consensus (imperative-verb lead for
work items, behavior/user-focused phrasing for user-facing issues, skimmable in a backlog list
without opening the ticket, acts as a memory aid for the reader).

## Rules for every type

- **Thai, one line, no trailing period.** Same register as the description body.
- **Skimmable without opening the ticket.** Someone scanning a backlog list should know what the
  ticket is about from the title alone.
- **State WHAT, not WHY-we-noticed-it or HOW-we'll-fix-it.** Root cause and fix approach belong in
  the description (Evidence / Technical Notes), not the title — a title front-loaded with a
  diagnosis reads wrong the moment the real cause turns out different, and then needs a rename.
- **No `[Area]` bracket prefix by default.** `labels` already carries the domain/area tag (see
  `SKILL.md` Step 3 — bug gets `bug` + 1-2 domain tags, others get 1-2 domain tags) — a bracket
  prefix in the title duplicates that field for no gain. Skip it unless the team can't filter or
  group by label in their list view. **Exception: Sub-task** — its bracket carries the **parent
  key**, not an area, which is not covered by any other field; see the table below.
- **One ticket, one title.** If the title needs "และ"/"กับ" to describe it, it's two tickets.

## Per-type pattern

| Type | Pattern | Example |
|---|---|---|
| Bug | Symptom, behavior-focused, present tense — what's observably wrong | "ยอดคงเหลือไม่ถูกหักหลังลูกค้ายืนยันการสั่งซื้อ" |
| Story | The outcome the user gets once shipped | "หักยอดคงเหลือตอนลูกค้ายืนยันการสั่งซื้อ" |
| Task | Imperative verb + concrete object — describes the work, not the user value | "เพิ่ม index ตาราง orders ให้ query ยืนยันคำสั่งซื้อ" |
| Epic | Noun-phrase naming the initiative — broader in scope than a single fix | "ระบบคิดค่าบริการแบบ Traffic-based สำหรับ Campaign" |
| Sub-task | `[PARENT-KEY] ` + imperative + a slice narrow enough to tell apart from sibling sub-tasks | "[TP-809] เขียน migration เพิ่มคอลัมน์ display_time_id" |

## Anti-patterns

- **Vague:** "บั๊กหน้า login" — a bug about what, exactly, on that page?
- **Diagnosis-in-title:** "เพราะ null pointer ตอน settle" — that's the root cause, which belongs in
  the description's Evidence section, not the symptom the title should carry.
- **Multi-issue:** "แก้ settlement + เพิ่ม logging + refactor retry" — split into 3 tickets.
- **Redundant with nothing:** "Bug in payment" — a scanner gains nothing actionable from it.
