> **Single Thai Bug/Story creation:** prefer `jira-acli:create-jira-ticket` for conversational, guided PO/QA-readable tickets with human confirmation. This directory remains the reference for terminal, ADF, bulk, and automation workflows.

# acli examples — description & body formats

GOOD/BAD reference for the #1 acli pitfall: **Jira uses ADF, Confluence uses storage XHTML, and `--from-json` is stricter than the flags.** Each pair shows WHY, not just WHAT.

Files here:

- `workitem-from-json.good.json` — valid `create-bulk --from-json` input (ADF description)
- `workitem-from-json.bad.json` — same intent, wrong description shape (do **not** use)
- `bug-template.json` — bug template (ADF), ready for `create --from-json`
- `story-template.json` — story template (user-centric work item)
- `epic-template.json` — epic template (high-level initiative)
- `task-template.json` — task (implementation work) template
- `subtask-template.json` — sub-task template (requires a parent)

---

## 0. Work-item templates (bug / story / epic / task / sub-task)

Five templates, each derived from real TP work items and standardized on ADF headings (the richest used headings; thinner ones used bold inline labels — headings win for scannability).

**Wording rules — apply to all five (the whole point):** concise, plain, on-point.
- One idea per line. State the behavior, not a story. Numbers/IDs/paths over prose.
- No vague language: not "ใช้ไม่ได้" but *what* fails *when* (Atlassian bug-report guidance).
- **Acceptance Criteria** — each **yes/no testable** (Specific, Testable, Clear; Atlassian acceptance-criteria guidance). Format: **Given/When/Then** — one titled block per AC (`**AC# — <short title>**` then `กำหนดให้` / `เมื่อ` / `ผลลัพธ์` on separate bullet lines). Team-wide standard (Head of Engineering) — always use it, not a fallback reserved for complex behavior. Two rules separate an AC a PO/QA can sign off from one they can't:
  - **No technical terms.** An AC must read for a PO/QA with no eng background. ❌ field/column names (`order_status`, `entity_type`), enum values (`TYPE_A`), API paths (`GET /admin/x/:id`), DB refs (`INSERT INTO`, foreign key). ✅ plain business nouns (ยอดคงเหลือ, วันหมดอายุ, ช่องทางการขาย), baht/day counts (500 บาท, หมดอายุ 30 วัน), and outcomes the user **sees** — not what the DB stores.
  - **Cover past the happy path** (each still its own AC block): error/empty case · permission/auth · a boundary value that looks empty but is real (ราคา 0 บาท = "ฟรี", ไม่ใช่ "ยังไม่ตั้งราคา") · for any "ไม่อยู่ในขอบเขตรอบนี้" item on the same flow, an AC asserting old behavior is unchanged `(Regression check)`.
- Sub-task = **one clear action**; don't over-layer the hierarchy (agile breakdown guidance).
- If a section has nothing real to say, delete it — don't pad.

### Bug — `bug-template.json`

Derived from TP-418, 447, 455, 457, 460, 461.

```bash
acli jira workitem create --from-json ${CLAUDE_SKILL_DIR}/examples/bug-template.json
```

