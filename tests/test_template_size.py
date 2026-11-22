"""Size limits of the template's always-loaded and per-step instructions."""

from pathlib import Path

import pytest

FILES = Path(__file__).resolve().parent.parent / "files"
CLAUDE_MD_MAX = 150
SKILL_MD_MAX = 100
SKILLS = sorted((FILES / ".claude" / "skills").glob("*/SKILL.md"))


def line_count(path):
    return len(path.read_text(encoding="utf-8").splitlines())


def test_claude_md_within_limit():
    lines = line_count(FILES / "CLAUDE.md")
    assert lines <= CLAUDE_MD_MAX, f"CLAUDE.md has {lines} lines (max {CLAUDE_MD_MAX})"


def test_skills_found():
    assert SKILLS, "no SKILL.md found under files/.claude/skills/"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.parent.name)
def test_skill_md_within_limit(skill):
    lines = line_count(skill)
    assert lines <= SKILL_MD_MAX, f"{skill.parent.name}/SKILL.md has {lines} lines (max {SKILL_MD_MAX})"
