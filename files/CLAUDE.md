# Project rules: spec-driven development (SDD)

This project is spec-driven. The spec defines **what** and **why**; code is the
**how**. The rules below extend the global `~/.claude/CLAUDE.md`. Where they
are more specific, they win inside this project. Hooks enforce the core rules
(see "Enforcement"), so treat a denial as a stop sign, not an obstacle.

## Source of truth

Precedence: `specs/` (constitution) > the current feature spec in `Plans/` >
chat history. Never rely on memory of earlier sessions; read the files.

```
CLAUDE.md                  # these rules
specs/                     # constitution: owner-controlled, hook-locked
├── mission.md             # why: vision, audience, scope, non-goals
├── tech-stack.md          # stack, versions, constraints, testing
├── roadmap.md             # small phases, one "- [ ] Phase N — title" line each
└── backlog/               # research and ideas not yet on the roadmap (not locked)
Plans/                     # feature specs: agent-written, owner-approved
├── YYYY-MM-DD-<slug>/     # plan.md, requirements.md, validation.md
└── done/                  # finished features
.claude/hooks/sdd_guard.py # the guard (Claude Code hooks, pre-commit, CI)
.claude/skills/            # constitution, feature-spec, validate-feature, replan
.githooks/pre-commit       # agent-independent backstop
```

Formats: `specs/README.md` and `Plans/README.md`. Branch
`feature/phase-2-agents` ↔ `Plans/YYYY-MM-DD-phase-2-agents/` (the slug is the
last part of the branch name).

## Workflow

| Step | Skill | Result |
|---|---|---|
| 1. Constitution (once, then living) | `/constitution` | `specs/` written in an interview |
| 2. Feature spec | `/feature-spec` | branch + `Plans/<dir>/` with 3 files, **no code** |
| 3. Owner approval | owner sends `#spec-ok` | code edits unlocked on this branch |
| 4. Implementation | (prompt) | code, task group by task group |
| 5. Validation | `/validate-feature` | checks run, drift fixed, roadmap ticked, merge |
| 6. Replanning | `/replan` | roadmap, constitution and workflow updated |

At the start of every session, the guard prints the SDD status: branch,
constitution state, current feature spec and approval, next roadmap phase.
Act on it.

## Enforcement (hooks)

`.claude/hooks/sdd_guard.py`, wired in `.claude/settings.json`:

| What | Rule | Unlock |
|---|---|---|
| `specs/mission.md`, `tech-stack.md`, `roadmap.md` | Locked once all three exist; writable while any is missing (bootstrap) | Owner: `#spec-szerkesztes`, until `#spec-zar` or 12 hours |
| Roadmap checkbox `[ ]` → `[x]` (Edit tool) | Always allowed | none needed |
| Guard files: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks/sdd_guard.py`, its test, `.githooks/`, `~/.claude/settings.json` | Locked | Owner: `#spec-szerkesztes` |
| Code (everything except `specs/`, `Plans/`, `docs/`, `.claude/`, `.githooks/`, `*.md`, `.gitignore`, git-ignored files) | Only on a feature branch whose spec the owner approved | Owner: `#spec-ok` on that branch |
| Lock and approval flag files (`.claude/.sdd-*`) | Never writable by the agent | none |
| `git commit --no-verify`, changing `core.hooksPath` | Always denied | none |

- Keywords count only when a line of the **owner's** message starts with them.
  Never write a keyword at the start of a line in a prompt you give a subagent,
  and never ask a subagent to "unlock" anything.
- When a write is denied: stop, tell the owner what you wanted to change and
  why, and propose the exact change (file, section, old -> new). Never work
  around the guard (other tools, scripts, different paths, flag files).
- The git pre-commit hook enforces the same code rule for any agent or
  editor: no code commits on `main` and none on a branch without a spec
  (merge and squash-merge commits are allowed). The optional CI check
  (`.github/workflows/sdd-check.yml`) fails a PR that changes code without
  changing a spec, unless it has the label `no-spec-change`.
- Known gaps: programs that write files themselves (package managers,
  generators, formatters) and writes hidden behind variables are not seen by
  the hook. The pre-commit hook catches them at commit time. Behave as if the
  rules had no gaps.

## Rules per step

**Constitution:** interview first (AskUserQuestion, grouped on mission / tech
stack / roadmap), write after. Brownfield: derive from the existing code,
README, TODO and commits first, then ask about gaps. Roadmap phases are small,
shippable and independently reviewable.

**Feature spec:** start from a clean state (no uncommitted work, previous
branch merged, on `main`) and preferably a fresh context (`/clear`). Interview
(grouped on scope / decisions / context) before writing. `validation.md` must
contain commands you can run yourself plus the owner's manual checks. No code
in this step.

**Implementation:** only after `#spec-ok`. Follow `plan.md` task group by task
group. For security, auth, data and migrations: one group at a time, then
stop. Do not go beyond `requirements.md`. If something is missing or
ambiguous, stop and ask. Never decide silently.

**Validation:** run every check in `validation.md` and report pass/fail with
evidence. Review at the level of "does it work and match the spec". For
non-trivial features, offer a deep review by parallel subagents. Done means:
all checks pass, spec and code in sync, roadmap phase ticked, spec moved to
`Plans/done/`.

**Replanning:** between features, on a `replanning/<topic>` branch. Small code
corrections still need a spec and `#spec-ok`; larger new work becomes a new
roadmap phase. Mid-feature ideas go to `specs/backlog/YYYY-MM-DD-<topic>.md`,
not into the current branch or the roadmap.

## Spec and code stay in sync

- Any change in behaviour or decisions updates the relevant spec file in the
  same change. Fix spec and code together when a bug traces back to the spec.
- Decisions discovered during review go to `requirements.md` under "Decisions",
  with date and reason. An omission found in review is not a failure: record it.
- Spec changes go through the agent so that related files (plan, requirements,
  validation, README) stay consistent. After renames or moves, including IDE
  refactors by the owner, update every mention in specs and docs.

## Level of detail in specs

Include goals, audience, constraints, success criteria, user flows and key
technical decisions (pinned versions, strictness, data model). Leave out
variable names, CSS classes and file-internal structure.

## Interplay with the global rules

- The global "plan first if bigger than ~3 files" rule is fulfilled by the
  feature spec: `plan.md` is that plan, `#spec-ok` is the approval.
- The global "ask one specific question" rule has one exception: constitution
  and spec interviews use grouped questions.
- Global git and safety rules still apply. Propose commits at the end of each
  step and make them only after approval. Never push without asking.
- Commit scopes: `docs(specs): ...` for the constitution, `docs(plans): ...`
  for feature specs, Conventional Commits for code.
