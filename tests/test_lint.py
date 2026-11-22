"""files/.claude/lib/sdd_lint.py: each check with a passing and a failing case."""

import subprocess
import sys

from libtest import LIB

LINT = LIB / "sdd_lint.py"
DIR = "Plans/2026-11-01-phase-1-hello"

SPEC_M = """---
szint: M
---
# Hello

Roadmap: Fázis 1: Hello
Branch: feature/phase-1-hello

## Cél
Say hello.

## Bele tartozik
- a greeting

## Nem tartozik bele
- farewells

## Döntések
- The greeting is plain text: simplest (döntött: owner, 2026-11-01)
- Port range 8000-8999, a wrapped
  line that ends the bullet (döntött: agent, 2026-11-01)

## Kész, ha
- it says hello

## Ellenőrzés
- [ ] Agent: `bash Plans/2026-11-01-phase-1-hello/validate.sh`, check T1 → PASS
- [ ] Owner: open the page

## Kockázat és visszaút
- ajtó: kétirányú: a revert undoes it
- hatósugár: kicsi: one greeting page
- revert the commit
"""

VALIDATE = """#!/usr/bin/env bash
# shellcheck source=/dev/null
source "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/.claude/lib/sdd_check.sh"
sdd_init "$@"
check T1 "says hello" true
sdd_finish
"""

PLAN = """# Terv: hello

Roadmap: Fázis 1: Hello
Branch: feature/phase-1-hello

## 1. csoport: Greeting
1. write it

## 2. csoport: Ellenőrzés
- run validation.md
"""

REQUIREMENTS = """# Követelmények: hello

## Hatókör
- a greeting

## Hatókörön kívül
- farewells

## Döntések
- Timeout 5 s, kalibrálandó (döntött: agent, 2026-11-01)

## Kontextus
- none

## Kockázat és visszaút
- ajtó: egyirányú: the greeting is mailed out
- hatósugár: nagy: every user gets it

## Kalibrálás
<!-- results -->
"""

VALIDATION = """# Validáció: hello

## Automatikus ellenőrzések (az agent futtatja)
- [ ] T1: says hello
- [ ] Fresh-subagent probe with the guide

## Kézi ellenőrzések (az owner futtatja)
- [ ] look at it

## Kész definíciója
- all green
"""


def lint(repo, *args):
    return subprocess.run(
        [sys.executable, str(LINT), *args], cwd=repo.path, env=repo.env, capture_output=True, text=True, timeout=60,
    )


def feature(repo, files):
    repo.git("checkout", "-q", "-b", "feature/phase-1-hello")
    for name, text in files.items():
        repo.write(DIR + "/" + name, text)


def findings(result):
    return [ln for ln in result.stdout.splitlines() if ": [" in ln]


# --- spec -------------------------------------------------------------------

def test_good_m_spec_passes(repo):
    feature(repo, {"spec.md": SPEC_M, "validate.sh": VALIDATE})
    r = lint(repo)
    assert r.returncode == 0, r.stdout + r.stderr


def test_m_spec_missing_sections_and_level(repo):
    feature(repo, {"spec.md": SPEC_M.replace("## Nem tartozik bele\n", "").replace("szint: M", "szint: X")})
    out = lint(repo).stdout
    assert "szint: S" in out
    feature_text = SPEC_M.split("## Kockázat és visszaút")[0]
    repo.write(DIR + "/spec.md", feature_text)
    r = lint(repo)
    assert r.returncode == 1
    assert "missing section `## Kockázat és visszaút`" in r.stdout


def test_s_spec_needs_only_three_sections(repo):
    feature(repo, {"spec.md": "---\nszint: S\n---\n# x\n\n## Cél\nx\n\n## Kész, ha\n- x\n\n## Ellenőrzés\n- [ ] Owner: x\n"})
    assert lint(repo).returncode == 0


def test_branch_line_must_match_the_folder(repo):
    feature(repo, {"spec.md": SPEC_M.replace("Branch: feature/phase-1-hello", "Branch: feature/phase-2-other"), "validate.sh": VALIDATE})
    assert "does not match the folder" in lint(repo).stdout


def test_l_spec_needs_all_files_and_groups(repo):
    feature(repo, {"plan.md": PLAN.replace("## 1. csoport: Greeting", "## Greeting").replace("## 2. csoport: Ellenőrzés", "## End"), "requirements.md": REQUIREMENTS})
    out = lint(repo).stdout
    assert "no task group" in out
    assert "validation.md:0: [spec] missing" in out
    assert "validate.sh:0: [spec] missing" in out


