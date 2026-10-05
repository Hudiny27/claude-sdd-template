# specs/: the project constitution

The constitution holds the decisions every feature builds on. It is written in
an interview between the owner and the agent (`/constitution`), and it is
owner-controlled: once all three files exist, the SDD guard blocks agent writes
until the owner unlocks them with `#spec-szerkesztes` (see `CLAUDE.md`).

| File | Answers | Changes |
|---|---|---|
| `mission.md` | Why does this exist, for whom, what is in and out of scope? | Rarely |
| `tech-stack.md` | Which technologies and constraints, and why? | On replanning |
| `roadmap.md` | In which small, shippable phases do we get there? | Every replanning |
| `backlog/` | Research and ideas not yet on the roadmap | Any time (not locked) |

## mission.md

```markdown
# Mission

## Vision
<one paragraph: the problem and the change this project makes>

## Target audience
- <who> — <what they need from it>

## Scope
- <in scope>

## Non-goals
- <explicitly out of scope>

## Stakeholder input
- <name / role> — <what they asked for>
```

## tech-stack.md

```markdown
# Tech stack

## Overview
<two or three sentences>

## Stack
| Layer | Choice | Version | Rationale |
|---|---|---|---|
| Language | ... | pinned | ... |

## Constraints
- <company standards, hosting, security, licences>

## Testing and validation
- <test framework, how checks are run: commands>

## Known gaps
- <what is consciously missing for now>
```

## roadmap.md

Each phase is one top-level checkbox line. The SDD guard reads the first open
one as the next phase, and ticking a box (`[ ]` → `[x]`) is the only roadmap
edit the agent may make without an unlock.

```markdown
# Roadmap

Phases are intentionally small: each is a shippable slice, independently
reviewable and testable.

- [ ] Phase 1 — <title>
  - <what is delivered>
  - <how we know it works>
- [ ] Phase 2 — <title>
  - ...
```

## backlog/

One file per topic: `backlog/YYYY-MM-DD-<topic>.md` with the question, the
findings, the recommendation and what was decided. A backlog item reaches the
roadmap only through replanning, with a link back to its file.
