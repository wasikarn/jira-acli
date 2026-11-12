#!/usr/bin/env bash
# Harness canary, not a verdict case: one fact (CANARY-7731) the draft must carry.
cat > notes.txt <<'NOTES'
Team note: add a health-check endpoint /healthz to the billing service. Tracking code CANARY-7731.
Owner unknown. No deadline set.
NOTES
