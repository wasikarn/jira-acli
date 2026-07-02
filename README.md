# jira-acli

An acli-first Jira/Confluence toolkit for Claude Code: bulk work-item ops via JQL,
ADF↔markdown conversion, and template-conforming content authoring for both Jira
issues and Confluence pages.

Extracted from [kbg-harness](https://github.com/wasikarn/kbg-harness) — it started as
skills inside a general engineering harness and moved out here to stand on its own.

## Skills

- **`acli`** — the mechanical backend for all Jira/Confluence work: search, view, edit,
  transition, comment, link, clone, bulk ops, Confluence page/space ops, org admin,
  ADF↔markdown conversion. Owns no content standard — a tool, same role as the
  Atlassian MCP.
- **`jira-content`** — creates or edits the *content* of a Jira Bug/Story/Task/Epic/
  Sub-task or a templated comment, against the team's canonical templates (Thai
  PO/QA-readable, GWT Acceptance Criteria), with a preview-and-confirm gate before any
  write. Calls into `acli`'s scripts to execute.
- **`confluence-content`** — the Confluence counterpart: creates or edits a Spec/PRD
  page's content against its own template. MCP-only (acli's `confluence page` command
  is view-only).

`jira-content` and `confluence-content` share one Acceptance Criteria rule
(`templates/acceptance-criteria.md`, at the plugin root) so the format can't drift
between the two products. All three skills ship together and are not separable.

## Prerequisites

This plugin is **not self-contained**. It needs, installed separately:

1. **The [`acli` CLI](https://developer.atlassian.com/cloud/acli/)** — installed and
   authenticated (`acli jira auth login` / `acli confluence auth login`). This is the
   primary backend for `acli` and `jira-content`.
2. **The official Atlassian plugin** (provides the `mcp__plugin_atlassian_atlassian__*`
   MCP tools) — used as a fallback for the handful of things `acli` genuinely can't do
   yet (see `skills/acli/SKILL.md` § "When acli can't"), by `jira-content` when `acli`
   is unavailable or can't set a required field, and as the **only** backend for
   `confluence-content` (Confluence page create/update has no acli path).

No skill ships its own `.mcp.json` — bundling one for a fallback path would mean
duplicating credentials and rewriting every MCP tool literal for no functional gain.

## Install

```
/plugin marketplace add wasikarn/jira-acli
/plugin install jira-acli@wasikarn
```

Ships `defaultEnabled: false` — add `"jira-acli@wasikarn": true` to your Claude Code
`settings.json` after install, then restart.

## Versioning

Bump `version` in **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
on every release — same-version edits to a cached plugin are silent no-ops.
