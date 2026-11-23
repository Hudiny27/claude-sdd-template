"""files/.claude/bin/sdd: each command in a repo laid out like an installed project."""

import datetime
import os
import shutil
import subprocess

import pytest

from libtest import LIB

FILES = LIB.parent.parent
TODAY = datetime.date.today().isoformat()
GOOD_S = """---
szint: S
---
# Hello

Branch: feature/phase-1-hello

## Cél
Say hello.

## Kész, ha
- it says hello

## Ellenőrzés
- [ ] Agent: `bash Plans/{dir}/validate.sh`, check T1 → PASS
- [ ] Owner: open the page
"""
VALIDATE = """#!/usr/bin/env bash
# shellcheck source=/dev/null
source "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/.claude/lib/sdd_check.sh"
sdd_init "$@"
check T1 "repo has a readme" test -f README.md
sdd_finish
"""


@pytest.fixture
def project(repo):
    for sub in ("hooks", "lib", "bin"):
        shutil.copytree(FILES / ".claude" / sub, repo.path / ".claude" / sub, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(FILES / ".githooks", repo.path / ".githooks")
    repo.write("Plans/README.md", (FILES / "Plans" / "README.md").read_text(encoding="utf-8"))
    repo.write(".gitignore", ".claude/.sdd-*\n__pycache__/\n")
    repo.write("specs/mission.md", "# Mission\n")
    repo.write("specs/tech-stack.md", "# Stack\n")
    repo.write("specs/roadmap.md", "# Roadmap\n\n- [ ] Fázis 1: Hello\n- [ ] Fázis 2: More\n")
    repo.commit("chore(sdd): scaffold")
    repo.git("config", "core.hooksPath", ".githooks")
    return repo


def sdd(repo, *args, timeout=120):
    return subprocess.run(
        ["python3", str(repo.path / ".claude" / "bin" / "sdd"), *args],
        cwd=repo.path, env=dict(repo.env, SDD_SHELLCHECK_DOCKER="0"), capture_output=True, text=True, timeout=timeout,
    )


def branch(repo):
    return repo.git("symbolic-ref", "--short", "HEAD").strip()


# --- preflight --------------------------------------------------------------

def test_preflight_passes_on_a_clean_main(project):
    r = sdd(project, "preflight")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK    working tree clean" in r.stdout
    assert "no upstream" in r.stdout


def test_preflight_fails_on_a_dirty_tree_and_a_missing_constitution(project):
    os.remove(project.path / "specs/roadmap.md")
    r = sdd(project, "preflight")
    assert r.returncode == 1
    assert "FAIL  working tree not clean" in r.stdout
    assert "constitution incomplete" in r.stdout


def test_preflight_lists_open_manual_checks_and_unmerged_branches(project):
    project.write("Plans/done/2026-10-01-a/spec.md", "## Ellenőrzés\n- [ ] Owner: open the page\n- [x] Owner: done\n")
    project.commit("docs: archived")
    project.git("branch", "feature/parked")
    project.git("checkout", "-q", "feature/parked")
    project.write("x.md", "x\n")
    project.commit("wip")
    project.git("checkout", "-q", "main")
    out = sdd(project, "preflight").stdout
    assert "1 open manual check(s)" in out
    assert "Plans/done/2026-10-01-a/spec.md:2: Owner: open the page" in out
    assert "feature/parked" in out


# --- new --------------------------------------------------------------------

def test_new_m_creates_branch_and_filled_spec(project):
    r = sdd(project, "new", "feature/phase-1-hello", "--level", "M")
    assert r.returncode == 0, r.stdout + r.stderr
    assert branch(project) == "feature/phase-1-hello"
    text = (project.path / f"Plans/{TODAY}-phase-1-hello/spec.md").read_text(encoding="utf-8")
    assert "szint: M\n" in text
    assert "Branch: feature/phase-1-hello\n" in text
    assert "Roadmap: Fázis 1: Hello\n" in text
    assert "## Kockázat és visszaút" in text


def test_new_s_keeps_three_sections_and_fix_has_no_phase(project):
    assert sdd(project, "new", "fix/typo", "--level", "S").returncode == 0
    text = (project.path / f"Plans/{TODAY}-typo/spec.md").read_text(encoding="utf-8")
    assert "szint: S\n" in text
    assert "Roadmap: nincs, `fix/` javítás" in text
    sections = [ln for ln in text.splitlines() if ln.startswith("## ")]
    assert sections == ["## Cél", "## Kész, ha", "## Ellenőrzés"]


def test_new_l_creates_four_files_and_a_runnable_validate_sh(project):
    assert sdd(project, "new", "feature/phase-2-more", "--level", "L").returncode == 0
    folder = project.path / f"Plans/{TODAY}-phase-2-more"
    assert sorted(p.name for p in folder.iterdir()) == ["plan.md", "requirements.md", "validate.sh", "validation.md"]
    assert os.access(folder / "validate.sh", os.X_OK)
    assert "Branch: feature/phase-2-more" in (folder / "plan.md").read_text(encoding="utf-8")
    r = subprocess.run(["bash", str(folder / "validate.sh")], cwd="/", env=project.env, capture_output=True, text=True)
    assert "SUMMARY: 0 passed" in r.stdout


def test_new_refuses_a_dirty_tree_an_existing_branch_and_a_bad_level(project):
    assert sdd(project, "new", "feature/x", "--level", "Q").returncode == 2
    project.git("branch", "feature/taken")
    r = sdd(project, "new", "feature/taken", "--level", "M")
    assert r.returncode == 1 and "already exists" in r.stderr
    project.write("dirty.md", "x\n")
    r = sdd(project, "new", "feature/phase-1-hello", "--level", "M")
    assert r.returncode == 1
    assert branch(project) == "main"


# --- handover ---------------------------------------------------------------

def test_handover_runs_lint_and_validate_sh_and_names_locked_files(project):
    sdd(project, "new", "fix/hello", "--level", "S")
    folder = f"Plans/{TODAY}-hello"
    project.write(folder + "/spec.md", GOOD_S.replace("feature/phase-1-hello", "fix/hello").format(dir=TODAY + "-hello")
                  + "\nChanges `specs/roadmap.md` too.\n")
    project.write(folder + "/validate.sh", VALIDATE + "# http://127.0.0.1:8000/ is local\n")
    r = sdd(project, "handover")
    assert "== lint\nno findings" in r.stdout, r.stdout + r.stderr
    assert "PASS  T1" in r.stdout
    assert "== live URLs in validate.sh\nnone" in r.stdout
    assert "specs/roadmap.md: say so in the handover" in r.stdout


def test_handover_fails_on_lint_findings(project):
    sdd(project, "new", "fix/hello", "--level", "S")
    r = sdd(project, "handover")
    assert r.returncode == 1
    assert "handover checks FAILED" in r.stdout


# --- archive ----------------------------------------------------------------

def spec_committed(project):
    sdd(project, "new", "fix/hello", "--level", "S")
    folder = f"Plans/{TODAY}-hello"
    project.write(folder + "/spec.md", GOOD_S.replace("feature/phase-1-hello", "fix/hello").format(dir=TODAY + "-hello"))
    project.write(folder + "/validate.sh", VALIDATE)
    project.commit("docs(plans): add spec")
    return folder


def test_archive_moves_fixes_paths_reruns_and_commits(project):
    folder = spec_committed(project)
    r = sdd(project, "archive")
    assert r.returncode == 0, r.stdout + r.stderr
    done = project.path / "Plans/done" / os.path.basename(folder)
    assert f"bash Plans/done/{TODAY}-hello/validate.sh" in (done / "spec.md").read_text(encoding="utf-8")
    assert not (project.path / folder).exists()
    assert "validate.sh passes" in r.stdout
    assert project.git("log", "-1", "--format=%s").strip() == f"docs(plans): archive {TODAY}-hello"
    assert project.git("status", "--porcelain") == ""


def test_archive_refuses_a_dirty_tree(project):
    spec_committed(project)
    project.write("notes.md", "x\n")
    r = sdd(project, "archive")
    assert r.returncode == 1
    assert "not clean" in r.stderr


# --- commit -----------------------------------------------------------------

def test_commit_needs_check_sh(project):
    project.write("NOTES.md", "x\n")
    r = sdd(project, "commit", "-m", "docs: notes", "--", "NOTES.md")
    assert r.returncode == 1
    assert ".claude/check.sh is missing" in r.stderr


def test_commit_only_when_the_check_passes_and_only_named_files(project):
    project.write(".claude/check.sh", "test -f PASS\n")
    project.commit("chore: check")
    project.write("NOTES.md", "x\n")
    project.write("OTHER.md", "y\n")
    r = sdd(project, "commit", "-m", "docs: notes", "--", "NOTES.md")
    assert r.returncode == 1
    assert "nothing committed" in r.stderr
    assert project.git("log", "-1", "--format=%s").strip() == "chore: check"
    project.write("PASS", "")
    r = sdd(project, "commit", "-m", "docs: notes", "--", "NOTES.md")
    assert r.returncode == 0, r.stdout + r.stderr
    assert project.git("show", "--name-only", "--format=", "HEAD").split() == ["NOTES.md"]
    assert "?? OTHER.md" in project.git("status", "--porcelain")


def test_preflight_lists_open_backlog_items(project):
    project.write("specs/backlog/2026-11-01-open.md", "# Export gomb\n\nÁllapot: nyitott: a következő /replan dönt.\n")
    project.write("specs/backlog/2026-11-02-planned.md", "# Planned\n\nÁllapot: ütemezve: Fázis 3\n")
    project.write("specs/backlog/2026-11-03-nostatus.md", "# Régi ötlet\n")
    project.git("add", "-A")  # an old item without a status line: past the new lint
    project.git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "docs: backlog")
    out = sdd(project, "preflight").stdout
    assert "2 open backlog item(s)" in out
    assert "specs/backlog/2026-11-01-open.md: Export gomb" in out
    assert "specs/backlog/2026-11-03-nostatus.md: Régi ötlet (no Állapot line)" in out
    assert "planned" not in out


