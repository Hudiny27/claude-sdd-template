"""files/.claude/lib/sdd_check.sh: every function with a passing and a failing case."""

import socket
import subprocess
import time
from libtest import LIB, alive


# --- sdd_init, check, sdd_finish -------------------------------------------

def test_init_enters_root_and_exports_own_folder(repo):
    r = repo.run('echo "pwd=$PWD"; echo "dir=$SDD_DIR"; check T1 ok true; sdd_finish\n')
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"pwd={repo.path}" in r.stdout
    assert f"dir={repo.path / 'Plans/x'}" in r.stdout


def test_init_outside_git_fails(tmp_path, repo):
    script = tmp_path / "loose.sh"
    script.write_text(f'source "{LIB / "sdd_check.sh"}"\nsdd_init\n')
    r = subprocess.run(["bash", str(script)], cwd="/", env=repo.env, capture_output=True, text=True)
    assert r.returncode == 2
    assert "not inside a git repository" in r.stderr


def test_check_pass_and_finish_zero(repo):
    r = repo.run('check T1 "says hi" echo hi; sdd_finish\n')
    assert r.returncode == 0
    assert "PASS  T1  says hi  (exit 0: hi)" in r.stdout
    assert "SUMMARY: 1 passed, 0 failed, 0 skipped" in r.stdout


def test_check_failure_makes_finish_nonzero_and_continues(repo):
    r = repo.run('check T1 bad bash -c "echo boom; exit 3"\ncheck T2 good true\nsdd_finish\n')
    assert r.returncode == 1
    assert "FAIL  T1  bad  (exit 3: boom)" in r.stdout
    assert "PASS  T2  good" in r.stdout
    assert "FAILED: T1" in r.stdout


def test_check_function_stops_at_first_failing_step(repo):
    r = repo.run('steps() { false; echo "not reached"; }\ncheck T1 steps steps\nsdd_finish\n')
    assert r.returncode == 1
    assert "not reached" not in r.stdout


def test_finish_without_checks_fails(repo):
    r = repo.run("sdd_finish\n")
    assert r.returncode == 1
    assert "no check ran" in r.stdout


def test_temp_dir_removed_on_error_exit(repo):
    r = repo.run('touch "$SDD_TMP/x"; echo "$SDD_TMP"; false\n')
    assert r.returncode == 1
    assert repo.leftovers() == []


def test_early_errexit_exit_prints_fail_and_summary(repo):
    body = (
        "P=$(free_port)\n"
        "start_bg web bash -c 'echo cannot bind; exit 1'\n"
        'wait_port "$P" 1\n'
        'check T1 "server answers" check_url "http://127.0.0.1:$P/"\n'
        "sdd_finish\n"
    )
    r = repo.run(body, timeout=30)
    assert r.returncode != 0
    assert "FAIL  EXIT" in r.stdout, r.stdout + r.stderr
    assert "SUMMARY: 0 passed, 1 failed, 0 skipped" in r.stdout


def test_exit_without_finish_fails_with_summary(repo):
    r = repo.run("check T1 ok true\n")
    assert r.returncode == 1
    assert "without sdd_finish" in r.stdout
    assert "SUMMARY: 1 passed, 1 failed, 0 skipped" in r.stdout


# --- live_only and local.env -----------------------------------------------

LIVE_BODY = "live_only check L1 live bash -c 'echo host=$SAMPLE_HOST'\nsdd_finish\n"


def test_live_only_skips_without_live(repo):
    repo.write(".claude/local.env", "SAMPLE_HOST=example.test\n")
    r = repo.run(LIVE_BODY)
    assert r.returncode == 0
    assert "SKIP  L1  live  (needs --live)" in r.stdout
    assert "loaded .claude/local.env" not in r.stdout


