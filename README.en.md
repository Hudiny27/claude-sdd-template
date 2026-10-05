# SDD project template

*Magyar változat: [README.md](README.md)*

Spec-driven development for Claude Code projects, based on the DeepLearning.AI
/ JetBrains course "Spec-Driven Development with Coding Agents". The rules are
written down, and the hooks enforce the parts that can be checked mechanically.

## Install

Once per machine:

```bash
git clone git@github.com:Hudiny27/claude-sdd-template.git ~/.claude/templates/sdd
mkdir -p ~/.claude/skills && cp -r ~/.claude/templates/sdd/claude-skill/sdd-init ~/.claude/skills/
```

Then, in Claude Code, in the project directory: `/sdd-init`

Or from a shell, without Claude:

```bash
bash ~/.claude/templates/sdd/install.sh [TARGET_DIR] [--with-ci]
```

The installer does the following:

- It never overwrites existing files. An existing `CLAUDE.md` gets the rules
  as `CLAUDE.sdd.md`.
- It runs `git init -b main` if the target is not a repository yet. It refuses
  if the target is inside another repository.
- It sets `core.hooksPath=.githooks` and appends the flag files to
  `.gitignore`.
- It runs the guard's self-test in the target.

Re-running it adds only what is missing, so it is safe after a template update.
Restart Claude Code afterwards, because hooks load at session start.

## What gets installed

| Path | Purpose |
|---|---|
| `CLAUDE.md` | SDD rules, workflow, enforcement and keywords for the agent |
| `specs/README.md`, `specs/backlog/` | Constitution formats (mission, tech stack, roadmap) |
| `Plans/README.md`, `Plans/done/` | Feature spec formats and lifecycle |
| `.claude/settings.json` | Wires the hooks: SessionStart, UserPromptSubmit, PreToolUse |
| `.claude/hooks/sdd_guard.py` | The guard: status, keywords, write gates, CI mode |
| `.claude/hooks/test_sdd_guard.py` | Regression tests (stdlib only) |
| `.claude/skills/{constitution,feature-spec,validate-feature,replan}/` | The workflow steps as skills |
| `.githooks/pre-commit` | Agent-independent backstop for code commits |
| `.github/workflows/sdd-check.yml` | Optional (`--with-ci`): PR check for spec–code sync |

## Workflow and keywords

```
/constitution → /feature-spec → #spec-ok → implement → /validate-feature → /replan → /feature-spec ...
```

| Keyword (at the start of a line) | Effect |
|---|---|
| `#spec-szerkesztes` | Unlock the constitution and the guard files for this session |
| `#spec-zar` | Lock them again (otherwise they lock after 12 hours) |
| `#spec-ok` | Approve the feature spec of the current branch, which allows code edits there |

## Enforcement levels

| Rule | Mechanism | Strength |
|---|---|---|
| Constitution changes only with the owner's consent | PreToolUse hook + keyword | Hard (Claude Code) |
| No code without an approved spec, no code on `main` | PreToolUse hook + `#spec-ok` | Hard for Edit/Write and common Bash writes |
| Same, for any agent or editor | git pre-commit | Hard at commit time (bypass `--no-verify` is denied to the agent) |
| PR changes code without changing a spec | CI `sdd-check` + branch protection | Hard at merge time |
| The agent knows the current state | SessionStart status | Always in context |
| Interview quality, level of detail, review depth | `CLAUDE.md` + skills | Soft: the owner's review |

Known gaps: programs that write files on their own (package managers,
generators, formatters), writes hidden behind variables, and other agents
before commit time. Server-side CI with branch protection is the only
guarantee that cannot be bypassed locally.

## Lessons built in (from the earlier PRD guard)

- There is no Stop hook, because Stop also fires when subagents finish.
- A prompt without a keyword never changes a lock.
- Interpreter checks work per line.
- Keywords count only at the start of a line, so a quoted keyword in an agent
  report unlocks nothing.
- `settings.local.json` is guarded, because `disableAllHooks` there would turn
  everything off.

## Maintaining the template

Edit the files under `files/`, then run the tests:

```bash
cd ~/.claude/templates/sdd/files && python3 -m unittest discover -s .claude/hooks -p 'test_*.py'
```

Existing projects do not update themselves. Copy a changed `sdd_guard.py` into
a project by hand; it is locked there, so the owner unlocks it with
`#spec-szerkesztes` first.
