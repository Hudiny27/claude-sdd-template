#!/usr/bin/env python3
"""sdd_lint.py: checks the parts of the SDD workflow that are text rules.

Template-owned: `install.sh --update` overwrites it. Do not edit it in a
project; propose changes in the template's backlog/ instead.

Usage (from the repository root or anywhere inside it):
  python3 .claude/lib/sdd_lint.py            the current branch's spec folder
  python3 .claude/lib/sdd_lint.py --final    the same, plus calibration
                                             results and dangling paths
                                             (run by /validate-feature)
  python3 .claude/lib/sdd_lint.py --staged   the staged files (run by the
                                             git pre-commit hook)
  --base REF   the branch the decisions and changes are compared with, at
               the point this branch left it (default: main; on main
               itself: HEAD)

Checks:
  spec         no template placeholder left (`<what to write>`, `- …`);
               spec.md: `szint: S|M` and the sections its level needs;
               level M and L: `ajtó:` and `hatósugár:` under "Kockázat és
               visszaút";
               level L: plan.md task groups, the requirements.md and
               validation.md sections, a validate.sh; a `Branch:` line
               that matches the folder.
  decisions    every bullet under "Döntések" has exactly one
               `(döntött: owner|agent, YYYY-MM-DD)`; a bullet that exists
               on the base branch is not deleted or reworded, only marked
               `(felváltva YYYY-MM-DD, lásd ...)`.
  calibration  every "Kalibrálás" subsection has Minta, Söprés, Választás,
               Ellenőrzés in order; --final: a "kalibrálandó" decision needs
               at least one subsection.
  coverage     with a validate.sh: every automated check bullet names the
               ID of a `check` call in it (a fresh-subagent probe is exempt).
  paths        code never names a dated spec folder (Plans/YYYY-MM-DD-...);
               a script in a spec folder takes the repo root from git, not
               from `parents[n]`.
  shell        `bash -n` and, when installed, `shellcheck` on spec-folder
               shell scripts.
  backlog      every specs/backlog/*.md item has `Állapot: nyitott | ütemezve
               | kész | elvetve` near the top.
  batch        a staged Plans/kotegek/*.md: front matter, the feature table,
               worktrees under .claude/worktrees/, a declared
               Auth/biztonság (igen | nem), filled estimates, known states.
  size         CLAUDE.md (or CLAUDE.sdd.md) at most 150 lines, SKILL.md at
               most 100, .claude/project.md at most 60.
  dangling     --final: backticked paths in the Markdown changed on this
               branch exist, and no Markdown still names a file this branch
               deleted or renamed.

Output: one `path:line: [check] message` line per finding; exit 1 if any.
"""

import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(HERE, "..", "hooks"))
import sdd_guard as guard  # noqa: E402

