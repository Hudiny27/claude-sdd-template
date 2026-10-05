---
name: replan
description: Replanning between features - review the roadmap, propose constitution updates, improve the SDD workflow itself, and schedule backlog items. Use after a feature is merged, when the owner brings new requirements, or when the owner asks to step back and replan.
---

# Replan

"Run slow to run fast": most of the developer's work is now planning and
validation, so make time between features to adjust the plan.

## 1. Clean start

- On an up-to-date `main`, clean working tree, last feature merged. Report
  and stop if not.
- Read `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, recent
  entries in `Plans/done/` and `specs/backlog/`.

## 2. Questions for the owner

Use the AskUserQuestion tool, grouped:

1. **Roadmap:** Is the next open phase still the right one? Should phases be
   merged, split or reordered? Should backlog items be scheduled?
2. **Constitution:** New stakeholder input, testing preferences, stack changes?
3. **Workflow:** What repeated manually in the last feature and could become a
   skill or a check (validation steps, changelog, release notes)?

Bring your own observations from the last feature as options.

## 3. Apply

- Work on a `replanning/<topic>` branch.
- Constitution changes are locked. Show the exact proposed change first (file,
  section, old -> new, why), then ask the owner to send `#spec-szerkesztes`.
- Small code corrections need their own spec, like any feature
  (`Plans/YYYY-MM-DD-<topic>/` + `#spec-ok`; the guard enforces this). Larger
  new work becomes a new roadmap phase instead of being done here.
- When a constitution change affects existing feature specs or code, list the
  affected places and update them in the same branch.
- New workflow skills go to `.claude/skills/<name>/SKILL.md` (project) unless
  the owner wants them global.

## 4. Close

Propose the commits and the merge, and make them after approval. Then the
next feature starts with `/feature-spec`.
