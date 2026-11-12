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

**Operator, 2026-11-13:** run round 2 below. A later review also noted that blind graders cannot see the template,
which is the reason both skills exist, so round 2 adds a separate trigger and template check.

## Round 2 (2026-11-13, before the run)

Two parts, both fixed before either runs. Plugin 0.1.51; skill text as in round 1.

### Part A: fresh blind pair for `confluence-content` (graders frozen at `21ecf8b671503290`)

**Writer.** A fresh agent with round 1's do-not-read list and a brief that adds one rule. A superseded value, a
rejected option or an unanswered question may appear anywhere in a good page when the page labels it as old,
rejected, out of scope or unknown: in a history or before/after table, a sources list, an out-of-scope list, or a
sentence away from the label. A trap grader fails only a statement of it as the current fact or the plan. No rule
may depend on distance to a digit or a label. Internal-only remarks stay strict.

**Blindness report.** As in round 1, this repo's `CLAUDE.md` and memory index were injected. The writer also saw
recent commit subjects saying `confluence-content` failed round 1 on loose graders. It reported no slip.

**Its own limits, left frozen.** Trap graders skip table lines (any line with `|`) and quoted or struck-through
text, so a bad page that states the old value only inside a table passes them. An unquoted Thai sentence that
restates the old rule as fact fails them, as intended.

| case | language | output | traps planted |
|---|---|---|---|
| `holdout2-confluence-content-refund-auto-approve` | Thai | `spec.md` | 500 baht corrected to 300; ShopCoin refund rejected; monthly cap unknown; 180,000 baht budget internal |
| `holdout2-confluence-content-scheduled-s3-export` | English | `prd.md` | 90 days corrected to 30; SFTP rejected; max schedules unknown; blame remark internal |

Eight regex graders per case plus the unscored `process-skill-fired`; all 16 pass the node self-test. Hash: as in
round 1, over `evals/holdout2-*`.

**Rule, fixed before the run.** Round 1's: 5 runs per arm, spend capped at $40, `confluence-content` stays a skill
if its with-skill mean over these two cases is above 0.90 and neither case loses by more than 0.05. If it fails,
every miss is read. It becomes a plain doc only if it would still fail with every false fail scored as a pass;
if false fails alone cause the failure, the round is reported as inconclusive and the operator decides.

### Part B: trigger and template check (not blind; reported, not gated by the A/B rule; graders frozen at `eabee73456197199`)

**Why.** Converting a skill to a plain doc keeps its templates. What the doc loses is the skill loading itself
when the user asks for a ticket or a spec without naming it. Round 1's prompts named the skill, so that was
never tested.

**Cases.** Written by the orchestrator, who has read the skills. Four `trigger-*` cases reuse round 1's fixtures.
Their prompts are plain requests, two Thai and two English, that never name a skill, the Skill tool or acli.
They run with the plugin loaded only (`--ablation none`), 5 runs each, spend capped at $20.

**Graders.**
- `process-skill-fired`: the skill loaded without being named.
- Template shape:
  - Bug: actual then expected, numbered repro steps, two Given/When/Then acceptance criteria, a regression AC.
  - Decision comment: labelled issue, decision and reason fields, and who decided.
  - Spec: business reason and out of scope, user stories, three Given/When/Then acceptance criteria.
  - Given/When/Then accepts Thai `กำหนดให้`/`เมื่อ`/`ผลลัพธ์` or English.

**Commitment (operator, 2026-11-13).** If a skill fires in fewer than 8 of its 10 trigger runs, the recommendation
is to convert it to a plain doc with a `CLAUDE.md` pointer, since the skill packaging then adds nothing over the
doc. Template-shape scores are reported beside it.

### Result (2026-11-13, plugin 0.1.51, commit df8bba7, `claude-opus-5-5`, CLI 2.1.322)

**Part A**, graders frozen at `21ecf8b671503290`. 5 runs per arm, $5.79, no run errors, and the skill fired in
10 of 10 with-arm runs. Full result: `results/2026-11-13-round2-a.json`.

