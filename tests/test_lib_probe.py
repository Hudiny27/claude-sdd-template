"""files/.claude/lib/sdd_probe.sh: copies for probes and the git status guard."""

import pytest


@pytest.fixture
def scratch(tmp_path):
    return tmp_path / "scratch"


def probe(repo, scratch, body):
    return repo.run(f'SDD_PROBE_ROOT="{scratch}"\n' + body, lib="sdd_probe.sh", init=False)


# --- probe_copy --------------------------------------------------------------

def test_probe_copy_includes_untracked_and_excludes_ignored(repo, scratch):
    repo.write(".gitignore", "real-data/\n")
    repo.commit("ignore real data")
    repo.write("real-data/patient.txt", "secret\n")
    repo.write("docs/new-guide.md", "new, not staged\n")
    r = probe(repo, scratch, "probe_copy 1 interactive\n")
    assert r.returncode == 0, r.stderr
    copy = scratch / "round-1" / "interactive"
    assert r.stdout.strip() == str(copy)
    assert (copy / "repo/docs/new-guide.md").read_text() == "new, not staged\n"
    assert (copy / "repo/src/app.py").exists()
    assert not (copy / "repo/real-data").exists()
    assert not (copy / "sample").exists()


def test_probe_copy_is_fresh_and_runs_regen_hook(repo, scratch):
    stale = scratch / "round-2" / "auto" / "repo" / "stale.txt"
    stale.parent.mkdir(parents=True)
    stale.write_text("old round\n")
    r = probe(repo, scratch,
              'probe_regen() { echo regenerated > "$1/repo/guide.md"; }\nprobe_copy 2 auto\n')
    assert r.returncode == 0, r.stderr
    assert not stale.exists()
    assert (scratch / "round-2/auto/repo/guide.md").read_text() == "regenerated\n"


def test_probe_copy_refuses_scratch_inside_repo(repo):
    r = probe(repo, repo.path / "probes", "probe_copy 1 a\n")
    assert r.returncode == 1
    assert "inside the repository" in r.stderr


def test_probe_copy_refuses_bad_names(repo, scratch):
    r = probe(repo, scratch, "probe_copy .. a\n")
    assert r.returncode == 2
    assert "usage" in r.stderr


def test_probe_copy_fails_when_regen_hook_fails(repo, scratch):
    r = probe(repo, scratch, "probe_regen() { return 1; }\nprobe_copy 1 a\n")
    assert r.returncode == 1
    assert "probe_regen failed" in r.stderr


# --- probe_base --------------------------------------------------------------

BASE_BODY = (
    'probe_upgrade() { echo upgraded >> "$1/upgrades"; echo "upgrade-ran" >&2; }\n'
    "probe_base samples/demo\n"
    "probe_copy 1 a\n"
)


def test_probe_base_upgrades_once_and_copies_into_rounds(repo, scratch):
    repo.write("samples/demo/project.json", '{"v": 1}\n')
    r1 = probe(repo, scratch, BASE_BODY)
    assert r1.returncode == 0, r1.stderr
    assert "upgrade-ran" in r1.stderr
    assert (scratch / "round-1/a/sample/upgrades").read_text() == "upgraded\n"
    r2 = probe(repo, scratch, BASE_BODY)
    assert "upgrade-ran" not in r2.stderr
    repo.write("samples/demo/project.json", '{"v": 2}\n')
    r3 = probe(repo, scratch, BASE_BODY)
    assert "upgrade-ran" in r3.stderr
    assert (scratch / "base/project.json").read_text() == '{"v": 2}\n'


def test_probe_base_fails_on_missing_sample(repo, scratch):
    r = probe(repo, scratch, "probe_base samples/none\n")
    assert r.returncode == 1
    assert "sample folder not found" in r.stderr


def test_probe_base_fails_when_upgrade_fails(repo, scratch):
    repo.write("samples/demo/project.json", "{}\n")
    r = probe(repo, scratch, "probe_upgrade() { return 1; }\nprobe_base samples/demo\n")
    assert r.returncode == 1
    assert not (scratch / "base.stamp").exists()


# --- snapshot_status and assert_no_new_files ---------------------------------

def test_no_new_files_passes_when_unchanged(repo, scratch):
    repo.write("wip.txt", "already there\n")
    probe(repo, scratch, "snapshot_status\n")
    r = probe(repo, scratch, "assert_no_new_files\n")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "unchanged" in r.stdout


def test_no_new_files_fails_on_left_file(repo, scratch):
    probe(repo, scratch, "snapshot_status\n")
    repo.write("left-by-probe.txt", "x\n")
    r = probe(repo, scratch, "assert_no_new_files\n")
    assert r.returncode == 1
    assert "left-by-probe.txt" in r.stdout


def test_no_new_files_needs_snapshot(repo, scratch):
    r = probe(repo, scratch, "assert_no_new_files\n")
    assert r.returncode == 1
    assert "run snapshot_status first" in r.stderr