Or write the report in Markdown (easier than editing ADF JSON) and convert:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py mybug.md -s "[OTP] เปลี่ยนภาษาแล้วเด้งกลับ" -p TP -t Bug > /tmp/wi.json
acli jira workitem create --from-json /tmp/wi.json
```

**Sections — required vs optional:**

| Section | When | Content (keep it concise) |
|---|---|---|
| สรุปปัญหา | always | 1–2 sentences: what broke / where / user impact |
| ขั้นตอน Reproduce | always | numbered actions, one step per line |
| ผลที่คาดหวัง | always | what should happen |
| ผลที่เกิดจริง | always | what happens + error/wrong state |
| ความรุนแรง | recommended | High/Medium/Low + one-line why |
| หลักฐาน | if available | env, account/order/id, screenshot/log |
| Technical Notes (dev) | if known | Root Cause / Fix / Files |

### Story — `story-template.json`

User-centric work item. Derived from Atlassian [user stories guidance](https://www.atlassian.com/agile/project-management/user-stories) ("As a [user], I want [goal], so that [benefit]" — non-technical, end-user perspective).

```bash
acli jira workitem create --from-json ${CLAUDE_SKILL_DIR}/examples/story-template.json
```

| Section | When | Content |
|---|---|---|
| User Story | always | "As a <role>, I want <goal> so that <benefit>" |
| Context | always | background / why — 1–2 sentences, non-technical |
| Acceptance Criteria | always | yes/no testable, one per line |
| Technical Notes | if known | approach, constraints (delete if not yet known) |
| Dependencies | if known | blockers or things that must be waited on |
| References | if any | plan / Figma / PR / link |

### Task — `task-template.json`

Implementation work. Derived from TP-466, 467, 473, 479.

```bash
acli jira workitem create --from-json ${CLAUDE_SKILL_DIR}/examples/task-template.json
```

| Section | When | Content |
|---|---|---|
| Context | always | why / goal, 1–2 sentences + plan link |
| Scope | always | files + what changes (line refs help) |
| Out of scope | recommended | what this task won't touch |
| Acceptance Criteria | always | yes/no testable, one per line |
| Tests | recommended | what to assert |
| References | if any | plan / Figma / PR links |

### Epic — `epic-template.json`

High-level initiative that spans multiple sprints. Derived from Atlassian agile guidance ("large body of work, broken into smaller stories, scope flexes with feedback").

```bash
acli jira workitem create --from-json ${CLAUDE_SKILL_DIR}/examples/epic-template.json
```

| Section | When | Content |
|---|---|---|
| Goal | always | business outcome / why this epic exists — 1–2 sentences |
| Scope | always | high-level what the epic covers (not file-level) |
| Out of scope | recommended | what the epic will not touch — prevents scope creep |
| Success Criteria | always | yes/no testable at epic level, one per line |
| Key Deliverables | always | milestones / shippable pieces (not a task list) |
| Dependencies & Risks | if known | blockers or things that must be waited on |
| Child Work Items | if known | task/story/sub-task breakdown (or delete if not yet planned) |
| References | if any | plan / PRD / Figma / link |

### Sub-task — `subtask-template.json`

A slice of a parent. **Must have a parent** — sub-tasks cannot be top-level. Derived from TP-436, 437, 489.

```bash
# parent set in the JSON via "parentIssueId", or pass --parent on the CLI
acli jira workitem create --from-json ${CLAUDE_SKILL_DIR}/examples/subtask-template.json
```

| Section | When | Content |
|---|---|---|
| Scope | always | one clear action + files |
| Out of scope | recommended | what siblings handle (avoid overlap) |
| Acceptance Criteria | always | yes/no testable, one per line |
| Files affected | if known | paths touched |

Sub-task parent: set `parentIssueId` in the JSON (or `--parent <KEY>` on the CLI). `parentIssueId` takes the issue **key** (e.g. `TP-479`) — verified by create+delete (sub-task created with `parent = TP-479`, no numeric id needed).

_Grounded in: real TP work items + Atlassian [bug-report template](https://www.atlassian.com/software/jira/templates/bug-report) / [user stories](https://www.atlassian.com/agile/project-management/user-stories) / [acceptance criteria](https://www.atlassian.com/work-management/project-management/acceptance-criteria) / [epics guidance](https://www.atlassian.com/agile/project-management/epics) + agile story/task/sub-task/epic breakdown best practices. Reconciled to one rule when sources disagreed: Given/When/Then, team-wide, per Head of Engineering._

### Acceptance Criteria — GOOD / BAD (Given/When/Then)

The one section worth a worked example. GOOD covers more than the happy path in plain nouns, one titled `กำหนดให้`/`เมื่อ`/`ผลลัพธ์` block per AC; BAD leaks tech terms, stops at the happy path, or skips the block structure.

**GOOD:**

**AC1 — หักยอดสำเร็จ (Happy path)**
* กำหนดให้: ลูกค้ามียอดคงเหลือ 500 บาท
* เมื่อ: ลูกค้ากดยืนยันการสั่งซื้อ 200 บาท
* ผลลัพธ์: ยอดถูกหัก เหลือ 300 บาท และเห็นข้อความสำเร็จ

**AC2 — ยอดไม่พอ (Error)**
* กำหนดให้: ลูกค้ามียอดคงเหลือไม่พอสำหรับรายการที่เลือก
* เมื่อ: ลูกค้ากดยืนยัน
* ผลลัพธ์: ระบบไม่หักยอด และแจ้งว่ายอดไม่พอ

**AC3 — ราคา 0 บาท (Boundary)**
* กำหนดให้: รายการราคา 0 บาท
* เมื่อ: ลูกค้ายืนยันการสั่งซื้อ
* ผลลัพธ์: ทำรายการสำเร็จ ถือว่า "ฟรี" ไม่ใช่ "ยังไม่ตั้งราคา"

**AC4 — ตรวจ Regression**
* กำหนดให้: ลูกค้าสั่งผ่านช่องทางนอกขอบเขตรอบนี้
* เมื่อ: ลูกค้าทำรายการตามปกติ
* ผลลัพธ์: ทำงานแบบเดิม ไม่ได้รับผลกระทบจากการเปลี่ยนแปลงรอบนี้

**BAD:**
- `order_status = PAID` ถูก set ใน `orders` table  ← field/enum/table names — PO/QA verify ไม่ได้
- เรียก `POST /api/v1/checkout` แล้วได้ `201`  ← API path + status code, ไม่ใช่สิ่งที่ผู้ใช้เห็น
- ลูกค้ามียอดคงเหลือพอ → กดยืนยัน → หักยอดสำเร็จ  ← บรรทัดเดียว ไม่แยก กำหนดให้/เมื่อ/ผลลัพธ์ เป็นบรรทัด — ไม่ตรง format มาตรฐานทีม
- (และมีแต่ happy path — ไม่มี error / boundary / regression)

## Comment templates (status update / QA verification / blocker / decision record)

⚠️ Unlike the five work-item templates above (each derived from real TP tickets), these four are a **starting proposal**, not mined from real usage or confirmed as a Head-of-Engineering standard — the AC format above was explicitly confirmed team-wide, this wasn't. Revise once used in practice.

Four templates for commenting on an *existing* ticket — not a new ticket's description, so no headings-and-sections overhead, just the purpose the comment serves. Same wording rules as above: Thai, plain, one idea per line, no vague language. Send any of these through the comment ADF pipeline (`SKILL.md` § Description format — `comment create` and `comment update` take ADF differently, don't assume they match):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py note.md > /tmp/note.json   # bare doc mode — no -s/-p/-t
acli jira workitem comment create --key KEY-1 --body-file /tmp/note.json
```

