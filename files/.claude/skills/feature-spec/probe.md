# Fresh-subagent probe

When a feature ships a document an LLM follows (a guide, a prompt, a
skill), `validation.md` contains a fresh-subagent probe: a subagent that
gets only that document does the task with it and reports where it got
stuck or had to guess. The agent runs it during validation, one probe per
mode (for example interactive, autonomous), the probes of one round in
parallel.

## When writing the spec

- Name the probes (one per mode), what each gets, and its success
  criterion.
- Write each probe's task from the sample project's real content (look at
  the sample while writing: what is in it, its segments, scenes): a request
  that makes sense on the sample and whose success can be checked.
- Name the limits of the probe environment in `validation.md` (for example
  a page behind a login without a session file, no network, a missing
  file), and fit the success criterion to them: a step the document
  correctly forbids in this environment is not a success criterion.
- Write the setup as `prepare-probe.sh` in the spec folder, next to
  `validate.sh` (see "Setup").

## Setup

`prepare-probe.sh` sources the template library `.claude/lib/sdd_probe.sh`
(contracts in its comments) and defines only the project hooks. If the
library lacks something, extend it in the template (a proposal in the
template's `backlog/`), not with a local workaround.

- A sample project in an older version's state: use `probe_base`, with the
  update in a `probe_upgrade` hook (no paid step).
- Each round and each probe: use `probe_copy`; rebuild generated documents
  (for example a writing guide) and ignored build output in a
  `probe_regen` hook.
- The probe's prompt names a scratch folder outside the repo for every file
  it writes; use `snapshot_status` before and `assert_no_new_files` after
  the round. The same holds for deep-review subagents in
  `/validate-feature`.

## Evaluating a round

- The probe passes if it meets the success criterion in `validation.md`.
  Of the gaps it reports, only real ones count: a misunderstanding caused
  by the probe's setup (for example a copied project's path) is not one.
- A real gap is **significant** if it made the probe fail, let it pass only
  by a workaround (for example a deliberately broken step), or made it
  guess something that would have given a wrong result (wrong output, a
  skipped rule, a privacy risk). A clarification, a tip or a judgement
  call ("how much zoom is enough?") is **minor**: fix it, but it starts no
  new round.

## Rounds

- After fixing the real gaps, a new fresh subagent and a new copy, until a
  round finds no new significant gap (at most 3 rounds). The last round's
  minor gaps can be fixed in the same round.
- If a significant gap remains after round 3, start no new round: stop and
  tell the owner what remains and why.
- Record the rounds (pass, the gaps fixed, the open questions) under
  "Döntések" in `requirements.md`; ideas outside the scope go to the
  backlog.

## Prompt skeleton

Fill in the probe's task:

```text
You are testing written instructions for an AI writer. Work only from the
documents named here; do not read the source code or tests.

Documents you may read:
- <the document(s) under test, with absolute paths>
- <the inputs the task needs, e.g. a project's generated files>

The project is a scratch copy: <absolute path>. <what is already there and
must not change>.

Situation: <mode, e.g. interactive at the review gate>. Do only this part:
1. <the task, step by step>
2. Then assume the owner answered: "<the owner's answer>". <what to do next>.

Rules: run commands from <repo> with <command prefix>. Never run <paid or
irreversible commands>. Write nothing outside <allowed folders>.
<When the probe has fewer tools than the real run (for example no Glob or
Grep), say so here, so it does not report the missing tool as a gap.>

Report back (plain text), briefly:
- <the result items the success criterion needs>;
- every place where the documents were unclear, missing something,
  contradicting each other, or where you had to guess, quoting the passage.
  This list is the most important part; leave out what you found clear.
```
