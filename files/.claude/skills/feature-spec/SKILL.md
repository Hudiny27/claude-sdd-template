---
name: feature-spec
description: >-
  Új feature vagy javítás indítása spec-vezérelten. Indítsd, ha az owner ezt
  mondja: „kezdjük a következő fázist”, „új feature”, „javítsuk ki …”, „írd
  meg a specet”, vagy „/feature-spec”. Original: start the next roadmap
  feature the spec-driven way - check preconditions, pick the level (S/M/L),
  create the feature branch, interview the owner, and write the spec under
  Plans/YYYY-MM-DD-<slug>/ (spec.md for S and M; plan.md, requirements.md,
  validation.md and validate.sh for L). No code. Use when the owner wants to
  start a feature, the next roadmap phase, a small fix, or a code-touching
  replanning change.
---

# Feature spec

Writes the spec for one feature. Reference files in this skill's folder
hold the details; each step says when to read one.

## 1. Preconditions

- Read `clean-start.md` in this skill's folder and run its checks.
- Recommend `/clear` if this session already worked on something else, so the
  spec, not chat memory, carries the intent.

## 2. Pick the feature, the branch and the level

- Default: the first open phase in `specs/roadmap.md`. If the owner named
  something else: an S-level fix goes ahead without a phase; anything bigger
  that is not on the roadmap goes through `/replan` first.
- Branch and spec folder follow the naming rule in `CLAUDE.md`.
- Before the spec, check read-only whether the goal is already met (the
  live setting, the current code, the deployed instance). If it is, the
  phase shrinks to an S-level check that records the evidence.
- Level: S, M or L as in `CLAUDE.md` ("Szabályok lépésenként"); the
  `size-up` skill has the full rules when it is installed. A big foggy idea
  is not a spec yet: map it first (`wayfinder`), with no feature branch.

## 3. Interview before writing

**S:** no interview. Restate the goal, "kész, ha" and how the owner checks
it in `spec.md`, and go to step 4. **M and L:** run the `grill` skill when it
is installed (popup rounds, the recommended answer first, facts looked up by
you, never asked); otherwise follow the rules below.

Read `specs/mission.md`, `specs/tech-stack.md` and, if relevant, earlier specs
in `Plans/done/`. Then use the AskUserQuestion tool, grouped on these three,
**before writing to disk**:

1. **Scope:** what is in, what is explicitly out.
2. **Decisions:** technical choices the constitution does not settle
   (libraries, data model, pinned versions, strictness).
3. **Context / validation:** constraints, stakeholder notes, and how we will
   know it works (commands the agent can run, manual checks for the owner).

Point out conflicts with the constitution. Do not resolve them silently.

## 4. Write the spec files

Use the formats in `Plans/README.md`. **S and M:** one `spec.md` in the spec
directory; a `validate.sh` only for an M with automated checks worth
scripting. **L:** `plan.md`, `requirements.md`, `validation.md` and
`validate.sh`.

- `plan.md`: numbered task groups, small enough to review one by one; the
  last group runs `validation.md`.
- A number you pick that depends on real data: before writing its decision,
  read `calibration.md` in this skill's folder.
- If the feature ships a document or skill that an LLM follows: before
  writing `validation.md`, read `probe.md` in this skill's folder.
- Before writing `validate.sh`, read `validate-sh.md` in this skill's
  folder, and do its "Before handing over the spec" part before step 5.

## 5. Hand over for review

- Summarise the spec in a few lines and list the assumptions you made. Each
  assumption is also recorded under "Döntések" as an `agent` decision.
- If the spec changes a locked file (the constitution, the guard's files),
  name it in the summary: the implementation asks for `#spec-szerkesztes`
  at its start, not during the validation.
- Close with the popup (`CLAUDE.md`, "Döntések és következő lépések felugró
  ablakban"): the commit `docs(plans): add spec for <feature>` and any other
  open choice of this step.
- Tell the owner at the end of the message, in the chat: when the spec is
  right, start a line of the message with `#spec-ok`. Then start a fresh
  context (`/clear`) and implement: "Implement the task groups in
  Plans/<dir>/plan.md."