SIZE_LIMITS = (("CLAUDE.md", 150), ("CLAUDE.sdd.md", 150), (".claude/project.md", 60))
SKILL_LIMIT = 100
SPEC_SECTIONS = {
    "S": ("Cél", "Kész, ha", "Ellenőrzés"),
    "M": ("Cél", "Bele tartozik", "Nem tartozik bele", "Döntések", "Kész, ha", "Ellenőrzés", "Kockázat és visszaút"),
}
L_SECTIONS = {
    "requirements.md": ("Hatókör", "Hatókörön kívül", "Döntések", "Kontextus", "Kockázat és visszaút"),
    "validation.md": ("Automatikus ellenőrzések", "Kézi ellenőrzések", "Kész definíciója"),
}
RISK_FIELDS = (
    ("ajtó", ("egyirányú", "kétirányú")),
    ("hatósugár", ("kicsi", "közepes", "nagy")),
)
CALIBRATION_FIELDS = ("Minta", "Söprés", "Választás", "Ellenőrzés")
DECIDED = re.compile(r"\(döntött: (owner|agent), \d{4}-\d{2}-\d{2}\)")
SUPERSEDED = re.compile(r"\s*\(felváltva [^)]*\)\s*$")
SUPERSEDED_OK = re.compile(r"\(felváltva \d{4}-\d{2}-\d{2}, lásd [^)]+\)")
DATED_SPEC = re.compile(r"Plans/(?:done/)?\d{4}-\d{2}-\d{2}-")
PARENTS = re.compile(r"\.parents\[\d+\]|(?:\.parent){2,}")
CHECK_ID = re.compile(r"(?:^|[\s;&|(])check\s+([A-Za-z][A-Za-z0-9_.-]*)\s")
PROBE_WORDS = re.compile(r"subagent|próba|probe", re.I)
# A template hint such as `<1–3 mondat: ...>`; `<dir>` (no space) and HTML comments are not.
PLACEHOLDER = re.compile(r"<[^!<>\s][^<>\n]* [^<>\n]*>")
BACKTICK = re.compile(r"`([^`\s]+)`")
NOT_A_PATH = re.compile(r"[<>*{}$…|?\[\]()'\"=,;:@~^]")
DANGLING_SKIP = ("Plans/done/", "specs/backlog/")
BATCH_ITEM = re.compile(r"^Plans/kotegek/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$")
BATCH_STATES = ("spec", "jóváhagyva", "épül", "merge-kész", "parkolva", "mergelve", "javítás", "elvetve")
BATCH_COLUMNS = ("#", "branch", "fokozat", "függ", "worktree", "becslés", "auth/biztonság", "állapot")
BACKLOG_STATES = ("nyitott", "ütemezve", "kész", "elvetve")
BACKLOG_ITEM = re.compile(r"^specs/backlog/[^/]+\.md$")