| case | with / without / Δ | cost per run with / without | turns with / without |
|---|---|---|---|
| `holdout2-confluence-content-refund-auto-approve` | 1.000 / 1.000 / 0.000 | $0.425 / $0.189 | 7.0 / 4.8 |
| `holdout2-confluence-content-scheduled-s3-export` | 1.000 / 0.975 / +0.025 | $0.356 / $0.187 | 6.8 / 5.2 |

`confluence-content` passes the rule: with-skill mean 1.000, no case loses. There was one miss, in the no-skill
arm (`trap-no-90-day-retention`), and it is a false fail too. The page says "The PM first draft ... says our copy is
kept for 90 days. On 2026-11-10 ... our copy is kept for **30 days**". The labelled-mention rule in the writer's brief
held: round 1 had 18 false fails per arm, round 2 had 0 with and 1 without. Round 1's pending decision is settled:
`confluence-content` stays a skill.

**Part B**, graders frozen at `eabee73456197199`. Plugin arm only, 5 runs per case, $7.25, no run errors. Full
result: `results/2026-11-13-round2-b.json`.

| case | skill fired | template shape | cost per run | turns |
|---|---|---|---|---|
| `trigger-jira-content-bug-th` | 5/5 | 20/20 | $0.349 | 7.4 |
| `trigger-jira-content-decision-en` | 5/5 | 10/10 | $0.252 | 6.6 |
| `trigger-confluence-content-points-th` | 5/5 | 15/15 | $0.422 | 6.0 |
| `trigger-confluence-content-ratelimit-en` | 5/5 | 15/15 | $0.428 | 7.6 |

Both skills fired in 10 of 10 runs on prompts that never named them, and every trace shows
`Launching skill: jira-acli:...`. That is well above the 8-of-10 commitment, so both stay skills. Every Bug and spec
run wrote acceptance criteria as Thai `กำหนดให้`/`เมื่อ`/`ผลลัพธ์` blocks, including the English rate-limit request,
as the skills' "write the body in Thai" rule says.

**Limits.**
- Part B has no no-skill arm. Its shape graders also accept generic English labels ("Problem", "Out of scope",
  "Given:"), so they show that the skill applies its template. They do not show that plain Claude would not.
- In round 1, Thai bug tickets without the skill used checkbox lists instead of Given/When/Then blocks. That was
  seen while reading misses and was not graded.
- Cost: a with-skill run costs 1.4x to 2.4x a plain one across both rounds.
- No competing skills. A `claude plugin eval` run starts "with only your plugin loaded". User settings, hooks,
  `CLAUDE.md`, other installed plugins, memory and skills are absent (code.claude.com/docs/en/plugin-evals, "How
  runs are isolated"). So 10 of 10 is the trigger rate with no other skill to choose. In a real session with dozens
  of skills it can be lower: mh found one of its own skills fired 0 of 20 times mid-prompt. Part C measures that.

### Part C: trigger in a real session (2026-11-13, before the run)

**Why.** Part B had no competing skills. This part runs the same four `trigger-*` prompts with the operator's normal
user settings: every installed plugin and skill, hooks and `CLAUDE.md`. jira-acli is added with `--plugin-dir`
(the `evals/mkcopy.sh` copy), not installed.

**How.** `claude -p` in a scratch directory holding the case's scaffolded fixtures, with `--permission-mode dontAsk`.
Tools are limited to `Read,Write,Edit,Glob,Grep,Skill,Bash(cat:*),Bash(ls:*)`, so no MCP tool and no acli can run.
The model is the settings default, recorded from the session's init event. There are 3 runs per prompt, so 6 per
skill. A run counts as fired when its stream shows a `Skill` call for that skill. Not graded: the template shape.

**Commitment.** This is Part B's 8-of-10 rule at the same rate. A skill that fires in fewer than 5 of its 6 runs goes
back to the operator with the recommendation to convert it to a plain doc with a `CLAUDE.md` pointer.
