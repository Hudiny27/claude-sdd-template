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

- Each round and each probe gets its own fresh, throwaway copy of the
  project in the session scratchpad. The copy is the whole project, no
  folder left out (the build output too), or the probe sees a false state
  (for example "missing build"). Generated documents (for example a writing
  guide) are regenerated on the copy, so the latest fixes are in them.
- If the sample project is in an older version's state (an old approval,
  output in an old format), bring it up to date once in a base copy in the
  scratchpad, with no paid step, and copy every round from it.
- `prepare-probe.sh` does this: the base copy once, then before every round
  the fresh copy and the regenerated documents, with the copy's own path.
  So no round starts with an old path or an outdated guide.
- If the script copies only files git tracks (because untracked ones may
  hold real data), stage the new files before the probe (`git add`, no
  commit); otherwise the copy lacks the guide and the tool.
- The probe's prompt names a scratch folder outside the repo for every file
  it writes; after the round, `git status` shows no file it left. The same
  holds for deep-review subagents in `/validate-feature`.

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