class Lint:
    def __init__(self, root, staged=False, base=None):
        self.root = root
        self.staged = staged
        self.findings = []
        branch = guard.branch_of(root)
        self.branch = branch
        self.base = base or ("HEAD" if not branch or branch in guard.MAIN_BRANCHES else "main")
        # Compare with the branch point, not with where the base is now: a base
        # that moved on would make its own changes look like this branch's.
        point = self.git("merge-base", self.base, "HEAD") if self.base != "HEAD" else None
        self.since = point.strip() if point and point.strip() else self.base

    # -- helpers

    def add(self, rel, line, check, message):
        self.findings.append((rel, line, check, message))

    def git(self, *args):
        out = subprocess.run(["git", "-C", self.root, *args], capture_output=True, text=True)
        return out.stdout if out.returncode == 0 else None

    def read(self, rel):
        """The file's text: from the index in --staged mode, else from the working tree."""
        if self.staged:
            text = self.git("show", ":" + rel)
            if text is not None:
                return text
        try:
            with open(os.path.join(self.root, rel), encoding="utf-8") as fh:
                return fh.read()
        except (OSError, UnicodeDecodeError):
            return None

    def exists(self, rel):
        return self.read(rel) is not None

    def base_text(self, rel):
        return self.git("show", self.since + ":" + rel)

    # -- checks

    def placeholders(self, rel, text):
        fence = False
        for i, ln in enumerate(text.splitlines(), 1):
            if ln.startswith("```"):
                fence = not fence
                continue
            plain = re.sub(r"`[^`]*`", "", ln)
            if not fence and (PLACEHOLDER.search(plain) or plain.strip() in ("- …", "…")):
                self.add(rel, i, "spec", "template placeholder left: " + short(ln.strip()))

    def spec(self, spec_dir):
        light = spec_dir + "/" + guard.LIGHT_SPEC
        for name in (guard.LIGHT_SPEC, *guard.SPEC_FILES):
            text = self.read(spec_dir + "/" + name)
            if text is not None:
                self.placeholders(spec_dir + "/" + name, text)
        if self.exists(spec_dir + "/plan.md"):
            self.spec_l(spec_dir)
            return
        text = self.read(light)
        if text is None:
            return
        level = frontmatter_level(text)
        if level not in SPEC_SECTIONS:
            self.add(light, 1, "spec", "front matter needs `szint: S` or `szint: M` (level L uses plan.md, requirements.md, validation.md)")
            return
        self.sections(light, text, SPEC_SECTIONS[level])
        if level == "M":
            self.branch_line(light, text, spec_dir)
            self.risk(light, text)
        body = section_lines(text, "Ellenőrzés")
        if body is not None and not any(re.match(r"^\s*- \[[ xX]\] ", ln) for _, ln in body):
            self.add(light, heading_line(text, "Ellenőrzés"), "spec", "\"Ellenőrzés\" needs `- [ ] Agent: ...` / `- [ ] Owner: ...` lines")

    def spec_l(self, spec_dir):
        plan = self.read(spec_dir + "/plan.md") or ""
        if not re.search(r"^## \d+\. csoport", plan, re.M):
            self.add(spec_dir + "/plan.md", 1, "spec", "no task group: plan.md needs `## 1. csoport: <name>` headings")
        self.branch_line(spec_dir + "/plan.md", plan, spec_dir)
        for name, wanted in L_SECTIONS.items():
            rel = spec_dir + "/" + name
            text = self.read(rel)
            if text is None:
                self.add(rel, 0, "spec", "missing: a level L spec has plan.md, requirements.md, validation.md and validate.sh")
            else:
                self.sections(rel, text, wanted)
                if name == "requirements.md":
                    self.risk(rel, text)
        if not self.exists(spec_dir + "/validate.sh"):
            self.add(spec_dir + "/validate.sh", 0, "spec", "missing: a level L spec has a validate.sh")

    def sections(self, rel, text, wanted):
        titles = [t for _, t in headings(text, 2)]
        for name in wanted:
            if not any(t == name or t.startswith(name + " ") for t in titles):
                self.add(rel, 0, "spec", "missing section `## " + name + "`")

    def risk(self, rel, text):
        body = section_lines(text, "Kockázat és visszaút")
        if body is None:
            return  # the missing section is reported by sections()
        line = heading_line(text, "Kockázat és visszaút")
        for field, values in RISK_FIELDS:
            pattern = r"^- " + field + r": (" + "|".join(values) + r")\b"
            if not any(re.match(pattern, ln) for _, ln in body):
                self.add(rel, line, "spec", "\"Kockázat és visszaút\" needs `- " + field + ": " + " | ".join(values) + ": <why>`")

    def branch_line(self, rel, text, spec_dir):
        m = re.search(r"^Branch:\s*`?([^\s`]+)`?\s*$", text, re.M)
        if not m:
            self.add(rel, 0, "spec", "missing `Branch: <branch>` line")
            return
        folder = os.path.basename(spec_dir)
        if not re.match(r"^\d{4}-\d{2}-\d{2}-" + re.escape(guard.branch_slug(m.group(1))) + "$", folder):
            line = text[: m.start()].count("\n") + 1
            self.add(rel, line, "spec", "Branch " + m.group(1) + " does not match the folder " + folder + " (the slug is the branch name's last part)")

    def decisions(self, rel, text):
        current = decision_bullets(text)
        for line, bullet in current:
            n = bullet.count("döntött:")
            if n != 1 or not DECIDED.search(bullet):
                why = "more than one decider: split it into one bullet per decider" if n > 1 else \
                    "needs `(döntött: owner | agent, YYYY-MM-DD)`"
                self.add(rel, line, "decisions", why + ": " + short(bullet))
            if "(felváltva" in bullet and not SUPERSEDED_OK.search(bullet):
                self.add(rel, line, "decisions", "write the mark as `(felváltva YYYY-MM-DD, lásd ...)`: " + short(bullet))
        old = self.base_text(rel)
        if old is None:
            return
        kept = {normal(b) for _, b in current}
        for _, bullet in decision_bullets(old):
            if normal(bullet) not in kept:
                self.add(
                    rel, 0, "decisions",
                    "a decision on " + self.base + " was deleted or reworded; keep it and mark it "
                    "`(felváltva YYYY-MM-DD, lásd ...)` instead: " + short(bullet),
                )

    def calibration(self, rel, text, final):
        body = section_lines(text, "Kalibrálás")
        subsections = []
        for line, ln in body or []:
            if ln.startswith("### "):
                subsections.append((line, ln[4:].strip(), []))
            elif subsections and re.match(r"^- [^:]+:", ln):
                subsections[-1][2].append(ln[2:].split(":", 1)[0].strip())
        for line, title, fields in subsections:
            if [f for f in fields if f in CALIBRATION_FIELDS] != list(CALIBRATION_FIELDS):
                self.add(rel, line, "calibration", "subsection `" + title + "` needs " + ", ".join(CALIBRATION_FIELDS) + " in this order")
        if final and not subsections:
            for line, bullet in decision_bullets(text):
                if "kalibrálandó" in bullet.lower():
                    self.add(rel, line, "calibration", "a kalibrálandó value has no measured result under `## Kalibrálás`: " + short(bullet))

    def coverage(self, spec_dir):
        script = self.read(spec_dir + "/validate.sh")
        if script is None:
            return
        ids = set()
        for ln in script.splitlines():
            if not ln.lstrip().startswith("#"):
                ids.update(CHECK_ID.findall(ln))
        for name, section, agent_only in (("validation.md", "Automatikus", False), (guard.LIGHT_SPEC, "Ellenőrzés", True)):
            rel = spec_dir + "/" + name
            text = self.read(rel)
            if text is None:
                continue
            for line, ln in section_lines(text, section, prefix=True) or []:
                m = re.match(r"^- \[[ xX]\] (.*)$", ln)
                if not m or (agent_only and not m.group(1).startswith("Agent:")) or PROBE_WORDS.search(ln):
                    continue
                if not any(re.search(r"(?<![\w.-])" + re.escape(i) + r"(?![\w-])", ln) for i in ids):
                    self.add(rel, line, "coverage", "name the validate.sh check ID that covers this (`check <ID> ...`): " + short(m.group(1)))

    def paths(self, rel, text, in_spec):
        for i, ln in enumerate(text.splitlines(), 1):
            if DATED_SPEC.search(ln):
                self.add(rel, i, "paths", "names a dated spec folder; the archive move breaks it (validate.sh: use $SDD_DIR)")
            if in_spec and PARENTS.search(ln):
                self.add(rel, i, "paths", "takes the repo root from its own place; use `git rev-parse --show-toplevel`")

    def shell(self, rel):
        path = os.path.join(self.root, rel)
        if self.staged:
            text = self.read(rel)
            if text is None:
                return
            out = subprocess.run(["bash", "-n"], input=text, capture_output=True, text=True)
        else:
            out = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        if out.returncode != 0:
            self.add(rel, 0, "shell", "bash -n: " + out.stderr.strip().splitlines()[-1])
            return
        if shutil.which("shellcheck"):
            out = subprocess.run(["shellcheck", "-f", "gcc", path], capture_output=True, text=True, cwd=self.root)
            for ln in out.stdout.splitlines():
                m = re.match(r"^[^:]+:(\d+):\d+: (.*)$", ln)
                if m:
                    self.add(rel, int(m.group(1)), "shell", "shellcheck: " + m.group(2))
        else:
            print("sdd_lint: shellcheck is not installed; " + rel + " got only `bash -n`", file=sys.stderr)

    def backlog(self, rel, text):
        state, line = backlog_status(text)
        if state is None:
            self.add(rel, line, "backlog", "needs a status line near the top: `Állapot: "
                     + " | ".join(BACKLOG_STATES) + "` (then free text), so /replan can list the open items")

    def batch(self, rel, text):
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        meta = dict(re.findall(r"^(\w+):\s*(.*?)\s*$", m.group(1), re.M)) if m else {}
        checks = (
            ("koteg", r"[a-z0-9-]+"), ("datum", r"\d{4}-\d{2}-\d{2}"),
            ("idokeret", r"\d{1,2}:\d{2}"), ("artifact", r"igen|nem"),
        )
        for key, pattern in checks:
            if not re.fullmatch(pattern, meta.get(key, "")):
                self.add(rel, 1, "batch", "front matter needs `" + key + ": " + pattern.replace("\\", "") + "`")
        rows = guard.batch_rows(text)
        header = batch_header(text)
        if header is None:
            self.add(rel, 0, "batch", "no feature table under `## " + guard.BATCH_SECTION + "`")
            return
        missing = [c for c in BATCH_COLUMNS if c not in header]
        if missing:
            self.add(rel, 0, "batch", "the feature table lacks the column(s) " + ", ".join(missing))
            return
        branches = {r["branch"] for r in rows}
        for r in rows:
            who = r["branch"] + ": "
            if r["fokozat"] not in ("S", "M", "L"):
                self.add(rel, 0, "batch", who + "Fokozat is S, M or L")
            if r["függ"] != "-" and r["függ"] not in branches:
                self.add(rel, 0, "batch", who + "depends on " + r["függ"] + ", which is not in the batch")
            if not r["worktree"].startswith(".claude/worktrees/"):
                self.add(rel, 0, "batch", who + "the worktree must be under .claude/worktrees/ (the guard sees only the project)")
            if r["auth/biztonság"] not in ("igen", "nem"):
                self.add(rel, 0, "batch", who + "Auth/biztonság is `igen` or `nem` (an auth or security feature gets a mandatory deep review)")
            if r["becslés"] in ("", "?"):
                self.add(rel, 0, "batch", who + "fill in Becslés (the time estimate)")
            if r["állapot"] not in BATCH_STATES:
                self.add(rel, 0, "batch", who + "Állapot is one of " + ", ".join(BATCH_STATES))

    def size(self, rel):
        text = self.read(rel)
        if text is None:
            return
        limit = dict(SIZE_LIMITS).get(rel)
        if limit is None and re.match(r"^\.claude/skills/[^/]+/SKILL\.md$", rel):
            limit = SKILL_LIMIT
        n = len(text.splitlines())
        if limit and n > limit:
            self.add(rel, n, "size", str(n) + " lines, the limit is " + str(limit) + ": move step details to a reference file")

    def dangling(self, spec_dir):
        changed = (self.git("diff", "--name-only", self.since) or "").splitlines()
        changed += (self.git("ls-files", "--others", "--exclude-standard") or "").splitlines()
        files = {f for f in changed if f.endswith(".md") and not f.startswith(DANGLING_SKIP) and os.path.basename(f) != "CHANGELOG.md"}
        if spec_dir:
            files.update(f for f in (self.git("ls-files", "-co", "--exclude-standard", spec_dir) or "").splitlines() if f.endswith(".md"))
        for rel in sorted(files):
            text = self.read(rel)
            for i, ln in enumerate((text or "").splitlines(), 1):
                for token in BACKTICK.findall(ln):
                    target = self.missing_path(rel, token)
                    if target:
                        self.add(rel, i, "dangling", "`" + token + "` does not exist")
        moved = (self.git("diff", "--name-status", "-M", self.since) or "").splitlines()
        gone = []
        for ln in moved:
            parts = ln.split("\t")
            if parts[0].startswith(("D", "R")) and len(parts) >= 2:
                gone.append((parts[1], parts[2] if len(parts) > 2 else None))
        if not gone:
            return
        tracked = [f for f in (self.git("ls-files", "*.md") or "").splitlines()
                   if not f.startswith(DANGLING_SKIP) and os.path.basename(f) != "CHANGELOG.md"]
        for rel in tracked:
            text = self.read(rel) or ""
            for old, new in gone:
                if old.startswith(DANGLING_SKIP) or "`" + old not in text:
                    continue
                for i, ln in enumerate(text.splitlines(), 1):
                    if re.search(r"`" + re.escape(old) + r"(?:[`#]|:\d)", ln):
                        self.add(rel, i, "dangling", "`" + old + "` was " + ("renamed to `" + new + "`" if new else "deleted") + " on this branch")

    def missing_path(self, rel, token):
        """True if token looks like a repo path whose first directory exists but the path does not."""
        token = token.split("#", 1)[0].rstrip("/")
        if "/" not in token or token.startswith(("/", "-", "http:", "https:")) or NOT_A_PATH.search(token) or "..." in token:
            return False
        looks_like_repo_path = False
        for base in (self.root, os.path.dirname(os.path.join(self.root, rel))):
            full = os.path.normpath(os.path.join(base, token))
            if os.path.exists(full):
                return False
            first = os.path.normpath(os.path.join(base, token.split("/")[0]))
            if first != base and os.path.isdir(first) and guard.inside(full, self.root):
                looks_like_repo_path = True
        return looks_like_repo_path

    # -- modes

    def branch_spec_dir(self):
        """The guard's spec folder, or an incomplete one (some L files only) for this branch."""
        if not self.branch or self.branch in guard.MAIN_BRANCHES:
            return None
        found = guard.find_spec_dir(self.root, self.branch)
        if found:
            return found
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}-" + re.escape(guard.branch_slug(self.branch)) + "$")
        try:
            names = sorted(os.listdir(os.path.join(self.root, "Plans")), reverse=True)
        except OSError:
            return None
        for name in names:
            if pattern.match(name) and any(os.path.isfile(os.path.join(self.root, "Plans", name, f)) for f in guard.SPEC_FILES):
                return "Plans/" + name
        return None

    def run_branch(self, final):
        spec_dir = self.branch_spec_dir()
        if spec_dir:
            self.spec_folder(spec_dir, final)
        for rel in [r for r, _ in SIZE_LIMITS] + self.skill_files():
            self.size(rel)
        for rel in backlog_files(self.root):
            self.backlog(rel, self.read(rel) or "")
        if final:
            self.dangling(spec_dir)

    def spec_folder(self, spec_dir, final=False):
        self.spec(spec_dir)
        for name in (guard.LIGHT_SPEC, "requirements.md"):
            rel = spec_dir + "/" + name
            text = self.read(rel)
            if text is not None:
                self.decisions(rel, text)
                self.calibration(rel, text, final)
        self.coverage(spec_dir)
        for rel in (self.git("ls-files", "-co", "--exclude-standard", spec_dir) or "").splitlines():
            self.spec_script(rel)

    def spec_script(self, rel):
        if rel.endswith((".sh", ".py")):
            self.paths(rel, self.read(rel) or "", in_spec=True)
        if rel.endswith(".sh"):
            self.shell(rel)

    def skill_files(self):
        out = self.git("ls-files", "-co", "--exclude-standard", ".claude/skills") or ""
        return [f for f in out.splitlines() if re.match(r"^\.claude/skills/[^/]+/SKILL\.md$", f)]

    def run_staged(self):
        out = self.git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR") or ""
        staged = [f for f in out.split("\0") if f]
        spec_dirs = set()
        for rel in staged:
            parts = rel.split("/")
            if parts[0] == "Plans" and len(parts) >= 3:
                if parts[1] not in ("done", "kotegek"):
                    spec_dirs.add("Plans/" + parts[1])
                if parts[-1] in (guard.LIGHT_SPEC, "requirements.md"):
                    self.decisions(rel, self.read(rel) or "")
                self.spec_script(rel)
            elif not guard.is_free(rel):
                self.paths(rel, self.read(rel) or "", in_spec=False)
            if is_backlog_item(rel):
                self.backlog(rel, self.read(rel) or "")
            if BATCH_ITEM.match(rel):
                self.batch(rel, self.read(rel) or "")
            if rel in dict(SIZE_LIMITS) or re.match(r"^\.claude/skills/[^/]+/SKILL\.md$", rel):
                self.size(rel)
        for spec_dir in sorted(spec_dirs):
            if self.exists(spec_dir + "/" + guard.LIGHT_SPEC) or self.exists(spec_dir + "/plan.md"):
                self.spec(spec_dir)
                for name in (guard.LIGHT_SPEC, "requirements.md"):
                    text = self.read(spec_dir + "/" + name)
                    if text is not None:
                        self.calibration(spec_dir + "/" + name, text, False)
                self.coverage(spec_dir)


