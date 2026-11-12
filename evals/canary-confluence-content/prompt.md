---
name: canary-confluence-content
tags: [canary]
runs: 1
max_turns: 20
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
First run `echo canary-bash-ok > bash-ok.txt` with the Bash tool. Then use the `jira-acli:confluence-content` skill (Skill tool, `skill: "jira-acli:confluence-content"`) to draft a short Confluence spec page from `notes.txt`, in English. All facts are in `notes.txt`; nobody will answer questions, so do not ask, and mark anything it does not say as unknown. Write the draft to `draft.md`. Do not create, publish or update anything in Jira or Confluence, and do not run acli or any Jira/Confluence tool.

Your final message is one line naming the file you wrote.

If the Skill tool reports the skill as unknown or unavailable, do the same task yourself and still end with the final message described above.
