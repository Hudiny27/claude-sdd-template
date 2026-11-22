---
name: constitution
description: Create or revise the project constitution (specs/mission.md, specs/tech-stack.md, specs/roadmap.md) through an interview with the owner. Use at project start, when bringing SDD into an existing codebase, or when the owner asks to change the mission, tech stack or roadmap.
---

# Constitution

The constitution is the project-level spec: mission, tech stack, roadmap.
Formats are in `specs/README.md`. Follow them exactly.

## 1. Gather context

- Read `CLAUDE.md`, `specs/README.md`, `README.md`, and any TODO, backlog or
  stakeholder notes in the repository.
- Decide the mode and say which one you chose:
  - **Greenfield** (no application code yet): the interview is the main source.
  - **Brownfield** (existing code): first derive the constitution from what
    exists. Use a subagent to explore the codebase and report back only a
    summary: structure, frameworks and their versions, tests and how they run,
    build and deploy, existing docs and open work. Then interview only about
    gaps and contradictions.
- Revision of an existing constitution: work on a `replanning/<topic>` branch.

## 2. Interview before writing

Use the AskUserQuestion tool, grouped on these three, **before writing to disk**:

1. **Mission:** vision, target audience, scope and non-goals, tone.
2. **Tech stack:** gaps, company standards, constraints, testing preferences.
3. **Roadmap:** granularity (prefer very small phases) and the first phases.

Bring your own recommendations and trade-offs into the options. The owner
decides.

## 3. Write, review and commit

- Write the three files in the formats of `specs/README.md`.
- Write `.claude/check.sh` from the tech stack: the project's lint, type
  check and tests, exit 0 when all pass. `sdd commit` runs it before every
  commit; it is the project's own file.
- Summarise the three files in a few lines and point out every assumption
  you made to fill a gap.
- The owner reviews. Apply requested changes yourself, keeping the three files
  consistent with each other.
- Ask in one popup (`CLAUDE.md`, "Döntések és következő lépések felugró
  ablakban"), a multi-select of the next steps: the commit
  `docs(specs): <summary>`, then `/feature-spec` for the first open roadmap
  phase. Do only what the owner ticks.
