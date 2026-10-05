# Plans/: feature specs

Every roadmap phase (and every replanning change that touches code) gets its
own feature spec before any code is written:

```
Plans/
├── YYYY-MM-DD-<slug>/     # active feature, <slug> = last part of the branch name
│   ├── plan.md            # numbered task groups
│   ├── requirements.md    # scope, out of scope, decisions, context
│   └── validation.md      # checks that prove it is done and can be merged
└── done/                  # finished features, moved here before merge
```

Branch `feature/phase-2-agents` ↔ directory `Plans/2026-10-05-phase-2-agents/`.
The SDD guard, the git pre-commit hook and the CI check all find the spec by
this naming rule.

## Lifecycle

1. `/feature-spec`: branch + interview + the three files. No code yet.
2. Owner review. Changes go through the agent so the three files stay consistent.
3. Owner approves with `#spec-ok`. From then on code edits are allowed on this branch.
4. Implementation, task group by task group.
5. `/validate-feature`: every check in `validation.md`, roadmap tick, move this
   directory to `done/`, merge.

## plan.md

```markdown
# Plan: <feature>

Roadmap: Phase <n> — <title>
Branch: feature/<slug>

## Group 1 — <name>
1. <task>
2. <task>

## Group 2 — <name>
3. <task>

## Group N — Verify
- Run every check in validation.md
```

## requirements.md

```markdown
# Requirements: <feature>

## Scope
- <what this feature delivers>

## Out of scope
- <what it deliberately does not do>

## Decisions
- <decision> — <why> (YYYY-MM-DD)

## Context
- <constraints, related code, stakeholder notes>
```

## validation.md

```markdown
# Validation: <feature>

## Automated checks (the agent runs these)
- [ ] `<command>` — <expected result>

## Manual checks (the owner runs these)
- [ ] <what to look at, where>

## Definition of done
- All checks above pass.
- Spec and code are in sync (no undocumented decisions).
- The roadmap phase is ticked.
```

## Level of detail

Write goals, constraints, success criteria, user flows and key technical
decisions (pinned versions, strictness, data model). Leave out variable names,
CSS classes and file-internal structure: the agent decides those.
