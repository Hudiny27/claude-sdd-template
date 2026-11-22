"""Helpers for the tests of files/.claude/lib: a throwaway git repo and a script runner."""

import os
import subprocess
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "files" / ".claude" / "lib"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
    "GIT_CONFIG_NOSYSTEM": "1",
}


class Repo:
    """A git repo under tmp_path; scripts run with TMPDIR inside tmp_path."""

    def __init__(self, tmp_path):
        self.path = tmp_path / "repo"
        self.tmp = tmp_path / "tmp"
        self.tmp.mkdir()
        self.path.mkdir()
        self.env = dict(os.environ, TMPDIR=str(self.tmp), HOME=str(tmp_path), **GIT_ENV)
        self.git("init", "-q", "-b", "main")
        self.write("README.md", "readme\n")
        self.write("src/app.py", "print('v1')\n")
        self.commit("init")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.path, env=self.env, check=True,
            capture_output=True, text=True,
        ).stdout

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)

    def run(self, body, *args, lib="sdd_check.sh", init=True, timeout=60):
        """Write body as Plans/x/validate.sh after the library header and run it from /."""
        header = f'source "{LIB / lib}"\n'
        if init:
            header += 'sdd_init "$@"\n'
        script = self.write("Plans/x/validate.sh", header + body)
        return subprocess.run(
            ["bash", str(script), *args], cwd="/", env=self.env,
            capture_output=True, text=True, timeout=timeout,
        )

    def leftovers(self):
        return sorted(p.name for p in self.tmp.iterdir())


def alive(pid):
    """True if pid exists and is not a zombie."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except FileNotFoundError:
        return False
    return stat.rsplit(")", 1)[1].split()[0] != "Z"