def batch_header(text):
    """The lower-cased column names of the batch file's feature table, or None (rows may come later)."""
    section = section_lines(text, guard.BATCH_SECTION) or []
    for _, line in section:
        if line.strip().startswith("|"):
            return [c.strip().lower() for c in line.strip().strip("|").split("|")]
    return None


# -- backlog


def is_backlog_item(rel):
    return bool(BACKLOG_ITEM.match(rel)) and os.path.basename(rel) != "README.md"


def backlog_files(root):
    folder = os.path.join(root, "specs", "backlog")
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return []
    return [r for r in ("specs/backlog/" + n for n in names) if is_backlog_item(r) and os.path.isfile(os.path.join(root, r))]


def backlog_status(text):
    """(state, line) of the first `Állapot:` line in the first 20 lines; state None if missing or not a known state."""
    for i, ln in enumerate(text.splitlines()[:20], 1):
        m = re.match(r"^Állapot:\s*(\S+?)(?=[:,.\s]|$)", ln)
        if m:
            word = m.group(1).lower()
            return (word if word in BACKLOG_STATES else None), i
    return None, 0


def open_backlog(root):
    """(path, title, has_status) of every backlog item that is open or has no valid status line."""
    out = []
    for rel in backlog_files(root):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        state, _ = backlog_status(text)
        if state in (None, "nyitott"):
            title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), os.path.basename(rel))
            out.append((rel, title, state is not None))
    return out


