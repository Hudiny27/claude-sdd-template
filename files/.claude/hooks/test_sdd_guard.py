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
        self.env = {**os.environ, **GIT_ENV, "CLAUDE_PROJECT_DIR": self.dir}
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

    def feature(self, branch="feature/phase-1-hello", spec=True):
        self.git("checkout", "-q", "-b", branch)
        if spec:
            slug = branch.rsplit("/", 1)[-1]
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


class PreCommit(Repo):
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

    def test_squash_merge_to_main_ok(self):
        self.feature()
        self.assertEqual(self.commit("src/app.ts").returncode, 0)
        self.git("checkout", "-q", "main")
        self.git("merge", "--squash", "feature/phase-1-hello")
        self.assertEqual(self.git("commit", "-q", "-m", "feat: hello", check=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
