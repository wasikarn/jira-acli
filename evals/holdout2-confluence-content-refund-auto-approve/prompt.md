---
name: holdout2-confluence-content-refund-auto-approve
tags: [holdout2, confluence-content]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
Use the `jira-acli:confluence-content` skill (Skill tool, `skill: "jira-acli:confluence-content"`) to draft the Confluence spec page for our refund auto-approve feature in the shop backoffice. The source material is in this directory: the team chat export, the meeting notes and an older draft. Everything you need is in those files and nobody is available to answer questions, so do not ask any. If the files do not say something, mark it as unknown in the page; do not invent it.

Write the page in Thai, with English technical terms (endpoint, flag, error code and so on) left in English, to `spec.md`. That is the only file to create; do not edit the source files. Do not create, publish or update anything in Jira or Confluence, and do not run `acli` or any Jira or Confluence tool.

Your final message is one line naming the file you wrote, nothing else.

If the Skill tool reports the skill as unknown or unavailable, do the same task yourself and still end with the final message described above.
