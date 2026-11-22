# Build window

Unattended. The `overnight` skill's rules hold (no questions, a decision
log, never weaken the checks, a guard denial is a stop sign); this file
adds what a batch needs.

## Order

- Run features from the batch file's order. At most two at the same time,
  and never two that the shared round marked as touching the same files.
- A dependant starts only when what it builds on is merge-ready; it builds
  in its own worktree on top of that branch (merge that branch's new
  commits into it first, never rebase, then rerun its checks).
- Full test suites queue on the suite lock by themselves; do not start a
  third feature to fill the wait.

## Per feature, to merge-ready

1. Set `Állapot: épül`. Build it with the `execute-plan` skill in its
   worktree (the plan: `plan.md` for L, `spec.md` for S and M), committing
   with `.claude/bin/sdd commit`.
2. Validate it as the `validate-feature` skill says, steps 1–4, with no
   popup: run `validate.sh` and `python3 .claude/lib/sdd_lint.py --final`,
   compare the code with the spec, and run the deep review when the spec's
   `ajtó` and `hatósugár` call for it. Fix real findings; record every
   decision you make as an `agent` line under the spec's "Döntések".
3. Finish it without merging (`validate-feature` step 6, items 2–3): tick
   the passed checks, commit, `.claude/bin/sdd archive` in the worktree. Do
   not tick the roadmap and do not merge: both wait for the morning.
4. Set `Állapot: merge-kész`.

Merge-ready means: every automated check green, the `--final` lint clean,
the review run as the risk fields say and its real findings fixed, the spec
archived, the branch one merge away from `main`; the manual checks listed
for the morning.

## Park, do not push through

Set `Állapot: parkolva` with the reason in the log, and go on with the
features that do not depend on it, when:

- the level rises, or the scope would grow beyond the spec;
- a decision is the owner's (outside the spec and the shared decisions);
- the same check fails after 3 different fix rounds;
- the guard denies a step.

Features that build on a parked one stop too (`parkolva`, reason: waits on
the other).

## End

At the time box, or when every feature is merge-ready or parked: write the
overnight report as `morning.md` describes, and stop.