def test_good_l_spec_passes(repo):
    feature(repo, {"plan.md": PLAN, "requirements.md": REQUIREMENTS, "validation.md": VALIDATION, "validate.sh": VALIDATE})
    r = lint(repo)
    assert r.returncode == 0, r.stdout + r.stderr


# --- decisions --------------------------------------------------------------

def test_decision_without_decider_or_with_two(repo):
    text = SPEC_M.replace(
        "- The greeting is plain text: simplest (döntött: owner, 2026-11-01)",
        "- The greeting is plain text: simplest\n- Mixed (döntött: owner, 2026-11-01) and (döntött: agent, 2026-11-01)",
    )
    feature(repo, {"spec.md": text, "validate.sh": VALIDATE})
    out = lint(repo).stdout
    assert "needs `(döntött: owner | agent, YYYY-MM-DD)`: The greeting is plain text" in out
    assert "more than one decider" in out


def test_deleted_decision_on_main_must_be_superseded(repo):
    repo.write("Plans/done/2026-10-01-old/spec.md", SPEC_M)
    repo.commit("old spec")
    reworded = SPEC_M.replace("simplest (döntött", "the simplest (döntött")
    repo.write("Plans/done/2026-10-01-old/spec.md", reworded)
    repo.git("add", "Plans/done/2026-10-01-old/spec.md")
    r = lint(repo, "--staged")
    assert r.returncode == 1
    assert "was deleted or reworded" in r.stdout
    superseded = SPEC_M.replace(
        "simplest (döntött: owner, 2026-11-01)",
        "simplest (döntött: owner, 2026-11-01) (felváltva 2026-11-20, lásd Plans/done/2026-11-20-new)",
    )
    repo.write("Plans/done/2026-10-01-old/spec.md", superseded)
    repo.git("add", "Plans/done/2026-10-01-old/spec.md")
    r = lint(repo, "--staged")
    assert r.returncode == 0, r.stdout


def test_badly_written_superseded_mark(repo):
    feature(repo, {"spec.md": SPEC_M.replace("simplest (döntött: owner, 2026-11-01)", "simplest (döntött: owner, 2026-11-01) (felváltva tegnap)"), "validate.sh": VALIDATE})
    assert "(felváltva YYYY-MM-DD, lásd ...)" in lint(repo).stdout


# --- calibration ------------------------------------------------------------

def test_calibrated_value_needs_a_result_at_the_end(repo):
    feature(repo, {"plan.md": PLAN, "requirements.md": REQUIREMENTS, "validation.md": VALIDATION, "validate.sh": VALIDATE})
    assert lint(repo).returncode == 0
    r = lint(repo, "--final")
    assert "kalibrálandó value has no measured result" in r.stdout
    repo.write(DIR + "/requirements.md", REQUIREMENTS + "\n### Timeout (1. csoport)\n- Minta: 20 runs\n- Söprés: | 3 s | 5 s |\n- Választás: 5 s: margin 2 s\n- Ellenőrzés: test_timeout\n")
    r = lint(repo, "--final")
    assert "calibration" not in r.stdout, r.stdout


def test_calibration_subsection_fields_in_order(repo):
    bad = REQUIREMENTS + "\n### Timeout (1. csoport)\n- Minta: 20 runs\n- Választás: 5 s\n- Söprés: x\n- Ellenőrzés: t\n"
    feature(repo, {"plan.md": PLAN, "requirements.md": bad, "validation.md": VALIDATION, "validate.sh": VALIDATE})
    assert "needs Minta, Söprés, Választás, Ellenőrzés in this order" in lint(repo).stdout


# --- coverage ---------------------------------------------------------------

def test_every_automated_check_names_a_check_id(repo):
    text = SPEC_M.replace("check T1 → PASS", "→ PASS").replace("- [ ] Owner: open the page", "- [ ] Owner: open the page\n- [ ] Agent: T9 something")
    feature(repo, {"spec.md": text, "validate.sh": VALIDATE})
    out = findings(lint(repo))
    assert len([f for f in out if "[coverage]" in f]) == 2, out


def test_probe_bullet_is_exempt_and_owner_lines_are_not_checked(repo):
    feature(repo, {"plan.md": PLAN, "requirements.md": REQUIREMENTS, "validation.md": VALIDATION, "validate.sh": VALIDATE})
    assert "[coverage]" not in lint(repo).stdout


# --- paths, shell -----------------------------------------------------------

