---
name: trigger-jira-content-decision-en
tags: [trigger, jira-content]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
Can you write up what we decided on RPT-412 as a comment for the ticket? Everything is in `issue.txt`, `meeting-notes.md` and `followup-thread.txt`. Put it in `comment.md` for now, I'll post it myself, so don't post anything to Jira. Don't ask me questions, just mark anything the files don't say as unknown.

Reply with one line naming the file.
