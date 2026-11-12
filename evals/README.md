# Evals

Blind A/B cases for `jira-content` and `confluence-content`, run with `claude plugin eval`. The operator's rule: a
skill stays a skill only if it beats plain Claude on held-out cases written by an agent that never saw it (numbers
below; source: the operator's global `CLAUDE.md` and `wasikarn/siang` `evals/README.md`). `acli` has no cases: it
drives a live site, and there is none while acli is logged out.

## Running

```bash
bash evals/mkcopy.sh <copy>/jira-acli   # see "Harness notes": the with-arm needs defaultEnabled true
claude plugin eval <copy>/jira-acli --tag holdout --allow-tools "Bash,Edit,Write" --runs 5 --scaffold \
  --trust-plugin --no-publish --max-cost-usd 40 --threshold 0 --output-dir <out> --json <out>/result.json
```

Each run is a paid API call. Bash runs in Claude Code's OS sandbox (home unreadable, so acli has no credentials),
and personal MCP servers never load in a run.

## Harness notes

- `.claude-plugin/plugin.json` sets `defaultEnabled: false`, and `claude plugin eval` then runs the with-arm
  without the plugin (it warns: "nothing in the eval sandbox enables it"). Runs use a scratch copy made with
  `git archive HEAD` with `defaultEnabled` set to `true`; the skill text is the commit's.
- Without `--allow-tools "Bash,Edit,Write"` no run can write its draft, and both arms score near 0.
- A `tool_used: Skill` grader passes on any Skill call, even one that returns "unknown skill". The canary cases
  (`canary-*`, tag `canary`, not part of any verdict) check the run itself: the Skill call loads the skill
  (the trace shows `Launching skill: jira-acli:...` and the `SKILL.md` text), a Bash call works with the plugin's
  `acli-guard` hook loaded, and file graders read the scaffolded files. 2026-11-12, plugin 0.1.51,
  `claude-opus-5-5`, CLI 2.1.322: both arms 1.00 on both canaries, $0.65.

## Held-out round 1 (2026-11-12, before the run, graders frozen at `d6042016da1909d6`)

**Writer.** A fresh agent wrote the four `holdout-*` cases in a scratch directory. It was told not to read anything
in this repo, any jira-acli path under `~/.claude`, any memory store, or `wasikarn/siang` beyond one case directory
used for format. It reported what it already knew: this repo's `CLAUDE.md` and memory index were injected into
its context, so it knew the template list, that `confluence-content` has a Mermaid script, and that both skills
share an acceptance-criteria rule. It says it used none of that, and no grader requires a heading, template,
table or acceptance criteria. It reported no slip. I (the orchestrator, who has read the skills) changed no case
file; I only checked them.

**Cases.** Each case gives source material (chat export, logs, meeting notes, an older draft) and asks for one
draft file, with no questions asked and nothing published.

| case | language | output | traps planted |
|---|---|---|---|
| `holdout-jira-content-checkout-timeout-bug` | Thai | Bug, `ticket.md` | 12% corrected to 3.4%; Redis ruled out; iOS unknown; customer name and phone internal |
| `holdout-jira-content-export-decision-record` | English | decision-record comment on RPT-412, `comment.md` | 24h corrected to 72h; 120s timeout and pagination rejected; `EXPORT_MAX_ROWS` unknown; merchant name internal |
| `holdout-confluence-content-points-expiry` | Thai | spec/PRD page, `spec.md` | 24 months corrected to 12; SMS cut; job run time unknown; SMS budget internal |
| `holdout-confluence-content-partner-rate-limit` | English | spec/PRD page, `spec.md` | 1000/min corrected to 600; per-IP keying rejected; burst size unknown; partner blame internal |

**Graders.** Nine `outcome-*` regex graders per case, on tokens that survive translation (keys, numbers, paths,
flags, ISO dates), plus `process-skill-fired`, which is with-only and unscored. Each regex grader carries at least
two `must-pass` and one `must-fail` lines; all 36 pass a node `RegExp` self-test. Hash: first 16 hex of
`find evals/holdout-* -type f | sort | xargs shasum -a 256 | shasum -a 256`, from the repo root.

**Rule, fixed before the run.** 5 runs per arm, spend capped at $40. Each skill stays a skill if, over its two
cases, the with-skill mean is above 0.90 and no case loses to the no-skill arm by more than 0.05. A skill that fails
becomes a plain doc (templates kept), with no tuning and no rerun on these cases; the move waits for the operator.
Cost and turns per run are reported, not gated. Editing any `holdout-*` file or the skill text after the run
starts voids it.

**What a pass can show.** The graders are blind, so they cannot see the skills' own contract (the team's Thai
PO/QA structure, Given/When/Then acceptance criteria). They check facts kept, corrections applied, rejected options
not stated as the plan, unknowns not invented, and internal remarks left out. A pass means the skill does no harm
there, not that the template helps.