def test_live_only_runs_with_live_and_loads_local_env(repo):
    repo.write(".claude/local.env", "SAMPLE_HOST=example.test\n")
    r = repo.run(LIVE_BODY, "--live")
    assert r.returncode == 0, r.stdout
    assert "loaded .claude/local.env" in r.stdout
    assert "PASS  L1  live  (exit 0: host=example.test)" in r.stdout


def test_live_only_failing_live_check_fails(repo):
    r = repo.run("live_only check L1 live false\nsdd_finish\n", "--live")
    assert r.returncode == 1
    assert "FAIL  L1" in r.stdout


def test_quick_and_unknown_args(repo):
    r = repo.run('echo "q=$SDD_QUICK l=$SDD_LIVE a=${SDD_ARGS[*]}"; check T1 ok true; sdd_finish\n',
                 "--quick", "extra")
    assert "q=1 l=0 a=extra" in r.stdout


# --- start_bg ----------------------------------------------------------------

def test_start_bg_process_gone_after_error_exit(repo):
    pidfile = repo.path.parent / "child.pid"
    body = (
        f"start_bg sleeper bash -c 'sleep 300 & echo $! > {pidfile}; wait'\n"
        f'echo "main=$SDD_BG_PID"\n'
        f'for _ in $(seq 50); do [ -s {pidfile} ] && break; sleep 0.1; done\n'
        "false\n"
    )
    r = repo.run(body)
    assert r.returncode == 1
    main_pid = int(r.stdout.split("main=")[1].split()[0])
    child_pid = int(pidfile.read_text())
    deadline = time.time() + 5
    while time.time() < deadline and (alive(main_pid) or alive(child_pid)):
        time.sleep(0.1)
    assert not alive(main_pid), "the started process survived the script"
    assert not alive(child_pid), "the started process's child survived the script"


def test_start_bg_refuses_command_substitution(repo):
    r = repo.run('x="$(start_bg s sleep 300)" || echo "refused"; check T1 ok true; sdd_finish\n')
    assert "refused" in r.stdout
    assert "must run in the main shell" in r.stderr


def test_stop_bg_stops_process_and_flushes_log(repo):
    body = (
        "start_bg writer bash -c 'trap \"echo bye; exit 0\" TERM; echo hello; "
        "while :; do sleep 0.1; done'\n"
        "pid=$SDD_BG_PID\n"
        "sleep 0.3\n"
        "stop_bg writer\n"
        'kill -0 "$pid" 2>/dev/null && echo "state=alive" || echo "state=gone"\n'
        'check T1 "log complete" grep -q bye "$SDD_TMP/writer.log"\n'
        "sdd_finish\n"
    )
    r = repo.run(body, timeout=30)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "state=gone" in r.stdout
    assert "PASS  T1" in r.stdout


def test_stop_bg_unknown_name_fails(repo):
    r = repo.run("stop_bg nosuch || echo refused\ncheck T1 ok true\nsdd_finish\n")
    assert "refused" in r.stdout
    assert "no background process named nosuch" in r.stderr


# --- free_port and wait_port -------------------------------------------------

def test_free_port_is_bindable(repo):
    r = repo.run('check T1 port free_port; sdd_finish\n')
    assert r.returncode == 0
    port = int(r.stdout.split("(exit 0: ")[1].split(")")[0])
    with socket.socket() as s:
        s.bind(("127.0.0.1", port))


def test_free_port_fails_without_python(repo):
    r = repo.run('python3() { return 1; }\ncheck T1 port free_port\nsdd_finish\n')
    assert r.returncode == 1
    assert "FAIL  T1  port" in r.stdout


def test_wait_port_times_out_on_closed_port(repo):
    r = repo.run('P=$(free_port); check T1 wait wait_port "$P" 1; sdd_finish\n')
    assert r.returncode == 1
    assert "nothing listens on port" in r.stdout


# --- check_url ---------------------------------------------------------------