### สถานะความคืบหน้า (Status update)

```
## 📌 ความคืบหน้า

[สิ่งที่ทำไปแล้ว — พูดถึงสิ่งที่เกิดขึ้น ไม่ใช่ขั้นตอนภายในทีม]

**ขั้นตอนถัดไป:** [สิ่งที่จะทำต่อ]
**คาดว่าจะเสร็จ:** [วันที่ ถ้าทราบ — ไม่ทราบให้เว้นว่าง อย่าเดา]
```

### ผลตรวจ QA (QA verification)

Reference the same `AC#` numbering as the ticket's own Acceptance Criteria (GWT format, see above) — a QA comment should trace back to the exact AC it verifies, not read as a free-form retest summary.

```
## 🧪 ผลตรวจ QA

* AC1 — [ชื่อ AC]: ✅ ผ่าน / ❌ ไม่ผ่าน — [หมายเหตุถ้าไม่ผ่าน]
* AC2 — [ชื่อ AC]: ✅ ผ่าน / ❌ ไม่ผ่าน — [หมายเหตุถ้าไม่ผ่าน]

**สรุป:** [ผ่านทั้งหมด พร้อมปิดงาน / ไม่ผ่าน ต้องแก้เพิ่ม]
```

### คำถาม/ติดขัด (Blocker / question)

