# Known Issues — acli skill

## Issue 1: md2adf.py ไม่ handle nested lists ถูกต้อง

**Severity:** By design (documented limitation)  
**Impact:** Description ใน Jira ที่มี nested list (bullet list ข้างใน ordered list) จะถูก flatten เป็น sibling lists แทนที่จะเป็น child lists  
**Affected files:**
- `skills/acli/scripts/md2adf.py`
- ทุก workflow ที่ใช้ `md2adf.py` → `acli jira workitem edit/create --from-json`

**Symptom:**
Markdown input:
```md
1. First item
   - Sub A
   - Sub B
2. Second item
```

Expected ADF: `orderedList > listItem > bulletList`  
Actual ADF: `orderedList` และ `bulletList` เป็น sibling (`listItem` ไม่มี `bulletList` เป็น child)

**Workaround (by design):**
ใช้ H3 sub-heading + flat bullets แทน nested list (ตามที่ `md2adf.py` docstring + acli REFERENCE แนะนำ) การ flatten เป็นพฤติกรรมที่ตั้งใจ ไม่ใช่ bug ที่ต้องแก้

---

## Issue 2: `acli jira workitem edit --from-json` ไม่สามารถใช้คู่กับ `--key` ได้

**Severity:** Low  
**Impact:** CLI error เมื่อพยายามใช้ `--key` ร่วมกับ `--from-json`  
**Error message:**
```
if any flags in the group [key jql filter generate-json from-json] are set none of the others can be; [from-json key] were all set
```

**Workaround:**
ใช้ `issues` array ภายใน JSON แทน:
```json
{
  "issues": ["TP-643"],
  "description": { ... }
}
```

แล้วเรียก:
```bash
acli jira workitem edit --from-json file.json --yes
```

ไม่ต้องใช้ `--key`

---

## Issue 3: `acli jira workitem view --json` แสดง `labels` เป็น `null` เสมอ แม้ set ไว้จริง

**Severity:** Low (misleading output, ไม่ใช่ data loss)
**Impact:** ตรวจ labels ผ่าน `acli jira workitem view KEY --json | jq .fields.labels` ได้ `null` เสมอ แม้ issue จะมี labels จริงตาม Jira (ยืนยันด้วย MCP `getJiraIssue` และหน้าเว็บ) — ทำให้เข้าใจผิดว่าการ set label ล้มเหลว ทั้งที่จริง ๆ สำเร็จแล้ว
**Affected commands:**
- `acli jira workitem view --json` — field `labels` ผิด
- ไม่กระทบ `acli jira workitem edit --labels` เอง (edit สำเร็จจริง แค่ view หลังจากนั้นแสดงผลผิด)

**Symptom:** (พบระหว่างแก้ TP-806/TP-809, 2026-07-06)
```bash
acli jira workitem edit --key TP-809 --labels "ready-for-agent" --yes   # ✓ success
acli jira workitem view TP-809 --json | jq .fields.labels                # → null  (ผิด)
```
Cross-check ด้วย MCP:
```
mcp__plugin_atlassian_atlassian__getJiraIssue → fields.labels: ["ready-for-agent"]   # ถูกต้อง
```

**หมายเหตุ (ไม่ฟันธง):** ยังไม่ยืนยันว่า `--label` ตอน `create` ล้มเหลวจริงหรือเปล่า — เช็ค changelog ของ TP-809 แล้วไม่มี entry ของ field `labels` เลย (Jira ไม่บันทึกค่าตอน create ลง changelog) เป็นไปได้สูงว่า label ติดมาตั้งแต่ create ปกติ และ `edit --labels` ที่ทำเพิ่มทีหลังเป็นแค่ no-op ประเด็นที่ยืนยันแน่นอนมีแค่อย่างเดียว: `view --json` เชื่อไม่ได้สำหรับ field นี้ ไม่ว่าจะ set มาจากตอนไหนก็ตาม

**Workaround:** อย่าเชื่อ `labels` field จาก `acli ... view --json` เพียงอย่างเดียว — cross-check ด้วย Atlassian MCP `getJiraIssue` หรือเปิดหน้าเว็บ ก่อนสรุปว่า label ไม่ถูก set

---

## Reported
- **Date:** 2026-06-15
- **Reporter:** wasikarn / Claude Code session
- **Context:** ปัญหาพบขณะ update Jira ticket TP-643 description ด้วย acli skill
