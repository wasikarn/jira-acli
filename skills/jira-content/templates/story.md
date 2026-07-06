# Story — type-specific guide

Loaded by `jira-acli:jira-content` Step 1–2. The shared metadata table, preview gate, and create commands live in `SKILL.md`; AC rules (including the Story-only coverage additions) live in [`acceptance-criteria.md`](../../../templates/acceptance-criteria.md) — this file holds only the Story-specific gather questions and Thai description template.

## Step 1 — Gather (Story)

Ask the user (all at once, not one by one):

1. **Feature name** — short Thai title, action-oriented (e.g. "หักยอดคงเหลือตอนลูกค้ายืนยันการสั่งซื้อ") — full rule + anti-patterns: [`title-conventions.md`](title-conventions.md)
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
* ผลลัพธ์: [expected outcome — be specific, plain business language only]

**AC2 — [Short title]**
...

---

📎 อ้างอิงการตัดสินใจเชิงเทคนิค: [spec or ADR if applicable]
```

**AC format/register/coverage rules (including the Story-only additions — per-surface, fallback):** [`acceptance-criteria.md`](../../../templates/acceptance-criteria.md) — single source, don't restate.

Then proceed to `SKILL.md` Step 3 (metadata — Story uses `Story` issue type, `Medium` priority default, no environment/versions rows) → Step 4 (preview) → Step 5 (create).