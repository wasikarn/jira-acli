---
name: holdout-confluence-content-points-expiry
tags: [holdout, confluence-content]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
Use the `jira-acli:confluence-content` skill (Skill tool, `skill: "jira-acli:confluence-content"`) to draft a Confluence spec/PRD page for the points-expiry notification feature, from `older-draft.md`, `meeting-notes-2026-11-05.md` and `line-chat.txt`. The page is shared with the mobile, backend and vendor teams. Write it in Thai, keeping technical terms, endpoint and flag names in English. All facts are in the files in the working directory. Nobody will answer questions, so do not ask any. Anything the files do not say is marked unknown in the draft, never invented. Write the draft to `spec.md`; it is the only file you create. Do not create, publish or update anything in Jira or Confluence, and do not run acli or any Jira or Confluence tool.

Your final message is one line naming the file, nothing else.

If the Skill tool reports the skill as unknown or unavailable, do the same task yourself and still end with the final message described above.