def test_code_naming_a_dated_spec_folder(repo):
    repo.write("tests/test_x.py", "DATA = 'Plans/2026-11-01-phase-1-hello/fixture.json'\n")
    repo.git("add", "tests/test_x.py")
    r = lint(repo, "--staged")
    assert r.returncode == 1
    assert "tests/test_x.py:1: [paths]" in r.stdout
    repo.write("tests/test_x.py", "DATA = 'fixture.json'\n")
    repo.git("add", "tests/test_x.py")
    assert lint(repo, "--staged").returncode == 0


def test_spec_script_must_not_use_parents(repo):
    feature(repo, {"spec.md": SPEC_M, "validate.sh": VALIDATE, "helper.py": "ROOT = Path(__file__).resolve().parents[2]\n"})
    assert "helper.py:1: [paths]" in lint(repo).stdout


def test_shell_syntax_error(repo):
    feature(repo, {"spec.md": SPEC_M, "validate.sh": VALIDATE + "if then fi\n"})
    repo.git("add", DIR)
    r = lint(repo, "--staged")
    assert "validate.sh:0: [shell] bash -n" in r.stdout


# --- size -------------------------------------------------------------------

def test_size_limits(repo):
    repo.write(".claude/project.md", "x\n" * 61)
    repo.write(".claude/skills/mine/SKILL.md", "x\n" * 100)
    out = lint(repo).stdout
    assert ".claude/project.md:61: [size]" in out
    assert "skills/mine" not in out
    repo.write(".claude/skills/mine/SKILL.md", "x\n" * 101)
    assert ".claude/skills/mine/SKILL.md:101: [size]" in lint(repo).stdout


# --- dangling ---------------------------------------------------------------

def test_dangling_paths_in_changed_markdown(repo):
    feature(repo, {"spec.md": SPEC_M, "validate.sh": VALIDATE})
    repo.write("docs/guide.md", "Run `src/app.py`, then `src/missing.py`; branch `feature/x`, `Plans/<dir>/x`.\n")
    out = lint(repo, "--final").stdout
    assert "docs/guide.md:1: [dangling] `src/missing.py` does not exist" in out
    assert "src/app.py`" not in out
    assert "feature/x" not in out and "<dir>" not in out


def test_markdown_naming_a_renamed_file(repo):
    repo.write("docs/guide.md", "Run `src/app.py`.\n")
    repo.commit("docs")
    feature(repo, {"spec.md": SPEC_M, "validate.sh": VALIDATE})
    repo.git("mv", "src/app.py", "src/main.py")
    repo.git("commit", "-q", "-m", "rename")
    out = lint(repo, "--final").stdout
    assert "docs/guide.md:1: [dangling] `src/app.py` was renamed to `src/main.py`" in out


def test_template_files_pass_their_own_lint(repo):
    """The template's own CLAUDE.md and skills stay within the size limits."""
    for rel in ("CLAUDE.md", ".claude/skills/feature-spec/SKILL.md", ".claude/project.md"):
        repo.write(rel, (LIB.parent.parent / rel).read_text(encoding="utf-8"))
    assert "[size]" not in lint(repo).stdout


def test_template_placeholders_left(repo):
    feature(repo, {"spec.md": SPEC_M.replace("Say hello.", "<1–3 mondat: mit akar az owner>").replace("- farewells", "- …"), "validate.sh": VALIDATE})
    out = lint(repo).stdout
    assert out.count("template placeholder left") == 2, out


def test_risk_fields_required_for_m_and_l(repo):
    text = SPEC_M.replace("- ajtó: kétirányú: a revert undoes it\n", "").replace("hatósugár: kicsi", "hatósugár: óriási")
    feature(repo, {"spec.md": text, "validate.sh": VALIDATE})
    out = lint(repo).stdout
    assert "needs `- ajtó: egyirányú | kétirányú: <why>`" in out
    assert "needs `- hatósugár: kicsi | közepes | nagy: <why>`" in out
    repo.git("checkout", "-q", "main")
    repo.git("checkout", "-q", "-b", "feature/phase-2-l")
    folder = "Plans/2026-11-01-phase-2-l/"
    for name, t in (("plan.md", PLAN.replace("phase-1-hello", "phase-2-l")), ("requirements.md", REQUIREMENTS.split("## Kockázat")[0]),
                    ("validation.md", VALIDATION), ("validate.sh", VALIDATE)):
        repo.write(folder + name, t)
    out = lint(repo).stdout
    assert "requirements.md:0: [spec] missing section `## Kockázat és visszaút`" in out