URL_BODY = (
    "P=$(free_port)\n"
    'start_bg web python3 -m http.server "$P" --bind 127.0.0.1\n'
    'wait_port "$P"\n'
    'check U1 root check_url "http://127.0.0.1:$P/"\n'
    'check U2 missing check_url "http://127.0.0.1:$P/nope"\n'
    'check U3 host check_url "http://127.0.0.1:$P/" --host 127.0.0.1\n'
    'check U4 wronghost check_url "http://127.0.0.1:$P/" --host example.test\n'
    "sdd_finish\n"
)


def test_check_url_status_and_host(repo):
    r = repo.run(URL_BODY)
    assert "PASS  U1" in r.stdout and "-> 200 127.0.0.1" in r.stdout
    assert "FAIL  U2" in r.stdout and "-> 404" in r.stdout
    assert "PASS  U3" in r.stdout
    assert "FAIL  U4" in r.stdout
    assert r.returncode == 1


HTTP_BODY = (
    "P=$(free_port)\n"
    'printf "hello world\\n" > hello.txt\n'
    'start_bg web python3 -m http.server "$P" --bind 127.0.0.1\n'
    'check H0 starts wait_port "$P"\n'
    'U="http://127.0.0.1:$P"\n'
    'check H1 equals check_http "$U/hello.txt" --status 200 --body-equals "hello world"\n'
    'check H2 contains check_http "$U/hello.txt" --body-contains "lo wo"\n'
    'check H3 notfound check_http "$U/nope" --status 404\n'
    'check H4 badstatus check_http "$U/hello.txt" --status 201\n'
    'check H5 badbody check_http "$U/hello.txt" --body-contains "absent text"\n'
    'check H6 badequals check_http "$U/hello.txt" --body-equals "hello"\n'
    'check H7 default2xx check_http "$U/nope"\n'
    "sdd_finish\n"
)


def test_check_http_status_and_body(repo):
    r = repo.run(HTTP_BODY, timeout=60)
    out = r.stdout
    assert "PASS  H1  equals  (exit 0: GET " in out and "-> 200, 12 bytes: hello world" in out, out
    assert "PASS  H2" in out
    assert "PASS  H3" in out
    assert "FAIL  H4" in out and "expected status 201, got 200" in out
    assert "FAIL  H5" in out and "body does not contain: absent text" in out
    assert "FAIL  H6" in out and "body is not equal to: hello" in out
    assert "FAIL  H7" in out and "expected a 2xx status, got 404" in out
    assert r.returncode == 1


# --- export_main -------------------------------------------------------------

def test_export_main_exports_files(repo):
    r = repo.run('check E1 export export_main "$SDD_TMP/main"\n'
                 'check E2 content grep -q v1 "$SDD_TMP/main/src/app.py"\nsdd_finish\n')
    assert r.returncode == 0, r.stdout


def test_export_main_fails_on_empty_archive(repo):
    repo.git("checkout", "-q", "--orphan", "empty")
    repo.git("rm", "-rq", "--cached", ".")
    repo.git("commit", "-q", "--allow-empty", "-m", "empty")
    r = repo.run('check E1 export export_main "$SDD_TMP/main" empty\nsdd_finish\n')
    assert r.returncode == 1
    assert "is empty" in r.stdout


def test_export_main_fails_on_missing_ref(repo):
    r = repo.run('check E1 export export_main "$SDD_TMP/main" nosuchref\nsdd_finish\n')
    assert r.returncode == 1
    assert "no such ref" in r.stdout


# --- run_suite ---------------------------------------------------------------

def test_run_suite_green_twice(repo):
    r = repo.run('check S1 suite run_suite true\nsdd_finish\n')
    assert r.returncode == 0
    assert "suite: 2 runs green" in r.stdout


def test_run_suite_names_failed_tests(repo):
    repo.write("fake_suite.sh", 'echo "FAILED tests/test_a.py::test_x - assert 0"; exit 1\n')
    r = repo.run('check S1 suite run_suite bash fake_suite.sh\nsdd_finish\n')
    assert r.returncode == 1
    assert "failed in both runs: tests/test_a.py::test_x; flaky: none" in r.stdout


