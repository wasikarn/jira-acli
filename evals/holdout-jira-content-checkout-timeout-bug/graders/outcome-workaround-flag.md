---
type: regex
pattern: 'checkout\.async_capture'
match: contains
target: {source: file, path: ticket.md}
# must-pass: Workaround: ปิด flag checkout.async_capture แล้ว error หาย
# must-pass: Disabled `checkout.async_capture` as a workaround
# must-fail: Workaround: ปิด feature flag ชั่วคราว
---
The workaround names the flag that was turned off.
