#!/usr/bin/env python3
"""Spec-driven development (SDD) guard for Claude Code, git and CI.

One file, several entry points (first CLI argument):

  session  SessionStart hook: print the SDD status into the agent's context.
  prompt   UserPromptSubmit hook: handle the owner's keywords.
  pretool  PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit|Bash): deny
             - writes to the constitution and to the guard's own files while
               they are locked,
             - writes to code while the current branch has no approved spec,
             - git commands that would bypass the git hooks.
  ci       CI check: `sdd_guard.py ci <base-sha> <head-branch>`. Fails when a
           change touches code without touching a spec.

The git pre-commit hook (.githooks/pre-commit) imports this module, so the
path rules live in one place.

Keywords count only when a line of the owner's message STARTS with them. An
agent report or a quoted mention inside a sentence does not trigger them.
  #spec-szerkesztes  unlock the constitution for this session (max 12 hours)
  #spec-zar          lock it again
  #spec-ok           approve the feature spec of the current branch

Lessons inherited from an earlier PRD guard:
  - No Stop hook. Stop also fires when a subagent finishes, so re-locking
    there ended an unlock in the middle of the turn that granted it.
  - A prompt without a keyword leaves every lock as it is.
  - Interpreter heuristics look per line, not per script, so a script that
    merely quotes a guarded path elsewhere is not denied.
  - Keywords quoted inside agent reports must not unlock anything.

Known limits: programs that write files on their own (npm, generators,
formatters), writes hidden behind variables or command substitution, and
paths assembled at runtime in interpreter code are not seen. The git
pre-commit hook is the backstop for code; CI is the backstop for merges.
"""

import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime

UNLOCK_KEYWORD = "#spec-szerkesztes"
RELOCK_KEYWORD = "#spec-zar"
APPROVE_KEYWORD = "#spec-ok"
# An unlock left behind by an abandoned session must not open the
# constitution days later. 12 hours covers a working day.
UNLOCK_TTL_SECONDS = 12 * 60 * 60

UNLOCK_PREFIX = ".sdd-unlock-"
APPROVED_PREFIX = ".sdd-approved-"
MAIN_BRANCHES = ("main", "master")
SPEC_FILES = ("plan.md", "requirements.md", "validation.md")

# Owner-controlled project documents (relative to a checkout root).
CONSTITUTION = ("specs/mission.md", "specs/tech-stack.md", "specs/roadmap.md")
ROADMAP = "specs/roadmap.md"
# The guard protects its own machinery with the same lock. settings.local.json
# is here because `disableAllHooks` there would switch every hook off. The git
# state files are here because they let a commit skip the pre-commit checks.
SELF_FILES = (
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/hooks/sdd_guard.py",
    ".claude/hooks/test_sdd_guard.py",
    ".git/MERGE_HEAD",
    ".git/SQUASH_MSG",
)
SELF_DIRS = (".githooks",)
# Outside the project, but able to disable this project's hooks.
USER_SETTINGS = (os.path.expanduser("~/.claude/settings.json"),)

# Not code: writable on any branch without an approved spec.
FREE_DIRS = ("specs", "Plans", "docs", ".claude", ".githooks")
FREE_FILES = (".gitignore", ".github/workflows/sdd-check.yml")
FREE_SUFFIXES = (".md",)

# Words that mark a guarded target in interpreter code (checked per line).
GUARDED_WORDS = CONSTITUTION + (
    "sdd_guard",
    "settings.json",
    "settings.local.json",
    ".githooks",
    "SQUASH_MSG",
    "MERGE_HEAD",
    UNLOCK_PREFIX,
    APPROVED_PREFIX,
)

# Commands whose non-option arguments are all changed (recursively for some).
ALL_ARGS_CHANGE = {"rm", "rmdir", "touch", "mkdir", "truncate", "shred", "unlink", "mv", "chmod", "chown"}
# Commands where only the last argument (or -t DIR) receives content.
LAST_ARG_WRITE = {"cp", "ln", "install", "rsync", "scp", "mv"}
GIT_WRITE_SUBCOMMANDS = {"rm", "mv", "checkout", "restore", "clean", "reset", "stash", "apply", "am", "revert", "cherry-pick"}
INTERPRETERS = {"python", "python3", "node", "perl", "ruby", "php", "deno", "bun"}
SHELLS = {"bash", "sh", "zsh", "dash"}
WRAPPERS = {"sudo", "env", "nice", "nohup", "time", "command", "timeout"}
INTERPRETER_WRITE_RE = re.compile(
    r"open\([^)]*['\"][wax+]|\.write\(|write_text|write_bytes|writeFile|appendFile|"
    r"os\.remove|os\.unlink|unlink\(|rmtree|os\.rename|os\.replace|shutil\.(move|copy)|"
    r"rmSync|renameSync|copyFileSync|\bsystem\(|subprocess|child_process|-i\b"
)
REDIRECT_RE = re.compile(r"^(?:\d*|&)(>>?|>\|)(.*)$")
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

