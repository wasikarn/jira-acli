# Acceptance Criteria: the team-wide standard (single source)

This is the only place the AC rule is defined. Every template, skill and reference in this
plugin points here instead of restating it. Restating it is how the old GWT rollout drifted:
the JSON templates went stale a full turn after the Markdown ones were fixed. If you are
tempted to copy this text elsewhere, add a pointer instead.

Team-wide standard, confirmed by the Head of Engineering. Use it for every AC, including AC for
simple behavior.

## Format: Given/When/Then

One titled block per AC:

```
**AC# — <short title>**
* กำหนดให้: <precondition>
* เมื่อ: <action>
* ผลลัพธ์: <expected outcome>
```

Put `กำหนดให้`, `เมื่อ` and `ผลลัพธ์` each on its own bullet line. Do not collapse them into one
line or leave a bare description sentence.

## Register: plain business language, no tech leaks

Each AC must read for a PO/QA with no engineering background and be yes/no testable (Specific,
Testable, Clear).

- Use plain business nouns (ยอดคงเหลือ, วันหมดอายุ, ช่องทางการขาย), baht and day counts (500 บาท,
  หมดอายุ 30 วัน), and outcomes the user sees.
- Avoid field/column names (`order_status`, `entity_type`), enum values (`TYPE_A`), API paths
  (`GET /admin/x/:id`) and DB references (`INSERT INTO`, foreign keys), and never describe what the
  DB stores.
- No vague language: say what fails and when, not "ใช้ไม่ได้".

## Coverage: past the happy path

Each of these is still its own AC block, not folded into the happy-path AC:

- Error or empty case: the thing that goes wrong.
- Permission/auth: who should not be able to do this.
- Boundary value that looks empty but is real (ราคา 0 บาท = "ฟรี", ไม่ใช่ "ยังไม่ตั้งราคา").
- Regression check: for any "ไม่อยู่ในขอบเขตรอบนี้" item on the same flow, an AC asserting
  old behavior is unchanged.

A Story also needs:
- Per-surface AC for each screen or channel the change is visible on.
- Fallback AC for existing data without the new information.

## Minimums

- Bug = 2: fix verification and regression check.
- Story = 3: happy path, error or edge case, and regression or permission.

## GOOD / BAD worked example

GOOD covers more than the happy path in plain nouns, one titled `กำหนดให้`/`เมื่อ`/`ผลลัพธ์`
block per AC; BAD leaks tech terms, stops at the happy path, or skips the block structure.

GOOD:

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

BAD: field/enum/API names; no `กำหนดให้`/`เมื่อ`/`ผลลัพธ์` split; or only the happy path.
