---
type: regex
pattern: 'members/[^\s/]+/points/expiring'
match: contains
target: {source: file, path: spec.md}
# must-pass: BE ทำ endpoint ใหม่ GET /v1/members/{memberId}/points/expiring
# must-pass: `GET /v1/members/:memberId/points/expiring` คืนจำนวนแต้มและวันหมดอายุ
# must-fail: app เรียก API เพื่อดึงแต้มที่ใกล้หมดอายุ แล้ว deep link ไปหน้า /points/expiring
---
The page names the new backend endpoint (not just the app deep link).