REASON_LOCKED = (
    "SDD guard: the constitution (specs/mission.md, specs/tech-stack.md, "
    "specs/roadmap.md) and the SDD guard's own files are owner-controlled and "
    "locked. Do not work around this. Put the proposed change in your reply "
    "instead (file, section, old -> new, why) and ask the owner to unlock: they "
    "start a line of their message with " + UNLOCK_KEYWORD + ". Reading is always allowed."
)
REASON_FLAG = (
    "SDD guard: lock and approval flag files are written only by the hook "
    "itself, never by the agent. Ask the owner instead."
)
REASON_BYPASS = (
    "SDD guard: bypassing git hooks (--no-verify, core.hooksPath) is not "
    "allowed. If a hook blocks a commit, fix the cause or ask the owner."
)


# ------------------------------------------------------------------ helpers


def normalise(raw, cwd):
    return os.path.normpath(os.path.join(cwd, os.path.expanduser(raw)))


def project_dir(payload):
    return os.path.normpath(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())


def git(root, *args, timeout=5):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def inside(path, base):
    return path == base or path.startswith(base + os.sep)


def checkout_root(path, proj):
    """Nearest ancestor of `path` holding .git (a worktree has a .git file)."""
    d = path
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        if d == proj or d == os.path.dirname(d):
            return proj
        d = os.path.dirname(d)


def locate(path, proj):
    """(checkout root, path relative to it) for a path inside the project, else None."""
    if not inside(path, proj):
        return None
    root = checkout_root(path, proj)
    return root, os.path.relpath(path, root).replace(os.sep, "/")


def branch_of(root):
    out = git(root, "symbolic-ref", "--short", "-q", "HEAD")
    return out.stdout.strip() if out and out.returncode == 0 else None


def branch_slug(branch):
    return branch.rsplit("/", 1)[-1]


def find_spec_dir(root, branch):
    """Plans[/done]/YYYY-MM-DD-<slug>/ holding all three spec files, newest first."""
    if not branch or branch in MAIN_BRANCHES:
        return None
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}-" + re.escape(branch_slug(branch)) + "$")
    found = []
    for base in ("Plans", "Plans/done"):
        try:
            names = os.listdir(os.path.join(root, base))
        except OSError:
            continue
        for name in names:
            d = os.path.join(root, base, name)
            if pattern.match(name) and all(os.path.isfile(os.path.join(d, f)) for f in SPEC_FILES):
                found.append(base + "/" + name)
    return max(found, key=os.path.basename) if found else None


def is_free(rel):
    rel = rel.replace(os.sep, "/")
    return rel.endswith(FREE_SUFFIXES) or rel in FREE_FILES or any(rel.startswith(d + "/") for d in FREE_DIRS)


def is_self(rel):
    return rel in SELF_FILES or any(rel == d or rel.startswith(d + "/") for d in SELF_DIRS)


def is_flag(path):
    return os.path.basename(path).startswith((UNLOCK_PREFIX, APPROVED_PREFIX))


def is_ignored(root, rel):
    out = git(root, "check-ignore", "-q", "--", rel)
    return bool(out) and out.returncode == 0


def missing_constitution(root):
    """Constitution files that do not exist yet. While any is missing, the
    constitution is being bootstrapped and stays writable."""
    return [rel for rel in CONSTITUTION if not os.path.isfile(os.path.join(root, rel))]


def first_open_phase(root):
    try:
        with open(os.path.join(root, ROADMAP), encoding="utf-8") as fh:
            for line in fh:
                if re.match(r"^\s*- \[ \] ", line):
                    return line.strip()[6:]
    except OSError:
        pass
    return None


# --------------------------------------------------------------- lock state


def unlock_flag(payload, proj):
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("session_id") or "default")) or "default"
    return os.path.join(proj, ".claude", UNLOCK_PREFIX + session)


