---
name: replan
description: Replanning between features - review the roadmap, propose constitution updates, improve the SDD workflow itself, and schedule backlog items. Use after a feature is merged, when the owner brings new requirements, or when the owner asks to step back and replan.
---

# Replan

"Run slow to run fast": most of the developer's work is now planning and
validation, so make time between features to adjust the plan.

## 1. Clean start

- Read `../feature-spec/clean-start.md` and run its checks, including the
  `/replan` part (open manual checks; ask about them in step 2).
- Read `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, recent
  entries in `Plans/done/` and `specs/backlog/`.

## 2. Questions for the owner

Use the AskUserQuestion tool, grouped:

1. **Roadmap:** Is the next open phase still the right one? Should phases be
   merged, split or reordered? Should backlog items be scheduled?
2. **Constitution:** New stakeholder input, testing preferences, stack changes?
3. **Workflow:** What repeated manually in the last feature and could become a
   skill or a check (validation steps, changelog, release notes)? Prefer a
   mechanism (code, a check) to a sentence. If the session's SDD status has
   a `Template:` line, offer to update the template-owned files with
   `install.sh --update` (it shows the diff first; the guard's files need
   `#spec-szerkesztes`).

Bring your own observations from the last feature as options.

## 3. Workflow improvements

Template-owned files (`CLAUDE.md`, the four skills and their reference
files, `Plans/README.md`, `specs/README.md`, the hooks) are not edited in a
project: a template update overwrites them. Project lessons go to the
extension points: `.claude/rules/<topic>.md`, `.claude/project.md`, and the
project's own scripts and tests.

- **Placement order.** Every workflow improvement takes the first rung that
  works:
  1. code or a check (a script, a test, a hook in the project);
  2. a path-scoped rule: `.claude/rules/<topic>.md` with `paths:`
     frontmatter (only `paths` is read; a rule without it loads at launch);
  3. a step's reference file, read only at that step (in the template: the
     skill's folder; in a project: a project file a rule or a project skill
     names for that step);
  4. `CLAUDE.md` (in a project: `.claude/project.md`, which `CLAUDE.md`
     loads in every session): only what matters in every session, short.
- **Log.** Each improvement gets one line in `.claude/workflow-log.md`
  (format there), with the rung it landed on. Code, specs and the roadmap
  are not logged.
- **Review.** When the SDD status says the log reached 10 entries since the
  last review, go through them with the owner to tidy up locally. For each
  entry one decision: turn it into code or a check if possible, merge it
  with another, or delete it. The result is usually less text than before.
  Then append `review: YYYY-MM-DD` to the log; the count starts again.
- **Template gate.** A lesson goes to the template only if all hold: it is
  a mechanism (code, hook, test, step structure) or concerns the
  philosophy; it came up independently in at least two projects; it cannot
  be solved at the project's extension points. A template change is a
  proposal file in the template repo's `backlog/`, approved by the owner.

## 4. Apply

- Work on a `replanning/<topic>` branch.
- Small code corrections need their own spec, like any feature
  (`Plans/YYYY-MM-DD-<topic>/` + `#spec-ok`; the guard enforces this). Larger
  new work becomes a new roadmap phase instead of being done here.
- When a constitution change affects existing feature specs or code, list the
  affected places and update them in the same branch.
- New workflow skills go to `.claude/skills/<name>/SKILL.md` (project) unless
  the owner wants them global.

## 5. Close

Ask in one popup (`CLAUDE.md`, "Döntések és következő lépések felugró
ablakban"), a multi-select: the commits, the merge, any cleanup (worktree,
temporary files) and `/feature-spec` for the next feature. Do only what the
owner ticks, in order; the push gets its own question.