def test_s_spec_needs_no_risk_fields(repo):
    feature(repo, {"spec.md": "---\nszint: S\n---\n# x\n\n## Cél\nx\n\n## Kész, ha\n- x\n\n## Ellenőrzés\n- [ ] Owner: x\n\n## Kockázat és visszaút\n- revert\n"})
    assert lint(repo).returncode == 0


# --- backlog ----------------------------------------------------------------

def test_backlog_item_needs_a_status_line(repo):
    repo.write("specs/backlog/2026-11-22-idea.md", "# Idea\n\nSome text.\n")
    repo.write("specs/backlog/2026-11-22-done.md", "# Done\n\nÁllapot: kész: Plans/done/x (2026-11-22)\n")
    repo.write("specs/backlog/2026-11-22-vague.md", "# Vague\n\nÁllapot: ötlet, még nincs a roadmapen.\n")
    repo.write("specs/backlog/README.md", "# not an item\n")
    out = lint(repo).stdout
    assert "specs/backlog/2026-11-22-idea.md:0: [backlog]" in out
    assert "specs/backlog/2026-11-22-vague.md:3: [backlog]" in out
    assert "2026-11-22-done.md" not in out and "README.md" not in out


def test_backlog_status_checked_on_commit(repo):
    repo.write("specs/backlog/2026-11-22-idea.md", "# Idea\n")
    repo.git("add", "specs/backlog/2026-11-22-idea.md")
    assert "[backlog]" in lint(repo, "--staged").stdout
    repo.write("specs/backlog/2026-11-22-idea.md", "# Idea\n\nÁllapot: nyitott: a következő /replan dönt.\n")
    repo.git("add", "specs/backlog/2026-11-22-idea.md")
    assert lint(repo, "--staged").returncode == 0


# --- batch file -------------------------------------------------------------

BATCH = """---
koteg: ejjel
datum: 2026-11-22
idokeret: 07:00
artifact: nem
---
# Köteg: ejjel

## Feature-ök
| # | Branch | Fokozat | Függ | Worktree | Becslés | Auth/biztonság | Állapot |
|---|---|---|---|---|---|---|---|
| 1 | feature/a | M | - | .claude/worktrees/a | 1 óra | nem | spec |
"""


def test_good_batch_file_passes(repo):
    repo.write("Plans/kotegek/2026-11-22-ejjel.md", BATCH)
    repo.git("add", "Plans/kotegek/2026-11-22-ejjel.md")
    r = lint(repo, "--staged")
    assert r.returncode == 0, r.stdout


def test_bad_batch_file(repo):
    bad = BATCH.replace("artifact: nem", "artifact: talán").replace(
        "| 1 | feature/a | M | - | .claude/worktrees/a | 1 óra | nem | spec |",
        "| 1 | feature/a | X | feature/zz | ../outside | 1 óra | igen | kész |",
    )
    repo.write("Plans/kotegek/2026-11-22-ejjel.md", bad)
    repo.git("add", "Plans/kotegek/2026-11-22-ejjel.md")
    out = lint(repo, "--staged").stdout
    for part in ("artifact", "Fokozat", "feature/zz", ".claude/worktrees/", "auth", "Állapot"):
        assert part in out, part


def test_batch_file_without_rows_yet_commits(repo):
    start = BATCH.split("| 1 | feature/a")[0]
    repo.write("Plans/kotegek/2026-11-22-ejjel.md", start)
    repo.git("add", "Plans/kotegek/2026-11-22-ejjel.md")
    r = lint(repo, "--staged")
    assert r.returncode == 0, r.stdout
    repo.write("Plans/kotegek/2026-11-22-ejjel.md", start.split("## Feature-ök")[0])
    repo.git("add", "Plans/kotegek/2026-11-22-ejjel.md")
    assert "no feature table" in lint(repo, "--staged").stdout


def test_final_lint_measures_from_the_branch_point_not_from_a_moved_main(repo):
    repo.write("docs/notes.md", "See `docs/decisions/` later.\n")
    repo.commit("docs")
    feature(repo, {"spec.md": SPEC_M, "validate.sh": VALIDATE})
    repo.commit("spec")
    # main moves on after the branch point: it edits a file the branch never touched
    repo.git("checkout", "-q", "main")
    repo.write("docs/notes.md", "See `docs/decisions/` later. (updated on main)\n")
    repo.commit("main moves")
    repo.git("checkout", "-q", "feature/phase-1-hello")
    r = lint(repo, "--final")
    assert "docs/notes.md" not in r.stdout, r.stdout