def test_run_suite_flags_flaky_test(repo):
    counter = repo.path.parent / "count"
    repo.write("fake_suite.sh",
               f'n=$(cat {counter} 2>/dev/null || echo 0); echo $((n + 1)) > {counter}\n'
               'if [ "$n" -eq 0 ]; then echo "FAILED tests/test_b.py::test_t"; exit 1; fi\n')
    r = repo.run('check S1 suite run_suite bash fake_suite.sh\nsdd_finish\n')
    assert r.returncode == 1
    assert "flaky: tests/test_b.py::test_t" in r.stdout


# --- full_once ---------------------------------------------------------------

def full_once_run(repo):
    counter = repo.path.parent / "runs"
    body = f'check F1 full full_once bash -c "echo x >> {counter}"\nsdd_finish\n'
    r = repo.run(body)
    assert r.returncode == 0, r.stdout
    return len(counter.read_text().splitlines()) if counter.exists() else 0, r.stdout


def test_full_once_skips_same_tree_and_reruns_after_change(repo):
    assert full_once_run(repo)[0] == 1
    runs, out = full_once_run(repo)
    assert runs == 1 and "skipped: already green" in out
    repo.write("docs/notes.md", "doc change only\n")
    assert full_once_run(repo)[0] == 1
    repo.write("src/app.py", "print('v2')\n")
    assert full_once_run(repo)[0] == 2


def test_full_once_does_not_record_failure(repo):
    counter = repo.path.parent / "runs"
    body = f'check F1 full full_once bash -c "echo x >> {counter}; exit 1"\nsdd_finish\n'
    assert repo.run(body).returncode == 1
    assert repo.run(body).returncode == 1
    assert len(counter.read_text().splitlines()) == 2


def test_full_once_quick_skips(repo):
    r = repo.run('check F1 full full_once false\nsdd_finish\n', "--quick")
    assert r.returncode == 0
    assert "skipped: --quick" in r.stdout


# --- assert_absent -----------------------------------------------------------

def test_assert_absent_passes_with_matching_proof(repo):
    repo.write("app.log", "all fine\n")
    r = repo.run("check A1 clean assert_absent 'Traceback' app.log --proof 'Traceback (most recent'\n"
                 "sdd_finish\n")
    assert r.returncode == 0, r.stdout


def test_assert_absent_fails_when_proof_does_not_match(repo):
    repo.write("app.log", "all fine\n")
    r = repo.run("check A1 clean assert_absent 'Trace back' app.log --proof 'Traceback (most'\n"
                 "sdd_finish\n")
    assert r.returncode == 1
    assert "proof sample does not match" in r.stdout


def test_assert_absent_fails_when_found_or_missing(repo):
    repo.write("logs/app.log", "Traceback (most recent call last):\n")
    r = repo.run("check A1 found assert_absent 'Traceback' logs --proof 'Traceback'\n"
                 "check A2 missing assert_absent 'Traceback' nolog.txt --proof 'Traceback'\n"
                 "sdd_finish\n")
    assert r.returncode == 1
    assert "FAIL  A1" in r.stdout and "found /Traceback/" in r.stdout
    assert "FAIL  A2" in r.stdout and "does not exist" in r.stdout


def test_assert_absent_proof_file(repo):
    repo.write("sample.txt", "sk-abc\n")
    repo.write("app.log", "clean\n")
    r = repo.run("check A1 key assert_absent 'sk-[a-z]+' app.log --proof-file sample.txt\n"
                 "check A2 key assert_absent 'zz' app.log --proof-file sample.txt\nsdd_finish\n")
    assert "PASS  A1" in r.stdout and "FAIL  A2" in r.stdout


