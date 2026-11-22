# validate.sh

Every automated check from `validation.md` as one bash script, written with
the spec and approved with it. It lives in the spec folder, so it is not
code and needs no `#spec-ok`. The owner can rerun it at any time.

## Writing it

- It runs from the repo root: `bash Plans/<dir>/validate.sh`.
- One `PASS`/`FAIL` line per check: the check's name and short evidence
  (exit code, key line). Non-zero exit if any check fails.
- Go through the automated bullets of `validation.md` one by one and name
  the `validate.sh` check (or the test module it runs) that covers each.
- A "there is no X" claim (no error message, no connection, no key in the
  log) proves something only if it once failed on a real X: the pattern
  must match what the system actually prints.
- A failed test run's evidence names the failed tests (pytest: the `FAILED`
  lines of `-rf`), so finding them needs no second full run.
- Its own temp dir, removed at the end.
- Background processes it starts (servers, stub APIs) are stopped at exit,
  failed runs included. Start them in the main shell, never inside
  `$(...)`, where the PID is lost and the process outlives the script.
- A server it starts gets a free port (for example Python `socket` port 0),
  never a fixed one: a server left behind on a fixed port could answer
  instead of the fresh code.
- Stop a server or background process by its own PID, never with
  `pkill -f <pattern>`: the pattern also matches the stopping command's own
  line and kills it.
- Live, paid or networked checks only behind an opt-in switch: `--live`
  loads the project's documented local settings itself and sets the live
  switch, so nothing has to be exported by hand.
- Local, git-ignored settings it needs (such as live sample paths, never
  secrets) come from a file the project documents. API keys come from the
  environment or the key store named in `tech-stack.md`.
- It finds its own folder with `$(dirname "$0")` and never hard-codes
  `Plans/<dir>`, so it still runs after the spec moves to `Plans/done/`.
- A test never names the spec folder (`Plans/<dir>/...`): the archive move
  breaks it. A helper script in the spec folder (a measurement, a probe)
  takes the repo root from the working directory or `git rev-parse
  --show-toplevel`, never from its own place (`parents[n]`).
- A check that compares with `main`'s code exports it from the repo
  (`git -C "$ROOT" archive main`, never from a temp dir) and first checks
  that the copy is not empty, so the comparison cannot silently match the
  branch with itself.
- It takes a `--quick` switch that skips the full test suite and the
  repeated or load runs, for the rerun after the archive move when the code
  has not changed since the last full pass.

## Before handing over the spec

- Run `bash -n` and `shellcheck` on it (via `docker run --rm -v
  "$PWD:/mnt" -w /mnt koalaman/shellcheck:stable` when shellcheck is not
  installed) and fix what they report: an error such as an unset variable
  under `set -u` otherwise stays hidden until the first check that reaches
  it.
- Run its offline part once: a `FAIL` because the new code is missing is
  expected, but every tool it calls must accept its flags and every summary
  it greps must appear.
- Open every live URL it uses once (status and final host after
  redirects): a page behind a login otherwise fails only at validation.

## At validation

- The approved `validate.sh` is part of the spec: read it before changing
  it, extend it rather than replace it, and record under "Döntések" what
  was added or dropped.
- Run the full test suite a second time: a test that fails in only one run
  is flaky; find its cause (often a time upper bound) before calling the
  checks passed.
- Order the runs so the full suite runs as few times as possible: run the
  probes and their fix rounds first; after each fix round run only the test
  modules it touches (plus lint and types), never the full suite. Run
  `validate.sh` (with the full suite, plus the second suite run) once, on
  the final commit, after the last fix; a later code change means one more
  full run, a docs-only change does not.
- While `validate.sh` or the full test suite runs, no heavy build, live test
  or subagent probe runs in parallel: the load can fail time-dependent
  tests.
