---
type: regex
pattern: 'orders/[^\s/]+/checkout'
match: contains
target: {source: file, path: ticket.md}
# must-pass: Endpoint: `POST /api/v2/orders/{orderId}/checkout`
# must-pass: เรียก POST /api/v2/orders/ORD-88412093/checkout แล้วได้ 504
# must-fail: หน้า checkout ค้างแล้วขึ้น error
---
The ticket names the failing endpoint.