# --- batch ------------------------------------------------------------------

def test_batch_new_and_add_create_worktrees_specs_and_rows(project):
    r = sdd(project, "batch", "new", "ejjel")
    assert r.returncode == 0, r.stdout + r.stderr
    batch = project.path / f"Plans/kotegek/{TODAY}-ejjel.md"
    assert "koteg: ejjel" in batch.read_text(encoding="utf-8")
    r = sdd(project, "batch", "add", "ejjel", "feature/phase-1-hello", "--level", "M")
    assert r.returncode == 0, r.stdout + r.stderr
    wt = project.path / ".claude/worktrees/phase-1-hello"
    assert (wt / f"Plans/{TODAY}-phase-1-hello/spec.md").is_file()
    assert project.git("-C", str(wt), "symbolic-ref", "--short", "HEAD").strip() == "feature/phase-1-hello"
    r = sdd(project, "batch", "add", "ejjel", "feature/phase-2-more", "--level", "S", "--after", "feature/phase-1-hello")
    assert r.returncode == 0, r.stdout + r.stderr
    text = batch.read_text(encoding="utf-8")
    assert "| 1 | feature/phase-1-hello | M | - | .claude/worktrees/phase-1-hello |" in text
    assert "| 2 | feature/phase-2-more | S | feature/phase-1-hello | .claude/worktrees/phase-2-more |" in text
    # The dependent branch starts from the branch it builds on.
    base = project.git("rev-parse", "feature/phase-1-hello").strip()
    assert project.git("merge-base", "--is-ancestor", base, "feature/phase-2-more") == ""
    assert branch(project) == "main"


