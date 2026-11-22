"""Tests for the SDD guard and the git pre-commit hook.

Run: python3 -m unittest discover -s .claude/hooks -p 'test_*.py'
Each test builds a throwaway git repository; nothing outside it is touched.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "sdd_guard.py")
PRE_COMMIT = os.path.join(HERE, "..", "..", ".githooks", "pre-commit")
SESSION = "test-session"
GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


class Repo(unittest.TestCase):
    def setUp(self):
        self.dir = os.path.realpath(tempfile.mkdtemp(prefix="sdd-test-"))
        self.addCleanup(shutil.rmtree, self.dir)
        self.env = {
            **os.environ,
            **GIT_ENV,
            "CLAUDE_PROJECT_DIR": self.dir,
            # Keep the real ~/.claude/templates out of the status under test.
            "SDD_TEMPLATE_DIR": os.path.join(self.dir, "no-template"),
        }
        self.git("init", "-q", "-b", "main")
        self.write(".gitignore", ".claude/.sdd-*\n*.log\n")
        self.write("README.md", "# test\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")

    # -- helpers

    def git(self, *args, check=True):
        return subprocess.run(["git", "-C", self.dir, *args], env=self.env, capture_output=True, text=True, check=check)

    def write(self, rel, text="x\n"):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def hook(self, mode, payload):
        payload = {"session_id": SESSION, "cwd": self.dir, **payload}
        out = subprocess.run(
            [sys.executable, GUARD, mode], input=json.dumps(payload), env=self.env, capture_output=True, text=True, check=True
        )
        return out.stdout

    def denied(self, tool, tool_input):
        out = self.hook("pretool", {"tool_name": tool, "tool_input": tool_input})
        return bool(out.strip()) and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"

    def edit(self, rel):
        return self.denied("Write", {"file_path": os.path.join(self.dir, rel), "content": "x"})

    def bash(self, command):
        return self.denied("Bash", {"command": command})

    def say(self, text):
        return self.hook("prompt", {"prompt": text})

    def constitution(self):
        for rel in ("specs/mission.md", "specs/tech-stack.md"):
            self.write(rel)
        self.write("specs/roadmap.md", "# Roadmap\n\n- [ ] Phase 1 — Hello\n- [ ] Phase 2 — More\n")

    def feature(self, branch="feature/phase-1-hello", spec=True, level=None):
        self.git("checkout", "-q", "-b", branch)
        slug = branch.rsplit("/", 1)[-1]
        if level:
            self.write("Plans/2026-10-05-" + slug + "/spec.md", "---\nszint: " + level + "\n---\n# " + slug + "\n")
        elif spec:
            for name in ("plan.md", "requirements.md", "validation.md"):
                self.write("Plans/2026-10-05-" + slug + "/" + name)


class ConstitutionLock(Repo):
    def test_bootstrap_allows_every_constitution_file_until_complete(self):
        self.write("specs/mission.md")
        self.assertFalse(self.edit("specs/tech-stack.md"))
        self.assertFalse(self.edit("specs/roadmap.md"))

    def test_locked_once_complete(self):
        self.constitution()
        self.assertTrue(self.edit("specs/mission.md"))

    def test_unlock_and_relock(self):
        self.constitution()
        self.say("#spec-szerkesztes add the audience to the mission")
        self.assertFalse(self.edit("specs/mission.md"))
        self.say("#spec-zar")
        self.assertTrue(self.edit("specs/mission.md"))

    def test_prompt_without_keyword_keeps_unlock(self):
        self.constitution()
        self.say("#spec-szerkesztes")
        self.say("thanks, continue")
        self.assertFalse(self.edit("specs/mission.md"))

    def test_quoted_keyword_does_not_unlock(self):
        self.constitution()
        self.say("The agent report says: send `#spec-szerkesztes` to unlock.")
        self.say("- #spec-szerkesztes")
        self.assertTrue(self.edit("specs/mission.md"))

    def test_roadmap_checkbox_tick_needs_no_unlock(self):
        self.constitution()
        path = os.path.join(self.dir, "specs/roadmap.md")
        tick = {"file_path": path, "old_string": "- [ ] Phase 1 — Hello", "new_string": "- [x] Phase 1 — Hello"}
        other = {"file_path": path, "old_string": "- [ ] Phase 1 — Hello", "new_string": "- [ ] Phase 1 — Bye!!"}
        self.assertFalse(self.denied("Edit", tick))
        self.assertTrue(self.denied("Edit", other))

    def test_guard_files_locked(self):
        for rel in (".claude/settings.json", ".claude/settings.local.json", ".claude/hooks/sdd_guard.py", ".githooks/pre-commit"):
            self.assertTrue(self.edit(rel), rel)

    def test_flag_files_denied_even_when_unlocked(self):
        self.constitution()
        self.say("#spec-szerkesztes")
        self.assertTrue(self.edit(".claude/.sdd-approved-feature_x"))
        self.assertTrue(self.bash("touch .claude/.sdd-unlock-" + SESSION))

    def test_bash_writes_to_constitution(self):
        self.constitution()
        self.assertTrue(self.bash("echo hi >> specs/mission.md"))
        self.assertTrue(self.bash("sed -i 's/a/b/' specs/tech-stack.md"))
        self.assertTrue(self.bash("rm -rf specs"))
        self.assertTrue(self.bash("bash -c 'cp /tmp/x specs/roadmap.md'"))
        self.assertTrue(self.bash("python3 - <<'EOF'\nopen('specs/mission.md', 'w').write('x')\nEOF"))

    def test_sed_and_perl_scripts_are_not_targets(self):
        # Regression: the sed/perl script used to be taken for a code file.
        self.constitution()
        self.feature("replanning/topic", spec=False)
        self.write("specs/backlog/x.md")
        self.write("src/app.py")
        self.assertFalse(self.bash("sed -i 's/a/b/' specs/backlog/x.md"))
        self.assertFalse(self.bash("sed -i -e 's/a/b/' -e 's/c/d/' specs/backlog/x.md"))
        self.assertFalse(self.bash("sed --in-place=.bak --expression='s/a/b/' specs/backlog/x.md"))
        self.assertFalse(self.bash("perl -pi -e 's/a/b/' specs/backlog/x.md"))
        self.assertTrue(self.bash("sed -i 's/a/b/' src/app.py"))
        self.assertTrue(self.bash("sed -i -e 's/a/b/' src/app.py"))
        self.assertTrue(self.bash("sed -i -f fix.sed src/app.py"))
        self.assertTrue(self.bash("perl -pi -e 's/a/b/' src/app.py"))
        self.assertTrue(self.bash("sed -i 's/a/b/' specs/tech-stack.md"))

    def test_bash_reads_are_free(self):
        self.constitution()
        self.assertFalse(self.bash("cat specs/mission.md && grep -n x specs/roadmap.md"))
        self.assertFalse(self.bash("git add specs && git commit -m 'docs(specs): update specs/mission.md'"))

    def test_interpreter_check_is_per_line(self):
        self.constitution()
        script = "python3 - <<'EOF'\n# see specs/mission.md\nopen('Plans/README.md', 'w').write('x')\nEOF"
        self.assertFalse(self.bash(script))

    def test_git_discard_of_dirty_constitution(self):
        self.constitution()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "constitution")
        self.assertFalse(self.bash("git stash"))
        self.write("specs/mission.md", "edited by the owner\n")
        self.assertTrue(self.bash("git checkout -- specs/mission.md"))
        self.assertTrue(self.bash("git stash"))


class CodeGate(Repo):
    def setUp(self):
        super().setUp()
        self.constitution()

    def test_code_on_main_denied(self):
        self.assertTrue(self.edit("src/app.ts"))
        self.assertTrue(self.bash("cat > src/app.ts <<'EOF'\nexport {}\nEOF"))

    def test_docs_and_ignored_files_free_on_main(self):
        for rel in ("Plans/README.md", "docs/notes.txt", "NOTES.md", ".gitignore", "specs/backlog/idea.md"):
            self.assertFalse(self.edit(rel), rel)
        self.assertFalse(self.bash("npm test > test.log"))

    def test_feature_branch_without_spec_denied(self):
        self.feature(spec=False)
        self.assertTrue(self.edit("src/app.ts"))

    def test_variables_set_in_the_command_are_resolved(self):
        # Regression: "$P/x" was resolved against the repo, so a write outside it was refused.
        self.feature("replanning/topic", spec=False)
        outside = os.path.realpath(tempfile.mkdtemp(prefix="sdd-out-"))
        self.addCleanup(shutil.rmtree, outside)
        self.assertFalse(self.bash("P=" + outside + "; mkdir -p \"$P/s\" && cat > \"$P/s/a.json\" <<'EOF'\n{}\nEOF"))
        self.assertFalse(self.bash("export P=" + outside + " && echo x > \"${P}/a.json\""))
        self.assertFalse(self.bash("D=" + outside + "; F=$D/a.json; echo x > $F"))
        self.assertTrue(self.bash("P=src; echo x > \"$P/app.py\""))
        self.assertTrue(self.bash("echo x > \"$UNSET_IN_THIS_COMMAND/app.py\""))

    def test_unapproved_spec_denied(self):
        self.feature()
        self.assertTrue(self.edit("src/app.ts"))

    def test_approved_spec_allows_code(self):
        self.feature()
        out = self.say("#spec-ok looks good")
        self.assertIn("approved", out)
        self.assertFalse(self.edit("src/app.ts"))
        self.assertFalse(self.bash("echo 'x' > src/util.ts"))

    def test_approval_is_per_branch(self):
        self.feature()
        self.say("#spec-ok")
        self.git("checkout", "-q", "main")
        self.assertTrue(self.edit("src/app.ts"))
        self.feature("feature/phase-2-more")
        self.assertTrue(self.edit("src/app.ts"))

    def test_approve_refused_without_spec_or_on_main(self):
        self.assertIn("ignored", self.say("#spec-ok"))
        self.feature(spec=False)
        self.assertIn("ignored", self.say("#spec-ok"))
        self.assertTrue(self.edit("src/app.ts"))

    def test_light_spec_needs_approval_then_allows_code(self):
        for level in ("S", "M"):
            self.git("checkout", "-q", "main")
            self.feature("feature/" + level.lower() + "-task", level=level)
            self.assertTrue(self.edit("src/app.ts"), level)
            self.assertIn("approved", self.say("#spec-ok"))
            self.assertFalse(self.edit("src/app.ts"), level)

    def test_rising_level_needs_a_new_approval(self):
        self.feature(level="S")
        self.say("#spec-ok")
        self.assertFalse(self.edit("src/app.ts"))
        self.write("Plans/2026-10-05-phase-1-hello/spec.md", "---\nszint: M\n---\n# grown\n")
        self.assertTrue(self.edit("src/app.ts"))
        self.assertIn("NOT approved", self.hook("session", {}))
        self.say("#spec-ok")
        self.assertFalse(self.edit("src/app.ts"))
        self.write("Plans/2026-10-05-phase-1-hello/spec.md", "---\nszint: S\n---\n# smaller\n")
        self.assertFalse(self.edit("src/app.ts"))

    def test_map_alone_is_not_a_spec(self):
        self.feature(spec=False)
        self.write("Plans/2026-10-05-phase-1-hello/terkep.md", "---\nszint: F\n---\n# map\n")
        self.assertIn("ignored", self.say("#spec-ok"))
        self.assertTrue(self.edit("src/app.ts"))

    def test_session_status_names_the_level(self):
        self.feature(level="S")
        self.assertIn("level S", self.hook("session", {}))
        self.git("checkout", "-q", "main")
        self.feature("feature/phase-2-more")
        self.assertIn("level L", self.hook("session", {}))

    def template(self):
        tpl = os.path.realpath(tempfile.mkdtemp(prefix="sdd-tpl-"))
        self.addCleanup(shutil.rmtree, tpl)
        for rel, text in (
            ("CLAUDE.md", "# rules v2\n"),
            ("Plans/README.md", "plans\n"),
            (".claude/skills/replan/SKILL.md", "replan v2\n"),
            (".github/workflows/sdd-check.yml", "ci\n"),
        ):
            os.makedirs(os.path.dirname(os.path.join(tpl, rel)), exist_ok=True)
            with open(os.path.join(tpl, rel), "w", encoding="utf-8") as fh:
                fh.write(text)
        self.env["SDD_TEMPLATE_DIR"] = tpl
        return tpl

    def test_session_status_names_template_drift(self):
        self.template()
        self.write("CLAUDE.md", "# rules v1\n")
        self.write("Plans/README.md", "plans\n")
        out = self.hook("session", {})
        self.assertIn("Template:", out)
        self.assertIn("CLAUDE.md", out)
        self.assertIn(".claude/skills/replan/SKILL.md", out)
        self.assertNotIn("Plans/README.md", out)
        # The CI workflow is optional: a project without it is not drift.
        self.assertNotIn("sdd-check.yml", out)

    def test_no_template_line_when_in_sync(self):
        tpl = self.template()
        for rel in ("CLAUDE.md", "Plans/README.md", ".claude/skills/replan/SKILL.md"):
            os.makedirs(os.path.dirname(os.path.join(self.dir, rel)) or self.dir, exist_ok=True)
            shutil.copy(os.path.join(tpl, rel), os.path.join(self.dir, rel))
        for rel in ("specs/README.md", ".claude/hooks/sdd_guard.py", ".githooks/pre-commit"):
            os.makedirs(os.path.dirname(os.path.join(tpl, rel)), exist_ok=True)
            self.write(rel, "same\n")
            shutil.copy(os.path.join(self.dir, rel), os.path.join(tpl, rel))
        self.assertNotIn("Template:", self.hook("session", {}))

    def test_rules_beside_a_foreign_claude_md_are_compared(self):
        self.template()
        self.write("CLAUDE.md", "# the project's own notes\n@CLAUDE.sdd.md\n")
        self.write("CLAUDE.sdd.md", "# rules v2\n")
        out = self.hook("session", {})
        self.assertNotIn("CLAUDE.md,", out)
        self.assertNotIn("CLAUDE.sdd.md", out)

    def test_drift_covers_reference_files_and_libraries_but_not_project_files(self):
        tpl = self.template()
        for rel in (".claude/skills/feature-spec/probe.md", ".claude/lib/sdd_check.sh", ".claude/project.md", ".claude/settings.json", "gitignore"):
            os.makedirs(os.path.dirname(os.path.join(tpl, rel)) or tpl, exist_ok=True)
            with open(os.path.join(tpl, rel), "w", encoding="utf-8") as fh:
                fh.write("template\n")
        self.write(".claude/project.md", "the project's own\n")
        self.write(".claude/settings.json", "{}\n")
        out = self.hook("session", {})
        self.assertIn("probe.md", out)
        self.assertIn("sdd_check.sh", out)
        self.assertNotIn("project.md", out)
        self.assertNotIn("settings.json", out)
        self.assertNotIn("gitignore", out)

    def test_open_manual_checks_of_archived_features_are_counted(self):
        self.write(
            "Plans/done/2026-10-01-a/validation.md",
            "# V\n\n## Automatikus ellenőrzések\n- [ ] `x`: y\n\n## Kézi ellenőrzések (az owner futtatja)\n- [ ] look at it\n- [x] done\n",
        )
        self.write("Plans/done/2026-10-02-b/spec.md", "---\nszint: M\n---\n## Ellenőrzés\n- [ ] Agent: x\n- [ ] Owner: open the page\n")
        self.assertIn("Open manual checks: 2", self.hook("session", {}))

    def test_no_manual_check_line_when_all_closed(self):
        self.write("Plans/done/2026-10-02-b/spec.md", "## Ellenőrzés\n- [x] Owner: open the page\n")
        self.assertNotIn("manual checks", self.hook("session", {}))

    def test_no_template_dir_no_template_line(self):
        self.assertNotIn("Template:", self.hook("session", {}))

    def test_outside_project_is_not_gated(self):
        self.assertFalse(self.denied("Write", {"file_path": os.path.join(tempfile.gettempdir(), "sdd-elsewhere.txt")}))

    def test_git_hook_bypass_denied(self):
        self.assertTrue(self.bash("git commit --no-verify -m x"))
        self.assertTrue(self.bash("git commit -anm x"))
        self.assertTrue(self.bash("git config core.hooksPath /dev/null"))
        self.assertTrue(self.bash("git -c core.hooksPath=x commit -m y"))
        self.assertFalse(self.bash("git checkout -b feature/phase-1-hello"))
        self.assertFalse(self.bash("git commit -m 'feat: x'"))

    def test_session_status(self):
        out = self.hook("session", {})
        self.assertIn("Branch: main", out)
        self.assertIn("Phase 1", out)
        self.feature()
        self.assertIn("NOT approved", self.hook("session", {}))

    def workflow_log(self, entries, reviewed_before=0):
        lines = ["# Workflow log", "", "Format: `- YYYY-MM-DD | file | rule | origin`", ""]
        lines += ["- 2026-01-%02d | CLAUDE.md | old rule | f" % (i + 1) for i in range(reviewed_before)]
        if reviewed_before:
            lines.append("review: 2026-02-01")
        lines += ["- 2026-03-%02d | CLAUDE.md | rule %d | f" % (i + 1, i) for i in range(entries)]
        self.write(".claude/workflow-log.md", "\n".join(lines) + "\n")

    def test_workflow_log_counts_entries_since_the_last_review(self):
        self.workflow_log(3, reviewed_before=12)
        out = self.hook("session", {})
        self.assertIn("Workflow log: 3/10", out)
        self.assertNotIn("time to review", out)

    def test_workflow_log_asks_for_a_review_at_ten(self):
        self.workflow_log(10)
        out = self.hook("session", {})
        self.assertIn("time to review", out)
        # The review tidies up locally; the template has its own gate.
        self.assertIn("turn into code or a check", out)
        self.assertNotIn("template, keep local", out)

    def test_no_workflow_line_without_entries(self):
        self.assertNotIn("Workflow log", self.hook("session", {}))
        self.workflow_log(0, reviewed_before=4)
        self.assertNotIn("Workflow log", self.hook("session", {}))


class CommandBans(Repo):
    """Shell habits that caused trouble in earlier projects; each denial names the right way."""

    def setUp(self):
        super().setUp()
        self.constitution()

    def reason(self, command):
        out = self.hook("pretool", {"tool_name": "Bash", "tool_input": {"command": command}})
        return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"] if out.strip() else ""

    def test_git_add_everything_denied(self):
        for cmd in ("git add -A", "git add --all", "git add .", "git add ./", "git add :/", "cd src && git add -A ."):
            self.assertTrue(self.bash(cmd), cmd)
        self.assertIn("git add <file>", self.reason("git add -A"))

    def test_git_add_by_name_allowed(self):
        for cmd in ("git add src/app.py specs/backlog/x.md", "git add -p src/app.py", "git add ./src/app.py"):
            self.assertFalse(self.bash(cmd), cmd)

    def test_git_commit_all_denied(self):
        for cmd in ("git commit -a -m x", "git commit -am x", "git commit --all -m x", "git -C . commit -qam x"):
            self.assertTrue(self.bash(cmd), cmd)
        # A message that merely contains "-a" is not the flag.
        self.assertFalse(self.bash("git commit -m '-a'"))
        self.assertFalse(self.bash("git commit -m 'fix: x' --amend"))

    def test_pkill_full_denied(self):
        for cmd in ("pkill -f 'python3 -m http.server'", "pkill --full uvicorn", "sudo pkill -9f node"):
            self.assertTrue(self.bash(cmd), cmd)
        self.assertFalse(self.bash("pkill uvicorn"))
        self.assertFalse(self.bash("kill 1234"))
        self.assertIn("PID", self.reason("pkill -f x"))

    def test_roadmap_shell_write_names_the_edit_tool(self):
        self.assertIn("Edit tool", self.reason("sed -i 's/- \\[ \\]/- [x]/' specs/roadmap.md"))


class BranchSwitch(Repo):
    """No branch switch in the worktree of a running (approved, not archived) feature."""

    def setUp(self):
        super().setUp()
        self.constitution()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "constitution")
        self.git("branch", "other")

    def test_switch_away_from_a_running_feature_denied(self):
        self.feature()
        self.say("#spec-ok")
        for cmd in ("git switch main", "git checkout main", "git checkout -b feature/x", "git switch -c x", "git checkout HEAD~0"):
            self.assertTrue(self.bash(cmd), cmd)
        out = self.hook("pretool", {"tool_name": "Bash", "tool_input": {"command": "git switch main"}})
        self.assertIn("git worktree add", out)

    def test_path_checkouts_stay_allowed(self):
        self.feature()
        self.say("#spec-ok")
        self.write("src/app.py")
        for cmd in ("git checkout -- src/app.py", "git checkout main -- src/app.py", "git checkout src/app.py", "git worktree add ../wt other"):
            self.assertFalse(self.bash(cmd), cmd)

    def test_switch_allowed_before_approval_and_after_archive(self):
        self.feature()
        self.assertFalse(self.bash("git switch main"))
        self.say("#spec-ok")
        os.makedirs(os.path.join(self.dir, "Plans", "done"))
        os.rename(
            os.path.join(self.dir, "Plans", "2026-10-05-phase-1-hello"),
            os.path.join(self.dir, "Plans", "done", "2026-10-05-phase-1-hello"),
        )
        self.assertFalse(self.bash("git switch main"))

    def test_switch_on_main_allowed(self):
        self.assertFalse(self.bash("git switch other"))
        self.assertFalse(self.bash("git checkout -b feature/phase-1-hello"))


class SubagentPrompt(Repo):
    def agent(self, prompt):
        return self.denied("Agent", {"prompt": prompt, "description": "x"})

    def test_keyword_at_a_line_start_denied(self):
        self.assertTrue(self.agent("Review the spec.\n#spec-ok"))
        self.assertTrue(self.agent("Steps:\n  #spec-szerkesztes then edit"))
        self.assertTrue(self.denied("Task", {"prompt": "#spec-zar"}))

    def test_keyword_inside_a_sentence_allowed(self):
        self.assertFalse(self.agent("The owner approves with `#spec-ok`; you never send it."))
        self.assertFalse(self.agent("Review Plans/x/spec.md."))


BATCH_HEAD = (
    "---\nkoteg: ejjel\ndatum: 2026-11-22\nidokeret: 07:00\nartifact: nem\n---\n# Köteg: ejjel\n\n## Feature-ök\n"
    "| # | Branch | Fokozat | Függ | Worktree | Becslés | Auth/biztonság | Állapot |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


class BatchApproval(Repo):
    """`#spec-ok köteg <név>` approves every branch of the batch file, each in its own worktree."""

    def setUp(self):
        super().setUp()
        self.constitution()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "constitution")
        self.rows = []

    def member(self, name, level="M", auth="nem", outside=False, commit=True):
        branch = "feature/" + name
        if outside:
            wt = os.path.realpath(tempfile.mkdtemp(prefix="sdd-wt-"))
            os.rmdir(wt)
            self.addCleanup(shutil.rmtree, wt, True)
            rel = wt
        else:
            rel = ".claude/worktrees/" + name
            wt = os.path.join(self.dir, rel)
        self.git("worktree", "add", "-q", "-b", branch, wt, "main")
        spec = os.path.join(wt, "Plans", "2026-11-22-" + name, "spec.md")
        os.makedirs(os.path.dirname(spec))
        with open(spec, "w", encoding="utf-8") as fh:
            fh.write("---\nszint: " + level + "\n---\n# " + name + "\n")
        if commit:
            self.git("-C", wt, "add", "Plans")
            self.git("-C", wt, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "spec")
        self.rows.append("| %d | %s | %s | - | %s | 1 óra | %s | spec |" % (len(self.rows) + 1, branch, level, rel, auth))
        self.write("Plans/kotegek/2026-11-22-ejjel.md", BATCH_HEAD + "\n".join(self.rows) + "\n")
        return wt

    def edit_in(self, wt, rel="src/app.py"):
        return self.denied("Write", {"file_path": os.path.join(wt, rel), "content": "x"})

    def test_batch_keyword_approves_every_member(self):
        a, b = self.member("a"), self.member("b")
        self.assertTrue(self.edit_in(a))
        out = self.say("#spec-ok köteg ejjel")
        self.assertIn("feature/a", out)
        self.assertIn("feature/b", out)
        self.assertFalse(self.edit_in(a))
        self.assertFalse(self.edit_in(b))
        # The main checkout itself stays closed for code.
        self.assertTrue(self.edit("src/app.py"))

    def test_worktree_outside_the_project_is_refused(self):
        inside, outside = self.member("a"), self.member("x", outside=True)
        out = self.say("#spec-ok köteg ejjel")
        self.assertIn("outside the project", out)
        self.assertFalse(self.edit_in(inside))
        self.assertIsNone(self.approved_level("feature/x"))

    def test_auth_member_is_refused(self):
        self.member("login", auth="igen")
        out = self.say("#spec-ok köteg ejjel")
        self.assertIn("auth", out)
        self.assertIsNone(self.approved_level("feature/login"))

    def test_uncommitted_spec_is_refused(self):
        a = self.member("a", commit=False)
        out = self.say("#spec-ok köteg ejjel")
        self.assertIn("commit the spec", out)
        self.assertIsNone(self.approved_level("feature/a"))
        self.assertTrue(self.edit_in(a))

    def test_batch_file_is_written_only_in_the_main_checkout(self):
        a = self.member("a")
        self.say("#spec-ok köteg ejjel")
        self.assertTrue(self.edit_in(a, "Plans/kotegek/2026-11-22-ejjel.md"))
        self.assertTrue(self.bash("echo x >> " + os.path.join(a, "Plans/kotegek/2026-11-22-ejjel.md")))
        self.assertFalse(self.edit("Plans/kotegek/2026-11-22-ejjel.md"))

    def test_unknown_batch_approves_nothing(self):
        self.member("a")
        self.assertIn("no batch", self.say("#spec-ok köteg masik"))
        self.assertIsNone(self.approved_level("feature/a"))

    def test_rising_level_in_a_member_needs_a_new_approval(self):
        a = self.member("a", level="S")
        self.say("#spec-ok köteg ejjel")
        self.assertFalse(self.edit_in(a))
        with open(os.path.join(a, "Plans", "2026-11-22-a", "spec.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nszint: M\n---\n# grown\n")
        self.assertTrue(self.edit_in(a))

    def approved_level(self, branch):
        path = os.path.join(self.dir, ".claude", ".sdd-approved-" + branch.replace("/", "_"))
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as fh:
            return fh.read()


class PreCommitBase(Repo):
    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.dir, ".claude", "hooks"))
        os.makedirs(os.path.join(self.dir, ".githooks"))
        shutil.copy(GUARD, os.path.join(self.dir, ".claude", "hooks", "sdd_guard.py"))
        shutil.copy(PRE_COMMIT, os.path.join(self.dir, ".githooks", "pre-commit"))
        os.chmod(os.path.join(self.dir, ".githooks", "pre-commit"), 0o755)
        self.git("config", "core.hooksPath", ".githooks")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore(sdd): scaffold")

    def commit(self, *files):
        for f in files:
            self.write(f)
        self.git("add", "-A")
        return self.git("commit", "-q", "-m", "change", check=False)


class PreCommit(PreCommitBase):
    def test_docs_on_main_ok(self):
        self.assertEqual(self.commit("specs/mission.md", "Plans/README.md").returncode, 0)

    def test_code_on_main_rejected(self):
        result = self.commit("src/app.ts")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be committed on main", result.stderr)

    def test_feature_branch_needs_spec(self):
        self.feature(spec=False)
        self.assertNotEqual(self.commit("src/app.ts").returncode, 0)
        self.feature("feature/phase-2-more")
        self.assertEqual(self.commit("src/app.ts").returncode, 0)

    def test_light_spec_is_enough(self):
        self.feature("feature/quick-fix", level="S")
        self.assertEqual(self.commit("src/app.ts").returncode, 0)

    def test_squash_merge_to_main_ok(self):
        self.feature()
        self.assertEqual(self.commit("src/app.ts").returncode, 0)
        self.git("checkout", "-q", "main")
        self.git("merge", "--squash", "feature/phase-1-hello")
        self.assertEqual(self.git("commit", "-q", "-m", "feat: hello", check=False).returncode, 0)


class PreCommitLint(PreCommitBase):
    """With .claude/lib/sdd_lint.py installed, the pre-commit hook lints the staged files."""

    def setUp(self):
        super().setUp()
        lint = os.path.join(HERE, "..", "lib", "sdd_lint.py")
        os.makedirs(os.path.join(self.dir, ".claude", "lib"))
        shutil.copy(lint, os.path.join(self.dir, ".claude", "lib", "sdd_lint.py"))
        self.git("add", ".claude/lib/sdd_lint.py")
        self.git("commit", "-q", "-m", "chore(sdd): add lint")

    def test_lint_finding_blocks_the_commit(self):
        self.feature("feature/quick-fix", spec=False)
        self.write("Plans/2026-10-05-quick-fix/spec.md", "---\nszint: S\n---\n# x\n\n## Cél\nx\n")
        result = self.commit("src/app.ts")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing section `## Kész, ha`", result.stdout + result.stderr)

    def test_clean_spec_commits(self):
        self.feature("feature/quick-fix", spec=False)
        self.write(
            "Plans/2026-10-05-quick-fix/spec.md",
            "---\nszint: S\n---\n# x\n\n## Cél\nx\n\n## Kész, ha\n- x\n\n## Ellenőrzés\n- [ ] Owner: look\n",
        )
        result = self.commit("src/app.ts")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_merge_commit_is_not_linted(self):
        self.feature()  # placeholder L files that would not pass the lint
        self.git("add", "-A")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "spec")
        self.git("checkout", "-q", "main")
        self.git("merge", "--squash", "feature/phase-1-hello")
        self.assertEqual(self.git("commit", "-q", "-m", "feat: hello", check=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
