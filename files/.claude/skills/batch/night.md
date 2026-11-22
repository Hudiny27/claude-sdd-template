# Build window

Unattended. The `overnight` skill's rules hold (no questions, a decision
log, never weaken the checks, a guard denial is a stop sign); this file
adds what a batch needs.

## Order

- First set every feature the guard approved (its reply to `#spec-ok köteg`
  lists them) to `jóváhagyva` with `sdd batch set`; a refused one stays
  `spec`, with the guard's reason as the note.
- Start what `.claude/bin/sdd batch next` prints, and ask it again whenever
  a feature becomes merge-ready or parked. It keeps the order, at most two
  running, a dependant after what it builds on, and the "nem egyszerre"
  pairs apart. When it prints nothing and nothing is `épül`, the night is
  done.
- A dependant starts only when what it builds on is merge-ready; it builds
  in its own worktree on top of that branch (merge that branch's new
  commits into it first, never rebase, then rerun its checks).
- Full test suites queue on the suite lock by themselves; do not start a
  third feature to fill the wait.
- When `main` moved on since a feature branched (for example a template
  update), merge `main` into the feature branch (never rebase), rerun its
  checks and log it.

## Per feature, to merge-ready

1. `sdd batch set … épül`. Build it with the `execute-plan` skill in its
   worktree (the plan: `plan.md` for L, `spec.md` for S and M), committing
   with `.claude/bin/sdd commit`.
2. Validate it as the `validate-feature` skill says, steps 1–4, with no
   popup: run its `validate.sh` if the spec has one (else the commands of
   its "Ellenőrzés" section) and `python3 .claude/lib/sdd_lint.py --final`,
   compare the code with the spec, and run the deep review when the spec's
   `ajtó` and `hatósugár` call for it. Fix real findings; record every
   decision you make as an `agent` line under the spec's "Döntések".
3. Finish it without merging (`validate-feature` step 6, items 2–3): tick
   the passed checks, commit, `.claude/bin/sdd archive` in the worktree. Do
   not tick the roadmap and do not merge: both wait for the morning.
4. `sdd batch set … merge-kész`.

Merge-ready means: every automated check green, the `--final` lint clean,
the review run as the risk fields say and its real findings fixed, the spec
archived, the branch one merge away from `main`; the manual checks listed
for the morning.

## A "nem egyszerre" pair

When both features of a pair are merge-ready, check that they merge one
after the other: in a scratch worktree from `main`, merge the earlier, then
the later, and run the project's check. If that is clean, nothing changes.
If they conflict, merge the earlier branch into the later one in its
worktree, resolve, rerun its checks, write the earlier branch into its
`Függ` cell, and log why: now it merges only together with the earlier.

## Park, do not push through

Run `sdd batch set … parkolva "<reason>"` (it parks the dependants too)
and go on with the rest, when:

- the level rises, or the scope would grow beyond the spec;
- a decision is the owner's (outside the spec and the shared decisions);
- the same check fails after 3 different fix rounds;
- the guard denies a step.


## End

At the time box, or when every feature is merge-ready or parked: write the
overnight report as `morning.md` describes, and stop.