def test_assert_absent_fails_on_empty_target_unless_allowed(repo):
    repo.write("empty.log", "")
    (repo.path / "emptydir").mkdir()
    r = repo.run("check A1 file assert_absent 'Traceback' empty.log --proof 'Traceback'\n"
                 "check A2 dir assert_absent 'Traceback' emptydir --proof 'Traceback'\n"
                 "check A3 allowed assert_absent 'Traceback' empty.log --proof 'Traceback' "
                 "--allow-empty\n"
                 "sdd_finish\n")
    assert "FAIL  A1" in r.stdout and "is empty" in r.stdout, r.stdout
    assert "FAIL  A2" in r.stdout
    assert "PASS  A3" in r.stdout
    assert r.returncode == 1


# --- prove_red ---------------------------------------------------------------

def test_prove_red_new_test_fails_on_base(repo):
    repo.git("checkout", "-q", "-b", "feature/x")
    repo.write("src/app.py", "print('v2')\n")
    repo.write("tests/check_v2.sh", 'grep -q v2 src/app.py\n')
    r = repo.run("check R1 red prove_red --base main --timeout 10 --files tests/check_v2.sh "
                 "-- bash tests/check_v2.sh\nsdd_finish\n")
    assert r.returncode == 0, r.stdout
    assert "red on main as expected" in r.stdout


def test_prove_red_fails_when_test_passes_on_base(repo):
    repo.write("tests/check_v1.sh", 'grep -q v1 src/app.py\n')
    r = repo.run("check R1 red prove_red --base main --timeout 10 --files tests/check_v1.sh "
                 "-- bash tests/check_v1.sh\nsdd_finish\n")
    assert r.returncode == 1
    assert "does not catch the bug" in r.stdout


def test_prove_red_timeout_is_not_red(repo):
    r = repo.run("check R1 red prove_red --base main --timeout 1 -- sleep 30\nsdd_finish\n")
    assert r.returncode == 1
    assert "timed out" in r.stdout


# --- suite_lock --------------------------------------------------------------

def test_suite_lock_acquired_when_free(repo):
    r = repo.run("suite_lock 1\ncheck T1 ok true\nsdd_finish\n")
    assert r.returncode == 0, r.stdout + r.stderr


def test_suite_lock_times_out_when_held(repo):
    lock = repo.path / ".git" / "sdd-suite.lock"
    holder = subprocess.Popen(["flock", str(lock), "sleep", "30"])
    try:
        deadline = time.time() + 5
        while time.time() < deadline:
            if subprocess.run(["flock", "-n", str(lock), "true"]).returncode != 0:
                break
            time.sleep(0.05)
        r = repo.run("suite_lock 1 || exit 7\ncheck T1 ok true\nsdd_finish\n")
    finally:
        holder.kill()
        holder.wait()
    assert r.returncode == 7
    assert "still held" in r.stderr


# --- the example validate.sh in the feature-spec skill ------------------------

def test_skill_example_validate_sh_runs(repo):
    doc = (LIB.parent / "skills/feature-spec/validate-sh.md").read_text(encoding="utf-8")
    example = doc.split("```bash\n", 1)[1].split("```", 1)[0]
    for lib in ("sdd_check.sh", "sdd_probe.sh"):
        repo.write(f".claude/lib/{lib}", (LIB / lib).read_text(encoding="utf-8"))
    repo.write("tests/test_ok.py", "def test_ok():\n    assert True\n")
    script = repo.write("Plans/x/validate.sh", example)
    env = dict(repo.env, PYTHONDONTWRITEBYTECODE="1")

    def run():
        return subprocess.run(["bash", str(script)], cwd="/", env=env,
                              capture_output=True, text=True, timeout=120)

    first = run()
    assert first.returncode == 0, first.stdout + first.stderr
    assert "PASS  T1  test suite  (exit 0: green on code tree" in first.stdout
    assert "PASS  T3" in first.stdout
    assert "SKIP  L1" in first.stdout
    second = run()
    assert "skipped: already green" in second.stdout
