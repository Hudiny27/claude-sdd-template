---
name: validate-feature
description: Validate the current feature branch against its spec - run every check in validation.md, compare the code with requirements.md, optionally run a deep review with subagents, then tick the roadmap, archive the spec and prepare the merge. Use when implementation is finished or the owner asks to validate or finish a feature.
---

# Validate feature

## 1. Load the spec

- Find `Plans/YYYY-MM-DD-<slug>/` for the current branch (`<slug>` = last part
  of the branch name). Read `plan.md`, `requirements.md`, `validation.md`.
- Check that every task group in `plan.md` is done. List any that are not.

## 2. Run the automated checks

Run every automated check in `validation.md`. Report each one as a row:
check, pass/fail, short evidence (exit code, key output line). Do not paste
long logs. Never mark a check as passed without running it.

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

Offer it; run it if the owner agrees. Spawn 2–3 parallel subagents over the
whole change, each with one focus: correctness and edge cases; conformance to
`requirements.md` and `specs/tech-stack.md`; tests, security and error
handling. They report findings only. Verify each finding before acting on it.
This keeps the main context clean and catches what a single pass misses.

## 5. Hand over to the owner

- The result table, the drift you fixed, and the open findings.
- The manual checks from `validation.md`, as a short list for the owner.
- Remind the owner to read the key tests or step through them in the debugger
  if they want to own the change, not just accept it.

## 6. Finish (only after the owner confirms that everything passes)

1. Tick the phase in `specs/roadmap.md` (`[ ]` → `[x]`; this edit needs no unlock).
2. Update `CHANGELOG.md` if the project keeps one.
3. Move the spec directory to `Plans/done/`.
4. Propose the commit(s) and make them after approval. Then propose the
   merge into `main` (squash or merge, as the owner prefers) and do it after
   approval. Never push without asking.
5. Suggest `/replan` before the next feature.
