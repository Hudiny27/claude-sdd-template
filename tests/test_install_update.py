"""install.sh: a plain re-run changes nothing; --update refreshes only template-owned files."""

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "install.sh"
FILES = ROOT / "files"


def run_install(target, *flags):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        ["bash", str(INSTALL), str(target), *flags],
        capture_output=True, text=True, env=env, timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def snapshot(target):
    """Every file under target (git internals except config) with its bytes and mode."""
    state = {}
    for path in sorted(target.rglob("*")):
        rel = path.relative_to(target).as_posix()
        if rel.startswith(".git/") and rel != ".git/config":
            continue
        if path.is_file():
            state[rel] = (path.read_bytes(), path.stat().st_mode)
    return state


@pytest.fixture
def installed(tmp_path):
    target = tmp_path / "project"
    run_install(target)
    return target


def test_plain_rerun_changes_nothing(installed):
    before = snapshot(installed)
    run_install(installed)
    assert snapshot(installed) == before


def test_update_overwrites_template_files_and_keeps_extension_points(installed):
    skill = installed / ".claude/skills/replan/SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "local edit\n", encoding="utf-8")
    project_md = installed / ".claude/project.md"
    project_md.write_text("# Saját\n\nproject rule\n", encoding="utf-8")
    rule = installed / ".claude/rules/x.md"
    rule.write_text("---\npaths: ['src/**']\n---\nlocal rule\n", encoding="utf-8")

    out = run_install(installed, "--update")

    assert skill.read_bytes() == (FILES / ".claude/skills/replan/SKILL.md").read_bytes()
    assert "diff    .claude/skills/replan/SKILL.md" in out
    assert project_md.read_text(encoding="utf-8") == "# Saját\n\nproject rule\n"
    assert rule.read_text(encoding="utf-8") == "---\npaths: ['src/**']\n---\nlocal rule\n"


def test_update_without_changes_reports_nothing_to_update(installed):
    before = snapshot(installed)
    out = run_install(installed, "--update")
    assert "nothing: the template-owned files match" in out
    assert snapshot(installed) == before


def test_install_adds_check_library_and_ignores_local_env(installed):
    for lib in ("sdd_check.sh", "sdd_probe.sh"):
        assert (installed / ".claude/lib" / lib).read_bytes() == (FILES / ".claude/lib" / lib).read_bytes()
    assert ".claude/local.env" in (installed / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_update_refreshes_check_library(installed):
    lib = installed / ".claude/lib/sdd_check.sh"
    lib.write_text("# local workaround\n", encoding="utf-8")
    out = run_install(installed, "--update")
    assert lib.read_bytes() == (FILES / ".claude/lib/sdd_check.sh").read_bytes()
    assert "update  .claude/lib/sdd_check.sh" in out