```
## ⚠️ คำถาม/ติดขัด

[สิ่งที่ติดขัด หรือคำถามที่ต้องการคำตอบ — ระบุให้ชัดว่าใครต้องตอบ]

**ผลกระทบถ้าไม่ได้คำตอบ:** [เช่น งานหยุด / เดดไลน์เลื่อน]
```

### บันทึกการตัดสินใจ (Decision record)

```
## 📋 บันทึกการตัดสินใจ

**ประเด็น:** [สิ่งที่ต้องตัดสินใจ]
**ตัดสินใจ:** [ผลการตัดสินใจ]
**เหตุผล:** [ทำไมถึงตัดสินใจแบบนี้]
**ผู้ตัดสินใจ:** [ชื่อ/บทบาท ถ้าทราบ]
```

---

## 1. Jira description via `--from-json`

`description` must be a full ADF document object — a bare string does not match the schema.

**GOOD** (`workitem-from-json.good.json`):
```json
"description": { "type": "doc", "version": 1,
  "content": [ { "type": "paragraph",
    "content": [ { "type": "text", "text": "Repro steps: ..." } ] } ] }
```

**BAD** (`workitem-from-json.bad.json`):
```json
"description": "Repro steps: ..."
```
Why: the generated schema (`acli jira workitem create --generate-json`) emits `description` as an ADF `{type:"doc",...}` object. A plain string is not ADF, so it won't be accepted/rendered as intended.

---

## 2. Jira description via flag — plain text is fine

The flag path wraps plain text into ADF for you. Do **not** hand-write ADF JSON on the command line.

**GOOD:**
```bash
acli jira workitem create -p TEAM -t Task -s "Login bug" \
  --description "Users hit a 500 on submit. Repro: POST /login with empty body."
```

**BAD:**
```bash
acli jira workitem create -p TEAM -t Task -s "Login bug" \
  --description '{"type":"doc","version":1,"content":[...]}'
```
Why: the flag already accepts plain text and wraps it. Pasting raw ADF JSON as a flag value is redundant and error-prone (shell quoting, escaping). Reserve ADF objects for `--from-json`.

---

## 3. Don't mix Jira ADF with Confluence storage format

**BAD — Confluence XHTML in a Jira description:**
```bash
acli jira workitem create -p TEAM -t Task -s "X" --description "<p>Hello</p>"
```
Why: `<p>...</p>` is Confluence **storage format**, not Jira ADF. In Jira the tags show as literal text — Jira does not parse XHTML.

**BAD — Markdown expecting render:**
```bash
acli jira workitem create -p TEAM -t Task -s "X" --description "See **the docs**"
```
Why: ADF `text` nodes are literal. `**the docs**` renders as the literal asterisks, not bold. Use the flag's plain text for plain text; build an ADF object with marks if you need bold/links.

---

## 4. Confluence body — storage XHTML, not ADF

**GOOD:**
```bash
acli confluence blog create --space-id 12345 --title "Release Notes" \
  --body "<p>Shipped <strong>v2</strong>. <a href=\"https://x\">Changelog</a>.</p>"
```

**BAD — ADF JSON into Confluence:**
```bash
acli confluence blog create --space-id 12345 --title "X" \
  --body '{"type":"doc","version":1,...}'
```
Why: Confluence expects storage format (XHTML), the inverse of Jira. ADF here renders as literal JSON text.

---

## Quick rule

| You're writing... | Use |
|---|---|
| Jira, via flag | plain text (auto-wrapped to ADF) |
| Jira, via `--from-json` | ADF `{type:"doc",version:1,content:[...]}` object |
| Confluence body | storage format XHTML (`<p>`, `<strong>`, `<a>`) |

Regenerate the canonical schema any time with `acli jira workitem create --generate-json`.