def test_batch_add_refuses_unknown_batch_and_dependency(project):
    assert sdd(project, "batch", "add", "nincs", "feature/x", "--level", "M").returncode == 1
    sdd(project, "batch", "new", "ejjel")
    r = sdd(project, "batch", "add", "ejjel", "feature/x", "--level", "M", "--after", "feature/missing")
    assert r.returncode == 1 and "not in the batch" in r.stderr


def test_batch_status_shows_each_member(project):
    sdd(project, "batch", "new", "ejjel")
    sdd(project, "batch", "add", "ejjel", "feature/phase-1-hello", "--level", "M")
    out = sdd(project, "batch", "status", "ejjel").stdout
    assert "feature/phase-1-hello" in out
    assert "not approved" in out


def test_help_lists_the_commands_and_usage_errors_exit_2(project):
    r = sdd(project, "--help")
    assert r.returncode == 0
    assert "sdd batch add NAME BRANCH" in r.stdout and "sdd preflight" in r.stdout
    assert sdd(project, "batch", "add").returncode == 2
    assert sdd(project, "new", "feature/x").returncode == 2


def test_batch_status_without_a_name_uses_the_newest_batch(project):
    assert sdd(project, "batch", "status").returncode == 1  # no batch yet: a clear failure
    sdd(project, "batch", "new", "ejjel")
    out = sdd(project, "batch", "status").stdout
    assert f"Plans/kotegek/{TODAY}-ejjel.md: 0 feature(s)" in out


# --- batch: set and next ----------------------------------------------------

def batch_of_four(project):
    sdd(project, "batch", "new", "ejjel")
    for args in (("feature/a", "M"), ("feature/b", "S"), ("feature/c", "S", "--after", "feature/a"), ("feature/d", "S")):
        r = sdd(project, "batch", "add", "ejjel", args[0], "--level", *args[1:])
        assert r.returncode == 0, r.stderr
    batch = project.path / f"Plans/kotegek/{TODAY}-ejjel.md"
    text = batch.read_text(encoding="utf-8").replace("| ? | ? | spec |", "| 1 óra | nem | jóváhagyva |")
    text = text.replace("## Közös döntések\n", "## Közös döntések\n- nem egyszerre: `feature/b` és `feature/d` (döntött: agent, 2026-11-23)\n")
    batch.write_text(text, encoding="utf-8")
    return batch


