---
name: batch
description: >-
  Kötegelt üzemmód: több feature egy nap alatt, három rövid ablakban. Aktív
  ablak: közös kör és feature-enként kikérdezés és spec, egy köteg-jóváhagyás;
  éjjel felügyelet nélküli építés és validálás merge-kész állapotig; reggel
  egy döntés feature-enként a mergéről. Indítsd, ha az owner ezt mondja:
  „rakjunk össze egy köteget”, „mit építsen éjjel?”, „több feature-t
  egyszerre”, „készítsük elő az éjszakát”, „reggeli jelentés a kötegről”,
  „mi lett éjjel a köteggel?”, vagy „/batch”. Original: batch mode for the
  SDD workflow - interview and spec several features while the owner is
  present, approve them with one keyword, build and validate them unattended
  to merge-ready, and let the owner decide the merges in the morning.
---

# Batch

The SDD stations stay the same (spec, approval, gates, review, the owner's
merge decision); they are grouped in time so the owner takes part in three
short windows instead of all day. The one-by-one flow (`/feature-spec`,
`/validate-feature`) stays available.

Never in a batch: an auth or security feature (it goes the one-by-one way,
stopping after each group). Nothing reaches `main` or the remote at night.

## Which window

Run `.claude/bin/sdd batch status` (the newest batch; "no batch yet" when
there is none):

- no batch for today, or the owner asks for a new one: the **active
  window**;
- a batch whose features are approved and `#éjszaka` is on (or the owner
  says "építsd meg"): the **build window**;
- a batch with a night run behind it (an overnight report exists): the
  **decision window**.

Say in one line which window you are in and why.

## Active window (the owner is here)

Read `active.md` in this skill's folder and follow it. In short: pick the
features, a shared round on the whole batch, then per feature the
`/feature-spec` interview and spec in its own worktree, the time estimate,
the batch commit, the overnight brief, and the owner's two keyword lines.

## Build window (unattended)

Read `night.md` in this skill's folder and follow it. In short: each
feature to merge-ready with `execute-plan` and the validation steps, at
most two at a time, dependants on top of what they depend on; park what
stalls and go on with the rest.

## Decision window (morning)

Read `morning.md` in this skill's folder and follow it. In short: the
report per feature, the agent decisions up for overrule, the manual
checks, then one popup that decides merge, fix or drop per feature, and the
merges and the push the owner ticks.

## Rules for every window

- The batch file (`Plans/kotegek/ÉÉÉÉ-HH-NN-<név>.md`, format in
  `Plans/README.md`) is the batch's state. Change a feature's `Állapot`
  only with `.claude/bin/sdd batch set <név> <branch> <állapot> [megjegyzés]`
  in the main checkout: it also logs the change outside the repo and parks
  the dependants of a parked feature. The guard refuses edits of the copies
  in the worktrees. At night it stays uncommitted; the morning commits it.
- Each feature works only in its own worktree (`.claude/worktrees/<slug>`):
  run its commands with `git -C <worktree>` or from that folder. The main
  checkout stays on `main` and holds only the batch file and the shared
  documents (`docs/szotar.md`, `docs/decisions/`).
- Commit with `.claude/bin/sdd commit` in the feature's worktree; name the
  files.
- The approval keywords are typed by the owner at the start of a line; never
  put them in a subagent prompt.
