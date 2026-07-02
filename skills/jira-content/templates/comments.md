# Comment templates (status update / QA verification / blocker / decision record)

⚠️ Unlike the work-item templates (each derived from real TP tickets), these four are a
**starting proposal**, not mined from real usage or confirmed as a Head-of-Engineering standard —
the [Acceptance Criteria format](acceptance-criteria.md) was explicitly confirmed team-wide, this
wasn't. Revise once used in practice.

Four templates for commenting on an *existing* ticket — not a new ticket's description, so no
headings-and-sections overhead, just the purpose the comment serves. Same wording rules as the
work-item templates: Thai, plain, one idea per line, no vague language.

A **trivial one-line comment** doesn't need a template — just call `acli jira workitem comment
create --key KEY-1 --body "..."` directly (see `jira-acli:acli`). These four are for a comment
that has real structure to it.

Send any of these through the comment ADF pipeline — `comment create` and `comment update` take
ADF differently, don't assume they match (see `jira-acli:acli` § Description format):

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" note.md > /tmp/note.json   # bare doc mode — no -s/-p/-t
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

Reference the same `AC#` numbering as the ticket's own [Acceptance Criteria](acceptance-criteria.md)
— a QA comment should trace back to the exact AC it verifies, not read as a free-form retest
summary.

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
