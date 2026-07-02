# Story — type-specific guide

Loaded by `jira-acli:create-jira-ticket` Step 1–2. The shared metadata table, preview gate, create commands, AC rules, and failure modes live in `SKILL.md` — this file holds only the Story-specific gather questions, Thai description template, and Story-only AC coverage rules.

## Step 1 — Gather (Story)

Ask the user (all at once, not one by one):

1. **Feature name** — short Thai title, action-oriented (e.g. "หักยอดคงเหลือตอนลูกค้ายืนยันการสั่งซื้อ")
2. **Why are we doing this?** — business reason / problem being solved
3. **What should the system do?** — desired behavior in plain language
4. **What is OUT of scope this round?** — important for QA
5. **Any PO decision points?** — trade-offs or edge cases PO must sign off on
6. **Acceptance criteria** — rough testable behaviors (you will format them)

If the user already provided enough context, skip to Step 2.

## Step 2 — Format the issue (Story)

Write the description in **Thai** using this structure:

```
## 🎯 เหตุผลทางธุรกิจ (ทำไมต้องทำ)

[Current problem — 2-3 sentences. End with what we want to achieve.]

---

## ✅ พฤติกรรมที่ต้องการ

1. [what the system does]
2. [what the system does]

> ⚠️ [caveat about what does NOT happen]

---

## 📋 ขอบเขต (Scope)

**อยู่ในขอบเขตรอบนี้**
* [bullet list]

**ไม่อยู่ในขอบเขตรอบนี้ (สำคัญ — แจ้ง QA ให้ทราบ)**
* [bullet list]

---

## ⚠️ จุดที่ PO ต้องรับทราบและตัดสินใจร่วม

[Only include if there is a genuine decision point.]

---

## 🧪 เกณฑ์การยอมรับ (Acceptance Criteria) — สำหรับ QA

**AC1 — [Short title]**

* กำหนดให้: [precondition]
* เมื่อ: [action]
* ผลลัพธ์: [expected outcome — be specific, include field names / error codes where known]

**AC2 — [Short title]**
...

---

📎 อ้างอิงการตัดสินใจเชิงเทคนิค: [spec or ADR if applicable]
```

**AC formatting:** one titled block per AC (`**AC# — <short title>**`), each with `กำหนดให้` / `เมื่อ` / `ผลลัพธ์` on separate bullet lines — team-wide standard, not an escape hatch for complex cases only.

## AC coverage rules (Story only — in addition to the shared AC rules in SKILL.md)

- **Regression AC** for every out-of-scope item that touches the same flow.
- **Per-surface AC** for each screen/channel the change is visible on.
- **Boundary AC** for values that look missing but are real (e.g. 0 baht = free).
- **Fallback AC** for existing data without the new information.

Minimum 3 ACs: happy path + error/edge case + regression/permission. Then proceed to `SKILL.md` Step 3 (metadata — Story uses `Story` issue type, `Medium` priority default, no environment/versions rows) → Step 4 (preview) → Step 5 (create).