---
name: sdd-init
description: Set up spec-driven development (SDD) in the current project directory from ~/.claude/templates/sdd - CLAUDE.md rules, enforcement hooks, specs/ and Plans/ folders, workflow skills, git pre-commit hook, optional CI check. Use only when the user runs /sdd-init or explicitly asks to initialise SDD in a project.
---

# /sdd-init

Installs the SDD template into the current working directory. The installer
is deterministic and non-destructive; this skill runs it, explains the
result and resolves what it could not do on its own.

Template: `~/.claude/templates/sdd/` (`install.sh`, `files/`, `README.md`).

## 1. Look before installing

- Target: the current working directory, unless the user named another one.
- Show what is there (`ls -A`, and `git status --short` if it is a repository).
  Tell the user whether this is greenfield (empty or no code) or brownfield.
- If the directory is inside another git repository, the installer refuses.
  Ask where the project root should be.

## 2. Ask one question

Use AskUserQuestion: "Install the GitHub PR check (sdd-check workflow)?" with
the options "No, local hooks only" and "Yes, add the CI check". Recommend
"Yes" only if the project will live on GitHub.

## 3. Install

```bash
bash ~/.claude/templates/sdd/install.sh "$PWD"            # or add --with-ci
```

Report the created and skipped files briefly, and the self-test line. If the
self-test failed, stop and show the failure.

## 4. Resolve what the installer reported

- **`.claude/settings.json` existed:** the hooks are not wired. Show the user
  the `hooks` block from `~/.claude/templates/sdd/files/.claude/settings.json`
  merged into their file (as a diff). Apply it only after approval.
- **`CLAUDE.md` existed:** the rules were installed as `CLAUDE.sdd.md`. Offer
  to add the line `@CLAUDE.sdd.md` to `CLAUDE.md`, and do it after approval.
- **`core.hooksPath` was already set:** explain that the pre-commit backstop
  is inactive and ask how to proceed. Never change it silently.

## 5. Commit and restart

- Propose the scaffold commit on `main`:
  `chore(sdd): scaffold spec-driven workflow`, and make it after approval.
- Tell the user to **restart Claude Code in this directory**. Hooks and
  project skills load at session start, so protection is not active in the
  current session. After the restart, the session status line from the guard
  confirms it.
- Next step after the restart: `/constitution` (greenfield: interview;
  brownfield: derived from the existing code first).

## Keywords to tell the user

- `#spec-szerkesztes` at the start of a line: unlock the constitution (until
  `#spec-zar` or 12 hours).
- `#spec-ok` at the start of a line: approve the feature spec of the current branch.
