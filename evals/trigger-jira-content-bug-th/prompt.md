---
name: trigger-jira-content-bug-th
tags: [trigger, jira-content]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
ช่วยร่าง bug ให้ทีม payment หน่อย จาก `slack-thread.txt` กับ `error-log.txt` เขียนลง `ticket.md` ไว้ก่อน ยังไม่ต้องสร้างใน Jira เดี๋ยวผมเปิดเอง ข้อมูลมีแค่ในไฟล์ ไม่ต้องถามกลับนะ อะไรที่ไฟล์ไม่ได้บอกให้เขียนว่าไม่ทราบ

เสร็จแล้วตอบบรรทัดเดียวว่าเขียนไฟล์ไหน
