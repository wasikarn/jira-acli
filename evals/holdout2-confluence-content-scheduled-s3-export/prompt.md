---
name: holdout2-confluence-content-scheduled-s3-export
tags: [holdout2, confluence-content]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
Use the `jira-acli:confluence-content` skill (Skill tool, `skill: "jira-acli:confluence-content"`) to draft the Confluence PRD page for scheduled data exports to customer S3 buckets. The files in this directory hold all the facts: a Slack thread export, the design review notes, an error log from the prototype and the PM's first draft. No one can answer questions, so do not ask. Anything the files leave open is marked unknown in the page, never filled in by guessing.

Write the page in English to `prd.md`; that is the only file to create, and the source files stay unchanged. Do not create, publish or update anything in Jira or Confluence, and do not run `acli` or any Jira or Confluence tool.

Your final message is one line naming the file you wrote, nothing else.

If the Skill tool reports the skill as unknown or unavailable, do the same task yourself and still end with the final message described above.
