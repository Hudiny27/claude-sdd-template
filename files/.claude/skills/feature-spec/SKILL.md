---
name: feature-spec
description: Start the next roadmap feature the spec-driven way - check preconditions, create the feature branch, interview the owner, and write Plans/YYYY-MM-DD-<slug>/{plan,requirements,validation}.md. No code. Use when the owner wants to start a feature, the next roadmap phase, or a code-touching replanning change.
---

# Feature spec

Writes the spec for one feature. **No production code in this skill.** The SDD
guard blocks code until the owner approves the spec with `#spec-ok`.

## 1. Preconditions (report each one; stop if any fails)

- The working tree is clean (`git status --short` is empty).
- The previous feature branch is merged and you are on an up-to-date `main`.
- The constitution exists (`specs/mission.md`, `specs/tech-stack.md`,
  `specs/roadmap.md`). If not, run `/constitution` first.
- Recommend `/clear` if this session already worked on something else, so the
  spec, not chat memory, carries the intent.

## 2. Pick the feature and branch

- Default: the first open phase in `specs/roadmap.md` (`- [ ] Phase N — ...`).
  If the owner named something else, use that.
- Branch: `feature/phase-<n>-<short-name>` (for replanning changes:
  `replanning/<topic>`). The spec directory is
  `Plans/<today, YYYY-MM-DD>-<last part of the branch name>/`. The guard,
  the pre-commit hook and CI find the spec by this rule.

## 3. Interview before writing

Read `specs/mission.md`, `specs/tech-stack.md` and, if relevant, earlier specs
in `Plans/done/`. Then use the AskUserQuestion tool, grouped on these three,
**before writing to disk**:

1. **Scope:** what is in, what is explicitly out.
2. **Decisions:** technical choices the constitution does not settle
   (libraries, data model, pinned versions, strictness).
3. **Context / validation:** constraints, stakeholder notes, and how we will
   know it works (commands the agent can run, manual checks for the owner).

Point out conflicts with the constitution. Do not resolve them silently.

## 4. Write the three files

Use the formats in `Plans/README.md`:

- `plan.md`: numbered task groups, small enough to review one by one; the
  last group runs `validation.md`.
- `requirements.md`: scope, out of scope, decisions (with date and why),
  context. No variable names or CSS-level detail.
- `validation.md`: automated checks the agent runs (exact commands and
  expected results), manual checks for the owner, definition of done.

## 5. Hand over for review

- Summarise the spec in a few lines and list the assumptions you made.
- Apply review changes yourself and keep the three files consistent.
- Propose the commit `docs(plans): add spec for <feature>` and make it after approval.
- Tell the owner: when the spec is right, start a line of the message with
  `#spec-ok`. Then start a fresh context (`/clear`) and implement:
  "Implement the task groups in Plans/<dir>/plan.md." For security, auth, data
  or migrations: one task group at a time.
