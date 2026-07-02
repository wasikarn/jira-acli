#!/usr/bin/env bash
set -euo pipefail
# Per-skill wrapper for acli's whole-description replace script.
# Resolves the plugin root from this file's own path so the skill body only
# needs: bash "${CLAUDE_SKILL_DIR}/scripts/acli-set-desc.sh" KEY desc.md
__src="${BASH_SOURCE[0]:-$0}"
__dir="$(cd "$(dirname "$__src")" && pwd)"
__root="$(cd "${__dir}/../../.." && pwd)"
exec bash "${__root}/skills/acli/scripts/acli-set-desc.sh" "$@"
