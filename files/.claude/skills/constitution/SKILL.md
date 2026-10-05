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

## 3. Write

- While any of the three files is missing, the guard lets you write all of
  them (bootstrap).
- Once all three exist they are locked. If a write is denied, stop: show the
  exact change you propose (file, section, old -> new, why) and ask the owner
  to send `#spec-szerkesztes`. Never work around the guard.
- The roadmap uses one checkbox line per phase: `- [ ] Phase N — <title>`.

## 4. Review and commit

- Summarise the three files in a few lines and point out every assumption
  you made to fill a gap.
- The owner reviews. Apply requested changes yourself, keeping the three files
  consistent with each other.
- Propose the commit `docs(specs): <summary>` and make it after approval.
- Next step: `/feature-spec` for the first open roadmap phase.
