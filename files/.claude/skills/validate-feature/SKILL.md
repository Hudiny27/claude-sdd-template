---
name: validate-feature
description: Validate the current feature branch against its spec - run every check in validation.md, compare the code with requirements.md, optionally run a deep review with subagents, then tick the roadmap, archive the spec and prepare the merge. Use when implementation is finished or the owner asks to validate or finish a feature.
---

# Validate feature

Reference files hold the details; each step says when to read one. Some
live in the `feature-spec` skill's folder (`../feature-spec/`).

## 1. Load the spec

- Find the branch's spec folder (the SDD status names it). Level L: read
  `plan.md`, `requirements.md`, `validation.md`. Levels S and M: read `spec.md`; its "Ellenőrzés" section
  plays the role of `validation.md`, its "Bele tartozik" and "Döntések" the
  role of `requirements.md`.
- Check that every task group in `plan.md` (L) or every "Kész, ha" line (S,
  M) is done. List any that are not.

## 2. Run the automated checks

- Before running or changing `validate.sh`, read
  `../feature-spec/validate-sh.md` (its "At validation" part sets the run
  order and the second suite run).
- Run every automated check in `validation.md` (S/M: the "Ellenőrzés" lines
  of `spec.md`): `bash Plans/<dir>/validate.sh` if it exists (with `--live`
  for the live part); a check the script misses is added to it.
- If `validation.md` has a fresh-subagent probe, read
  `../feature-spec/probe.md` and run it as it says.
- Report each check as a row: check, pass/fail, short evidence (exit code,
  key output line). Do not paste long logs. Never mark a check as passed
  without running it.

## 3. Compare code with spec

The level of the review: does it work, and does it match the spec.

- Diff the branch against `main`. For each requirement: met, partly met, or
  not met.
- Run `python3 .claude/lib/sdd_lint.py --final` and fix each finding
  (paths left dangling by a rename, missing calibration results).
- Anything the code does that the spec does not say is drift. For each case,
  either fix the code or record it under "Döntések" in `requirements.md`
  (S/M: `spec.md`). If it is a real decision, ask the owner first.

## 4. Deep review (non-trivial features)

Sized by `ajtó` and `hatósugár` under "Kockázat és visszaút": egyirányú or
nagy: run it by default (the owner may skip it); kétirányú and kicsi, or
level S: skip it; otherwise offer it. Spawn 2–3
parallel subagents over the whole change, each with one focus: correctness
and edge cases; conformance to `requirements.md` and `specs/tech-stack.md`;
tests, security and error handling. Each also gets `docs/kodolasi-szabalyok.md`
and `docs/szotar.md` if they exist: a finding names the broken rule, or the
code name that differs from the glossary. They report findings only. Verify each
finding before acting on it. Each reviewer writes only to a scratch folder,
as in `../feature-spec/probe.md` ("Setup").

## 5. Hand over to the owner

- The result table, the drift you fixed, and the open findings.
- For paid APIs: the actual usage (characters, minutes, calls) against the
  estimate in `validation.md`.
- The manual checks from `validation.md`, as a short list, sized by the
  same two fields: kétirányú and kicsi: the evidence (output, screenshot),
  the checks optional; egyirányú or nagy: every check, plus the edge cases
  worth trying to break it with.
- Remind the owner to read the key tests or step through them in the debugger
  if they want to own the change, not just accept it.
- End with a popup (`CLAUDE.md`, "Döntések és következő lépések felugró
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
will ask about them. Before step 3, read `finish.md` in this skill's
folder.

1. Tick the phase in `specs/roadmap.md` with the Edit tool. Skip this when
   the work has no roadmap phase (a `fix/` branch).
2. Update `CHANGELOG.md` if the project keeps one.
3. Tick every check in `validation.md` (S/M: in the "Ellenőrzés" section of
   `spec.md`) that passed (`[ ]` → `[x]`), commit, then archive the spec
   with `.claude/bin/sdd archive`.
4. Make the commit(s) and the merge into `main` (squash or merge, as the
   owner prefers) that the owner ticked in the step 5 popup; if the popup
   was skipped, ask in one now.
5. After the merge, ask about the push in a popup: name the branch, the
   remote and the commits it would send (`git log --oneline
   origin/main..main`). Push only on the owner's click; a denied push is a
   stop sign.
6. Offer `/replan` (before the next feature) as an option in the push
   popup, so one click covers both.
