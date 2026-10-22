---
name: validate-feature
description: Validate the current feature branch against its spec - run every check in validation.md, compare the code with requirements.md, optionally run a deep review with subagents, then tick the roadmap, archive the spec and prepare the merge. Use when implementation is finished or the owner asks to validate or finish a feature.
---

# Validate feature

## 1. Load the spec

- Find `Plans/YYYY-MM-DD-<slug>/` for the current branch (`<slug>` = last part
  of the branch name). Level L: read `plan.md`, `requirements.md`,
  `validation.md`. Levels S and M: read `spec.md`; its "Ellenőrzés" section
  plays the role of `validation.md`, its "Bele tartozik" and "Döntések" the
  role of `requirements.md`.
- Check that every task group in `plan.md` (L) or every "Kész, ha" line (S,
  M) is done. List any that are not.

## 2. Run the automated checks

Run every automated check in `validation.md` (S/M: the "Ellenőrzés" lines
of `spec.md`): `bash Plans/<dir>/validate.sh` if it exists
(with `--live` for the live part), plus by hand any check the script does
not cover (and fix the script). Run the fresh-subagent probe if
`validation.md` has one, as `Plans/README.md` ("Friss subagent-próba")
describes: a fresh scratch copy per round and probe, the prompt skeleton,
the probes of one round in parallel. After fixing what it finds, repeat with
a new fresh subagent until a round finds no new real gap (at most 3 rounds),
and record the rounds under "Döntések". Report
each one as a row: check, pass/fail, short evidence (exit code, key output
line). Do not paste long logs. Never mark a check as passed without running
it. Run the full test suite a second time: a test that fails in only one
run is flaky; find its cause (often a time upper bound) before calling the
checks passed.

## 3. Compare code with spec

- Diff the branch against `main`. For each requirement: met, partly met, or
  not met.
- Anything the code does that the spec does not say is drift. For each case,
  either fix the code or update `requirements.md` (under "Döntések", with date,
  why, and who decided: `owner` or `agent`). If it is a real decision, ask the
  owner first.
- If a renamed or moved file is still mentioned in specs, docs or README,
  update the mentions.

## 4. Deep review (non-trivial features)

Offer it for M and L (not for S); run it if the owner agrees. Spawn 2–3 parallel subagents over the
whole change, each with one focus: correctness and edge cases; conformance to
`requirements.md` and `specs/tech-stack.md`; tests, security and error
handling. They report findings only. Verify each finding before acting on it.
This keeps the main context clean and catches what a single pass misses.

## 5. Hand over to the owner

- The result table, the drift you fixed, and the open findings.
- For paid APIs: the actual usage (characters, minutes, calls) against the
  estimate in `validation.md`.
- The manual checks from `validation.md`, as a short list for the owner.
- Remind the owner to read the key tests or step through them in the debugger
  if they want to own the change, not just accept it.
- End with a popup (CLAUDE.md, "Döntések és következő lépések felugró
  ablakban"): a multi-select of the finishing steps in step 6 (commit the
  spec updates, tick the roadmap and archive, merge into `main`) plus every
  cleanup this feature left behind (a scratch worktree, a probe folder on
  another machine, temporary files), each named with its path. If manual
  checks are still open, one more question: wait for them, or merge with
  them left open. Do only what the owner ticks, in order.

## 6. Finish (only after the owner confirms that everything passes)

If the owner asks to merge before the manual checks are done, leave those
checks open (`[ ]`) in `validation.md`, record the decision under
"Döntések" (`döntött: owner`), and tell the owner that the next `/replan`
will ask about them.

1. Tick the phase in `specs/roadmap.md` (`[ ]` → `[x]`; this edit needs no
   unlock). Skip this when the work has no roadmap phase (a `fix/` branch).
2. Update `CHANGELOG.md` if the project keeps one.
3. Tick every check in `validation.md` (S/M: in the "Ellenőrzés" section of
   `spec.md`) that passed (`[ ]` → `[x]`), then move
   the spec directory to `Plans/done/`. Fix any `Plans/<dir>` path the
   archived files still mention, and rerun `validate.sh` from its new place.
   Start the move from an empty index (`git status` clean) and commit it on
   its own: a move staged early (`git mv`) lands in whatever commit comes
   next.
4. Make the commit(s) and the merge into `main` (squash or merge, as the
   owner prefers) that the owner ticked in the step 5 popup; if the popup
   was skipped, ask in one now. Never push without asking.
5. After the merge, always ask about the push in a popup (AskUserQuestion),
   never as a question in the chat, so the owner only has to click. Name the
   branch and the remote, and the commits it would send
   (`git log --oneline origin/main..main`). Options: "Push (Javasolt)" —
   push `main` now; "Most ne" — leave it for later. Push only on the
   owner's click; a denied push is a stop sign.
6. Offer `/replan` (before the next feature) as an option in the push
   popup, so one click covers both.