def test_batch_next_respects_limit_dependencies_and_pairs(project):
    batch_of_four(project)
    out = sdd(project, "batch", "next").stdout
    assert out.splitlines()[:2] == ["feature/a", "feature/b"]
    sdd(project, "batch", "set", "ejjel", "feature/a", "épül")
    sdd(project, "batch", "set", "ejjel", "feature/b", "épül")
    assert sdd(project, "batch", "next").stdout.strip() == ""  # two are running
    sdd(project, "batch", "set", "ejjel", "feature/b", "merge-kész")
    # c waits for a, d may not run beside b's pair... b is done, so d can start
    assert sdd(project, "batch", "next").stdout.split() == ["feature/d"]
    sdd(project, "batch", "set", "ejjel", "feature/a", "merge-kész")
    assert "feature/c" in sdd(project, "batch", "next").stdout


def test_batch_set_parks_dependants_and_logs_outside_the_repo(project):
    batch = batch_of_four(project)
    r = sdd(project, "batch", "set", "ejjel", "feature/a", "parkolva", "3 sikertelen javítási kör")
    assert r.returncode == 0, r.stderr
    text = batch.read_text(encoding="utf-8")
    assert "| feature/a | M | - |" in text and text.count("| parkolva |") == 2
    logs = list((project.tmp.parent / ".claude" / "execute").rglob("naplo.md"))
    assert logs, "no ledger written"
    entries = logs[0].read_text(encoding="utf-8")
    assert "feature/a | parkolva | 3 sikertelen javítási kör" in entries
    assert "feature/c | parkolva | vár: feature/a" in entries
    assert sdd(project, "batch", "set", "ejjel", "feature/a", "kész").returncode == 2


# --- batch: report and merge ------------------------------------------------

def built_batch(project):
    """A batch of two, a and c (c builds on a), each with one commit and an archived spec."""
    project.write(".claude/check.sh", "true\n")
    project.commit("chore: check")
    sdd(project, "batch", "new", "ejjel")
    sdd(project, "batch", "add", "ejjel", "feature/a", "--level", "S")
    sdd(project, "batch", "add", "ejjel", "feature/c", "--level", "S", "--after", "feature/a")
    batch = project.path / f"Plans/kotegek/{TODAY}-ejjel.md"
    batch.write_text(batch.read_text(encoding="utf-8").replace("| ? | ? | spec |", "| 1 óra | nem | merge-kész |"), encoding="utf-8")
    for name in ("a", "c"):
        wt = project.path / ".claude/worktrees" / name
        spec = wt / f"Plans/{TODAY}-{name}/spec.md"
        spec.write_text(
            "---\nszint: S\n---\n# " + name + "\n\n## Cél\nx\n\n## Kész, ha\n- x\n\n## Ellenőrzés\n- [ ] Owner: nézd meg " + name + "\n\n"
            "## Döntések\n- éjjeli döntés " + name + " (döntött: agent, " + TODAY + ")\n", encoding="utf-8")
        (wt / (name + ".py")).write_text("X = 1\n", encoding="utf-8")
        if name == "c":
            project.git("-C", str(wt), "merge", "-q", "feature/a", "-m", "merge a")
        project.git("-C", str(wt), "add", "-A")
        project.git("-C", str(wt), "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "feat: " + name)
    return batch


def test_batch_report_lists_states_decisions_and_manual_checks(project):
    built_batch(project)
    out = sdd(project, "batch", "report").stdout
    assert "feature/a" in out and "feature/c" in out
    assert "merge-kész" in out
    assert "éjjeli döntés a" in out and "éjjeli döntés c" in out
    assert "Owner: nézd meg a" in out
    assert "feature/a" in out.split("feature/c")[1]  # c names what it depends on


def test_batch_merge_refuses_a_dependant_without_its_base(project):
    built_batch(project)
    r = sdd(project, "batch", "merge", "ejjel", "feature/c")
    assert r.returncode == 1 and "feature/a" in r.stderr
    assert project.git("log", "--oneline", "-1").strip().endswith("chore: check")


def test_batch_merge_merges_in_order_checks_and_cleans_up(project):
    batch = built_batch(project)
    r = sdd(project, "batch", "merge", "ejjel", "feature/c", "feature/a")
    assert r.returncode == 0, r.stdout + r.stderr
    log = project.git("log", "--first-parent", "--format=%s", "-2").splitlines()
    assert log == ["Merge branch 'feature/c'", "Merge branch 'feature/a'"]
    assert not (project.path / ".claude/worktrees/a").exists()
    assert project.git("branch", "--list", "feature/a").strip() == ""
    assert batch.read_text(encoding="utf-8").count("| mergelve |") == 2


def test_batch_status_after_merge_says_merged(project):
    built_batch(project)
    sdd(project, "batch", "merge", "ejjel", "feature/a", "feature/c")
    out = sdd(project, "batch", "status").stdout
    assert out.count("merged into main") == 2, out
    assert "no spec" not in out