def approved_flag(proj, branch):
    return os.path.join(proj, ".claude", APPROVED_PREFIX + re.sub(r"[^A-Za-z0-9_.-]", "_", branch))


def remove(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def write_flag(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def unlocked(payload, proj):
    """True while the owner's unlock for this session is in force."""
    path = unlock_flag(payload, proj)
    try:
        age = time.time() - os.path.getmtime(path)
    except OSError:
        return False
    if age > UNLOCK_TTL_SECONDS:
        remove(path)
        return False
    return True


def approved(proj, root):
    branch = branch_of(root)
    if not branch or branch in MAIN_BRANCHES:
        return False
    return os.path.isfile(approved_flag(proj, branch))


def prune_flags(proj):
    """Drop expired unlocks and approvals of branches that no longer exist."""
    for path in glob.glob(os.path.join(proj, ".claude", UNLOCK_PREFIX + "*")):
        try:
            if time.time() - os.path.getmtime(path) > UNLOCK_TTL_SECONDS:
                remove(path)
        except OSError:
            pass
    for path in glob.glob(os.path.join(proj, ".claude", APPROVED_PREFIX + "*")):
        try:
            with open(path, encoding="utf-8") as fh:
                branch = fh.readline().removeprefix("branch:").strip()
        except OSError:
            continue
        out = git(proj, "show-ref", "--verify", "--quiet", "refs/heads/" + branch)
        if branch and out is not None and out.returncode == 1:
            remove(path)


# ------------------------------------------------------------ path verdicts


def code_reason(proj, root):
    branch = branch_of(root)
    if not branch or branch in MAIN_BRANCHES:
        return (
            "SDD guard: no code changes on " + (branch or "a detached HEAD") + ". "
            "Start a feature branch with its spec first (/feature-spec). Specs, "
            "Plans, docs and Markdown files are always writable."
        )
    spec = find_spec_dir(root, branch)
    if not spec:
        return (
            "SDD guard: branch " + branch + " has no feature spec. Write "
            "Plans/YYYY-MM-DD-" + branch_slug(branch) + "/{plan,requirements,validation}.md "
            "first (/feature-spec), then ask the owner to review it."
        )
    return (
        "SDD guard: the feature spec " + spec + " for branch " + branch + " is not "
        "approved yet. Stop and ask the owner to review it; they approve by "
        "starting a line of their message with " + APPROVE_KEYWORD + "."
    )


def guarded_inside(path, root, git_only):
    """True if `path` is, or is an ancestor of, an existing guarded file.

    For whole-tree git operations (stash, reset --hard, checkout .) only
    guarded files with uncommitted changes count: there is nothing to lose
    otherwise.
    """
    for rel in CONSTITUTION + SELF_FILES + SELF_DIRS:
        target = os.path.join(root, rel)
        if not os.path.exists(target) or not inside(target, path):
            continue
        if git_only:
            out = git(root, "status", "--porcelain", "--", rel)
            if out is not None and out.returncode == 0 and not out.stdout.strip():
                continue
        return True
    return False


def verdict(raw, cwd, proj, payload, kind="write"):
    """Deny reason for changing `raw`, or None when allowed.

    kind: "write" puts content into the file; "tree" changes it or anything
    below it (rm -r, mv, chmod); "git" is a git working-tree operation.
    """
    if not raw:
        return None
    path = normalise(raw, cwd)
    if is_flag(path):
        return REASON_FLAG
    if path in USER_SETTINGS:
        return None if unlocked(payload, proj) else REASON_LOCKED
    loc = locate(path, proj)
    if loc is None:
        return None
    root, rel = loc

    if kind in ("tree", "git"):
        if guarded_inside(path, root, git_only=kind == "git") and not unlocked(payload, proj):
            return REASON_LOCKED
        # Deleting or moving code is left to the pre-commit backstop.
        return None

    if is_self(rel):
        return None if unlocked(payload, proj) else REASON_LOCKED
    if rel in CONSTITUTION:
        if unlocked(payload, proj) or missing_constitution(root):
            return None
        return REASON_LOCKED
    if is_free(rel) or is_ignored(root, rel) or approved(proj, root):
        return None
    return code_reason(proj, root)


def roadmap_tick_only(tool_input, cwd, proj):
    """An Edit of the roadmap that only turns '[ ]' into '[x]'.

    Ticking off a finished phase is routine and needs no unlock.
    """
    path = tool_input.get("file_path")
    loc = locate(normalise(path, cwd), proj) if path else None
    if not loc or loc[1] != ROADMAP:
        return False
    old, new = tool_input.get("old_string") or "", tool_input.get("new_string") or ""
    if old == new or len(old) != len(new):
        return False
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b and not (a == " " and b in "xX" and 0 < i < len(old) - 1 and old[i - 1] == "[" and old[i + 1] == "]"):
            return False
    return True


# ------------------------------------------------------------ bash analysis


def split_heredocs(command):
    """Return (command without heredoc bodies, list of heredoc bodies)."""
    lines = command.split("\n")
    out, bodies, pending = [], [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        pending.extend(m.group(2) for m in HEREDOC_RE.finditer(line))
        i += 1
        while pending and i <= len(lines):
            delim = pending.pop(0)
            body = []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            bodies.append("\n".join(body))
            i += 1  # skip the delimiter line
    return "\n".join(out), bodies


def segments(command):
    """Split a command line into simple commands."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace_split = True
    lexer.commenters = ""
    current = []
    try:
        for tok in lexer:
            if tok and set(tok) <= set(";&|()\n"):
                if current:
                    yield current
                current = []
            else:
                current.append(tok)
    except ValueError:
        # Unbalanced quotes: fall back to a plain split.
        yield command.split()
        return
    if current:
        yield current


def strip_wrappers(words):
    while words and (words[0] in WRAPPERS or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0])):
        words = words[1:]
        while words and words[0].startswith("-"):
            words = words[1:]
    return words


def git_subcommand(args):
    """(subcommand, its arguments), skipping git's own -C/-c options."""
    i = 0
    while i < len(args):
        if args[i] in ("-C", "-c"):
            i += 2
        elif args[i].startswith("-"):
            i += 1
        else:
            return args[i], args[i + 1 :]
    return None, []


def git_bypass(words):
    words = strip_wrappers(words)
    if not words or os.path.basename(words[0]) != "git":
        return False
    args = words[1:]
    if any("core.hookspath" in a.lower() for a in args):
        return True
    sub, rest = git_subcommand(args)
    if sub != "commit":
        return False
    return any(a == "--no-verify" or (re.match(r"^-[A-Za-z]+$", a) and "n" in a[1:]) for a in rest)


SCRIPT_OPTS = ("-e", "-f", "--expression", "--file")


def in_place_flag(arg):
    """-i, -i.bak, --in-place, or -i inside a short flag group (perl -pi)."""
    if arg.startswith("--"):
        return arg.startswith("--in-place")
    return arg.startswith("-") and (arg.startswith("-i") or "i" in arg[1:].split(".")[0])


def script_files(cmd, args):
    """The files an in-place sed/perl edits; its script is not one of them.

    The script is the value of -e/-f (sed, perl) or, for sed without -e/-f,
    the first non-option argument.
    """
    files = []
    has_script_opt = False
    skip_next = False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a in SCRIPT_OPTS:
            has_script_opt = skip_next = True
            continue
        if a.startswith(tuple(o + "=" for o in SCRIPT_OPTS if o.startswith("--"))):
            has_script_opt = True
            continue
        # perl bundles -e at the end of a flag group: -pi -e, -pie
        if cmd == "perl" and a.startswith("-") and not a.startswith("--") and a.endswith("e"):
            has_script_opt = skip_next = True
            continue
        if not a.startswith("-"):
            files.append(a)
    if cmd == "sed" and not has_script_opt and files:
        files = files[1:]
    return files


def write_targets(words):
    """Yield (path, kind) for every file this simple command changes."""
    rest = []
    it = iter(range(len(words)))
    for i in it:
        tok = words[i]
        m = REDIRECT_RE.match(tok)
        if m:
            target = m.group(2)
            if not target and i + 1 < len(words):
                target = words[i + 1]
                next(it, None)
            if target and not target.startswith("&") and target != "/dev/null":
                yield target, "write"
            continue
        rest.append(tok)

    words = strip_wrappers(rest)
    if not words:
        return
    cmd = os.path.basename(words[0])
    args = words[1:]
    plain = [a for a in args if not a.startswith("-")]

    if cmd in ALL_ARGS_CHANGE:
        for a in plain:
            yield a, "tree"
    if cmd in LAST_ARG_WRITE:
        if "-t" in args and args.index("-t") + 1 < len(args):
            yield args[args.index("-t") + 1], "write"
        elif plain:
            yield plain[-1], "write"
    elif cmd == "tee":
        for a in plain:
            yield a, "write"
    elif cmd in ("sed", "perl") and any(in_place_flag(a) for a in args):
        yield from ((a, "write") for a in script_files(cmd, args))
    elif cmd == "dd":
        for a in args:
            if a.startswith("of="):
                yield a[3:], "write"
    elif cmd == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok") for a in args):
        for a in args:
            if a.startswith("-") or a in ("!", "("):
                break
            yield a, "tree"
    elif cmd == "git":
        sub, sub_args = git_subcommand(args)
        if sub in GIT_WRITE_SUBCOMMANDS:
            paths = [a for a in sub_args if not a.startswith("-")]
            if "--" in sub_args:
                paths = sub_args[sub_args.index("--") + 1 :]
            if sub in ("clean", "stash", "reset") and not paths:
                paths = ["."]  # whole-tree operation
            if sub == "reset" and "--hard" not in sub_args:
                paths = []
            for a in paths:
                yield a, "git"


def expand(token, cwd):
    """Expand a glob relative to cwd; keep the token if nothing matches."""
    if any(ch in token for ch in "*?["):
        base = token if os.path.isabs(token) else os.path.join(cwd, token)
        matches = glob.glob(os.path.expanduser(base))
        if matches:
            return matches
    return [token]


def bash_verdict(command, cwd, proj, payload, depth=0):
    text, bodies = split_heredocs(command)
    for words in segments(text):
        if git_bypass(words):
            return REASON_BYPASS
        stripped = strip_wrappers([w for w in words if not REDIRECT_RE.match(w)])
        if stripped and stripped[0] == "cd":
            cwd = normalise(stripped[1] if len(stripped) > 1 else "~", cwd)
            continue
        for raw, kind in write_targets(words):
            for path in expand(raw, cwd):
                reason = verdict(path, cwd, proj, payload, kind)
                if reason:
                    return reason
        cmd = os.path.basename(stripped[0]) if stripped else ""
        if cmd in SHELLS and "-c" in stripped:
            idx = stripped.index("-c")
            if idx + 1 < len(stripped) and depth < 3:
                reason = bash_verdict(stripped[idx + 1], cwd, proj, payload, depth + 1)
                if reason:
                    return reason
        if (cmd in INTERPRETERS or cmd == "eval") and not unlocked(payload, proj):
            code = " ".join(stripped[1:]) + "\n" + "\n".join(bodies)
            for line in code.splitlines():
                if any(w in line for w in GUARDED_WORDS) and INTERPRETER_WRITE_RE.search(line):
                    return REASON_LOCKED
    return None


# -------------------------------------------------------------- hook modes


def deny(reason):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def pretool(payload):
    proj = project_dir(payload)
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or proj

    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        if tool == "Edit" and roadmap_tick_only(tool_input, cwd, proj):
            return
        reason = verdict(tool_input.get("file_path") or tool_input.get("notebook_path"), cwd, proj, payload)
    elif tool == "Bash":
        reason = bash_verdict(tool_input.get("command", ""), cwd, proj, payload)
    else:
        reason = None
    if reason:
        deny(reason)


def has_keyword(text, keyword):
    """True if a line starts with the keyword (alone or followed by a space)."""
    for line in text.splitlines():
        s = line.strip()
        if s == keyword or s.startswith(keyword + " ") or s.startswith(keyword + "\t"):
            return True
    return False


def session_root(payload, proj):
    cwd = normalise(payload.get("cwd") or proj, proj)
    return checkout_root(cwd, proj) if inside(cwd, proj) else proj


def approve(payload, proj):
    root = session_root(payload, proj)
    branch = branch_of(root)
    if not branch or branch in MAIN_BRANCHES:
        print("SDD: " + APPROVE_KEYWORD + " ignored: approvals belong to a feature branch, not " + (branch or "a detached HEAD") + ".")
        return
    spec = find_spec_dir(root, branch)
    if not spec:
        print(
            "SDD: " + APPROVE_KEYWORD + " ignored: branch " + branch + " has no "
            "Plans/YYYY-MM-DD-" + branch_slug(branch) + "/ with plan.md, requirements.md and validation.md."
        )
        return
    write_flag(
        approved_flag(proj, branch),
        "branch: " + branch + "\nspec: " + spec + "\napproved: " + datetime.now().isoformat(timespec="seconds") + "\n",
    )
    print(
        "SDD: the owner approved " + spec + " for branch " + branch + ". Code edits "
        "are allowed on this branch now. Implement plan.md task group by task group."
    )


def prompt(payload):
    proj = project_dir(payload)
    text = payload.get("prompt") or ""
    if has_keyword(text, RELOCK_KEYWORD):
        remove(unlock_flag(payload, proj))
        print("SDD: the constitution is locked again (" + RELOCK_KEYWORD + ").")
    elif has_keyword(text, UNLOCK_KEYWORD):
        write_flag(unlock_flag(payload, proj), "unlocked until " + RELOCK_KEYWORD + " or expiry\n")
        print(
            "SDD: the owner unlocked the constitution and the guard's files for this "
            "session, until " + RELOCK_KEYWORD + " or " + str(UNLOCK_TTL_SECONDS // 3600) + " hours."
        )
    if has_keyword(text, APPROVE_KEYWORD):
        approve(payload, proj)


def session(payload):
    proj = project_dir(payload)
    prune_flags(proj)
    root = session_root(payload, proj)
    branch = branch_of(root)
    lines = ["SDD status (from .claude/hooks/sdd_guard.py; the rules are in CLAUDE.md):"]
    lines.append("- Branch: " + (branch or "none (no git repo or detached HEAD)"))
    missing = missing_constitution(root)
    if missing:
        lines.append("- Constitution: INCOMPLETE (missing " + ", ".join(missing) + "). Start with /constitution. No code until it exists.")
    else:
        state = "UNLOCKED for this session" if unlocked(payload, proj) else "locked (owner unlocks with " + UNLOCK_KEYWORD + ")"
        lines.append("- Constitution: present, " + state + ".")
    if branch and branch not in MAIN_BRANCHES:
        spec = find_spec_dir(root, branch)
        if not spec:
            lines.append("- Feature spec: none for this branch yet. Write it with /feature-spec.")
        elif approved(proj, root):
            lines.append("- Feature spec: " + spec + " (approved; code edits allowed).")
        else:
            lines.append("- Feature spec: " + spec + " (NOT approved; code edits blocked until the owner sends " + APPROVE_KEYWORD + ").")
    else:
        lines.append("- On " + (branch or "no branch") + ": no code changes here. Start the next feature with /feature-spec.")
    phase = first_open_phase(root)
    if phase:
        lines.append("- Next open roadmap phase: " + phase)
    print("\n".join(lines))


def ci(argv):
    """Exit status 1 when the change touches code without a matching spec."""
    if len(argv) != 2:
        print("usage: sdd_guard.py ci <base-sha> <head-branch>", file=sys.stderr)
        return 2
    base, branch = argv
    root = os.getcwd()
    out = git(root, "diff", "--name-only", base + "...HEAD", timeout=60)
    if out is None or out.returncode != 0:
        print("sdd-check: git diff failed: " + (out.stderr.strip() if out else "git not available"), file=sys.stderr)
        return 2
    changed = [f for f in out.stdout.splitlines() if f]
    code = [f for f in changed if not is_free(f)]
    if not code:
        print("sdd-check: no code changes, nothing to check.")
        return 0
    errors = []
    if not any(f.startswith(("specs/", "Plans/")) for f in changed):
        errors.append(
            "code changed but no file under specs/ or Plans/ did. Update the spec, "
            "or label the PR 'no-spec-change' if that is intentional."
        )
    if not find_spec_dir(root, branch):
        errors.append(
            "branch " + branch + " has no Plans/YYYY-MM-DD-" + branch_slug(branch)
            + "/ (or Plans/done/...) with plan.md, requirements.md and validation.md."
        )
    for e in errors:
        print("sdd-check: " + e)
    if errors:
        print("sdd-check: code files changed: " + ", ".join(code[:20]) + (" ..." if len(code) > 20 else ""))
        return 1
    print("sdd-check: OK (" + str(len(code)) + " code files, spec present).")
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "ci":
        sys.exit(ci(sys.argv[2:]))
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}
    if mode == "pretool":
        pretool(payload)
    elif mode == "prompt":
        prompt(payload)
    elif mode == "session":
        session(payload)


if __name__ == "__main__":
    main()
