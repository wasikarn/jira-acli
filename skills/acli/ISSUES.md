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

## Issue 4: `acli jira workitem create --description-file`/`--description` เรียกตรงห่อ plain text เป็น ADF paragraph เดียว ไม่มี template

**Severity:** High (root cause คือไม่รู้ว่า `jira-acli` มีอยู่ ไม่ใช่ bug ของ acli เอง)
**Impact:** เรียก `acli jira workitem create --description-file`/`--description` ตรง ๆ โดยไม่ผ่าน `jira-acli:jira-content` จะห่อ plain text เป็น ADF `paragraph` node เดียว (ไม่มี heading/list ตาม template) และ create ไม่มี `--priority` flag ให้ตั้งเลย
**Affected commands:**
- `acli jira workitem create --description-file <file>` / `--description <text>` เรียกตรงจากภายนอก `jira-acli:jira-content`

**Symptom:** (พบตอนสร้าง TP-809/TP-806, 2026-07-06 — เรียกจากภายใน `kbg:to-prd` ซึ่งไม่รู้ว่า `jira-acli` มีอยู่)
- description flatten เป็น ADF `paragraph` node เดียว (ยืนยันจากอ่าน raw ADF)
- template shape ผิด (PRD shape ทั่วไป แทนที่จะเป็น canonical Bug/Task template)
- priority ค้างที่ default ของ Jira — ต้องแก้ด้วยมือทีหลัง
- labels ตรวจแล้วถูกต้องจริง — สิ่งที่ดูเหมือนผิดตอนแรกคือ Issue 3 ข้างบน (`view --json` misreport) ไม่ใช่ความเสียหายจากเคสนี้

ต้อง reformat + re-verify ทั้ง 2 ticket ทีหลัง

**Workaround / Prevention:** ห้ามเรียก `acli jira workitem create --description-file`/`--description` ตรง ๆ จากที่ไหนก็ตาม รวมถึงจาก skill อื่นที่บอกให้ "publish to tracker/backlog" — ต้องผ่าน `jira-acli:jira-content` เสมอเพื่อ reshape เป็น canonical template ก่อน (routing rule แบบเต็มอยู่ที่ root `~/.claude/CLAUDE.md` § "Atlassian / Jira & Confluence Work")

---

## Issue 5: `md2adf.py` ไม่ handle markdown table syntax — flatten เป็น plain text แทน real ADF table

**Severity:** High (silent structural data loss บน full-body description replace, ไม่ใช่แค่ misleading display แบบ Issue 1/3)
**Impact:** `md2adf.py` ไม่ parse markdown table (`| a | b |` + `| --- | --- |`) เป็น ADF `table`/`tableRow`/`tableCell`/`tableHeader` nodes เลย — แปลงเป็น `paragraph` ธรรมดาที่มี literal `|` characters แทน ถ้า description เดิมมี real ADF table (จาก UI หรือ process อื่น) แล้วรัน `acli-set-desc.sh`/`acli jira workitem edit --from-json` แบบ full-body replace ด้วย markdown ที่เขียน table ใหม่ ตาราง**ทั้งหมดจะหายและกลายเป็น text พังบน Jira**
**Affected files:**
- `skills/acli/scripts/md2adf.py`
- ทุก workflow ที่ full-body replace ผ่าน `acli-set-desc.sh` / `md2adf.py desc.md > wi.json && acli jira workitem edit --from-json`

**Symptom:** (พบระหว่างแก้ TP-820 sub-task ของ TP-807, 2026-07-14 — จับได้ก่อนเขียนจริง ไม่ใช่หลัง)
Markdown input:
```md
| Param | Type | Default |
| --- | --- | --- |
| `cameraId` | string | — |
```
Expected ADF: `table > tableRow > tableHeader/tableCell`
Actual ADF (ยืนยันด้วยการนับ node type จริงจาก `md2adf.py` output): **0 `table` nodes** — ทุกแถวถูกรวมเป็น `paragraph` เดียวที่มี text `"| Param | Type | Default | | --- | --- | --- | | `cameraId` | string | — |"`

Cross-check กับ ticket จริงที่มีอยู่แล้ว (TP-820, 8 tables): `acli jira workitem view --json` แสดง 8 `table` nodes ถูกต้อง — พิสูจน์ว่า Jira/ADF รองรับ table เต็มรูปแบบ ปัญหาอยู่ที่ `md2adf.py` parser ฝั่งเดียว ไม่ใช่ Jira API

**Workaround (Prevention — ต้องเช็คก่อนเขียนเสมอ):**
ก่อนรัน full-body replace (`acli-set-desc.sh` หรือ `md2adf.py` + `edit --from-json`) บน ticket ที่มีอยู่แล้ว **ต้องเช็คก่อนว่า description เดิมมี table หรือไม่**:
```bash
acli jira workitem view KEY --json | python3 -c "
import json,sys
d = json.load(sys.stdin)
def count_tables(n):
    if not isinstance(n, dict): return 0
    c = 1 if n.get('type') == 'table' else 0
    return c + sum(count_tables(x) for x in n.get('content', []))
print('table count:', count_tables(d['fields']['description'] or {}))
"
```
ถ้า count > 0: **ห้าม** full-body replace ผ่าน `md2adf.py` เด็ดขาด — จะทำลาย table ทั้งหมด ทางเลือกตอนนี้: (a) แก้เฉพาะส่วนที่ไม่มี table ผ่าน `acli-edit.sh --replace-section` โดยเลือก section ที่ไม่มี table อยู่ในขอบเขต, หรือ (b) ปล่อย body ไว้ไม่แตะ (ตามที่ทำกับ TP-820 จริง — แก้แค่ `summary` field ซึ่งเป็น plain string ไม่ใช่ ADF เลยไม่เจอปัญหานี้), หรือ (c) hand-build ADF ที่ preserve table node เดิมแล้ว inject ผ่าน MCP `editJiraIssue` แทน (ยังไม่ verify แนวทางนี้จริง) `md2adf.py` เองยังไม่รองรับ table syntax เลย — **การขยาย parser ให้ handle table เป็นงานที่ยังไม่ทำ**, ไม่ใช่แค่ workaround ที่พอใช้ได้

---

## Reported
- **Date:** 2026-06-15
- **Reporter:** wasikarn / Claude Code session
- **Context:** ปัญหาพบขณะ update Jira ticket TP-643 description ด้วย acli skill
