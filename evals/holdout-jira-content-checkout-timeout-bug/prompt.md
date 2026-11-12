---
name: holdout-jira-content-checkout-timeout-bug
tags: [holdout, jira-content]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---
Use the `jira-acli:jira-content` skill (Skill tool, `skill: "jira-acli:jira-content"`) to draft a Jira Bug ticket for the payment team about the checkout failures described in `slack-thread.txt` and `error-log.txt`. Write the ticket in Thai, keeping technical terms, codes, versions and names of systems in English. All facts are in the files in the working directory. Nobody will answer questions, so do not ask any. Anything the files do not say is marked unknown in the draft, never invented. Write the draft to `ticket.md`; it is the only file you create. Do not create, publish or update anything in Jira or Confluence, and do not run acli or any Jira or Confluence tool.

Your final message is one line naming the file, nothing else.

If the Skill tool reports the skill as unknown or unavailable, do the same task yourself and still end with the final message described above.