# -- Markdown helpers


def frontmatter_level(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if m:
        lv = re.search(r"^\s*szint:\s*([A-Za-z])\s*$", m.group(1), re.M)
        if lv:
            return lv.group(1).upper()
    return None


def headings(text, level):
    marks = "#" * level + " "
    fence = False
    for i, ln in enumerate(text.splitlines(), 1):
        if ln.startswith("```"):
            fence = not fence
        elif not fence and ln.startswith(marks):
            yield i, ln[len(marks):].strip()


def heading_line(text, title):
    return next((i for i, t in headings(text, 2) if t.startswith(title)), 0)


def section_lines(text, title, prefix=False):
    """(line number, line) pairs of the `## title` section (title is a prefix with prefix=True), or None."""
    lines = text.splitlines()
    out, inside, fence, found = [], False, False, False
    for i, ln in enumerate(lines, 1):
        if ln.startswith("```"):
            fence = not fence
        if not fence and ln.startswith("## "):
            t = ln[3:].strip()
            inside = t.startswith(title) if prefix else (t == title or t.startswith(title + " "))
            found = found or inside
            continue
        if inside and not fence:
            out.append((i, ln))
    return out if found else None


def decision_bullets(text):
    """(line, joined text) of each top-level bullet under every `## Döntések`, with its continuation lines."""
    body = section_lines(text, "Döntések") or []
    bullets = []
    in_comment = False
    open_bullet = False  # the previous line belongs to the current bullet
    for line, ln in body:
        if in_comment or "<!--" in ln:
            in_comment = "-->" not in ln
            continue
        if ln.startswith("- "):
            bullets.append([line, ln[2:].strip()])
            open_bullet = True
        elif not ln.strip() or re.match(r"^\s+- ", ln):
            open_bullet = False  # a blank line or a sub-bullet ends the bullet's own text
        elif bullets and open_bullet:
            bullets[-1][1] += " " + ln.strip()  # a wrapped line, indented or lazy
    return [(line, b) for line, b in bullets]


def normal(bullet):
    return " ".join(SUPERSEDED.sub("", bullet).split())


def short(text, n=90):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 3] + "..."


def main(argv):
    staged = "--staged" in argv
    final = "--final" in argv
    base = argv[argv.index("--base") + 1] if "--base" in argv and argv.index("--base") + 1 < len(argv) else None
    unknown = [a for a in argv if a.startswith("-") and a not in ("--staged", "--final", "--base")]
    if unknown or (staged and final):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if out.returncode != 0:
        print("sdd_lint: not inside a git repository", file=sys.stderr)
        return 2
    lint = Lint(out.stdout.strip(), staged=staged, base=base)
    if staged:
        lint.run_staged()
    else:
        lint.run_branch(final)
    for rel, line, check, message in lint.findings:
        print(rel + ":" + str(line) + ": [" + check + "] " + message)
    if lint.findings:
        print("sdd_lint: " + str(len(lint.findings)) + " finding(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