**Known loose graders, left frozen.**
- `outcome-burst-unknown` (partner-rate-limit) fails on any digit within 30 characters after "burst" other than
  600 or a year, so a correct line like "bursts ... p99 8.2s" or "bursts get 429" fails it.
- Trap graders that allow a rejected option only with a rejection word on the same or next line (the writer's
  own flag) fail a correct draft that explains the rejection further away.

When a case misses, read the draft before trusting the grader.

### Result (2026-11-12, plugin 0.1.51, graders frozen at `d6042016da1909d6`, commit 4583826)

5 runs per arm, $10.68, 381 s, no run errors, `claude-opus-5-5`, CLI 2.1.322. The skill fired in 20 of 20
with-arm runs. Full result: `results/2026-11-12-round1.json`.

| case | with / without / Δ | cost per run with / without | turns with / without |
|---|---|---|---|
| `holdout-jira-content-checkout-timeout-bug` | 0.911 / 0.822 / +0.089 | $0.377 / $0.197 | 7.4 / 4.0 |
| `holdout-jira-content-export-decision-record` | 1.000 / 1.000 / 0.000 | $0.230 / $0.125 | 5.6 / 4.4 |
| `holdout-confluence-content-partner-rate-limit` | 0.867 / 0.933 / −0.067 | $0.340 / $0.170 | 6.0 / 4.4 |
| `holdout-confluence-content-points-expiry` | 0.822 / 0.844 / −0.022 | $0.492 / $0.205 | 6.4 / 4.0 |

**By the frozen rule:** `jira-content` passes (with-skill mean 0.956, worst Δ 0.000). `confluence-content` fails
(mean 0.844, and partner-rate-limit loses by 0.067).

**Reading the drafts.** All 36 scored misses (18 per arm) are false fails. Every flagged draft was correct:
- the superseded value or rejected option appears only labelled as old, in a history table, a sources line or a
  before/after table (`no-per-ip-key`, `no-1000-limit`, `no-24-months`, `no-superseded-rate`);
- SMS appears under "Out of scope" (`no-sms-channel`);
- iOS appears under an "unknown" heading, or in an acceptance criterion to check it, with the word "unknown" on
  another line (`ios-unknown`);
- "burst behaviour (R1" trips the digit rule (`burst-unknown`).

The with-skill pages are longer (150 to 180 lines against about 90) and carry more history and source sections, so
they trip these graders more. Read this way, neither arm made a real error on any trap: both are at 1.00, and the
skills show neither gain nor harm on these checks, at 1.7x to 2.4x the cost per run. `jira-content`'s +0.089 is
grader noise too: the no-skill arm tripped `no-superseded-rate` three times with a correct "12% was the wrong number" note.

**Decision pending (operator).** The rule says `confluence-content` becomes a plain doc. The failure comes from the
loose graders named above before the run, not from a wrong page. A fresh blind pair whose trap graders accept a
labelled superseded value would settle it. No grader or skill was edited after the run.
