# validate.sh

Every automated check from `validation.md` (S and M: the agent lines of the
`spec.md` "Ellenőrzés" section, which also name the command
`bash Plans/<dir>/validate.sh`) as one bash script, written with the spec
and approved with it. It lives in the spec folder, so it is not
code and needs no `#spec-ok`. The owner can rerun it at any time.

It sources the template library `.claude/lib/sdd_check.sh`; each
function's contract is in the comment above it. A small check-specific
shell function in `validate.sh` is fine. What the library is for is not
reimplemented locally: ports, background processes, cleanup, temp dirs,
suite runs, the export of `main`. A missing reusable piece goes as a
proposal to the template's `backlog/`.

## Example

```bash
#!/usr/bin/env bash
# shellcheck source=/dev/null
source "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/.claude/lib/sdd_check.sh"
sdd_init "$@"
suite_lock
check T1 "test suite" full_once run_suite python3 -m pytest -q -rf
PORT="$(free_port)"
start_bg web python3 -u -m http.server "$PORT" --bind 127.0.0.1
check T2 "server starts" wait_port "$PORT"
check T3 "index page" check_http "http://127.0.0.1:$PORT/" \
  --status 200 --body-contains "Directory listing"
check T4 "unknown page is 404" check_http "http://127.0.0.1:$PORT/nope" --status 404
stop_bg web
check T5 "no traceback in the server log" \
  assert_absent 'Traceback' "$SDD_TMP/web.log" --proof 'Traceback (most recent call last):'
live_only check L1 "live API smoke test" python3 scripts/live_smoke.py
sdd_finish
```

## Writing it

- Start with `sdd_init "$@"`, end with `sdd_finish`; each check is one
  `check ID NAME CMD...` (a multi-step check is a shell function). A step
  that can fail runs inside `check`; outside it, errexit stops the script
  (the library still prints a `FAIL  EXIT` line and the summary).
- Go through the automated bullets of `validation.md` one by one and name
  the check ID (or the test module it runs) that covers each.
- A "there is no X" claim: use `assert_absent` with a proof sample of what
  the system really prints.
- The test suite: use `run_suite` (pytest with `-rf`) inside `full_once`,
  after `suite_lock`.
- Servers and stub APIs: use `free_port`, `start_bg` and `wait_port`
  (inside `check`). `start_bg NAME` writes stdout and stderr both to
  `$SDD_TMP/NAME.log`. Before asserting on that log, `stop_bg NAME`, so the
  log is complete; run the process unbuffered (`python3 -u`).
- A local HTTP response: use `check_http` (exact `--status`,
  `--body-contains`, `--body-equals`). A live URL's status and final host
  after redirects: use `check_url`.
- A comparison with `main`'s code: use `export_main`.
- Live, paid or networked checks: use `live_only`. Their local settings go
  in the git-ignored `.claude/local.env` (name its keys in the spec, never
  secrets); API keys come from the environment or the key store named in
  `tech-stack.md`.
- Use `$SDD_DIR` for the script's own folder and `$SDD_TMP` for temp files.
  A test never names the spec folder (`Plans/<dir>/...`): the archive move
  breaks it. The spec text may name it (the `bash Plans/<dir>/validate.sh`
  command): the archive step fixes those paths (`validate-feature/finish.md`).
  A helper script in the spec folder takes the repo root from
  `git rev-parse --show-toplevel`, never from its own place (`parents[n]`).

## Before handing over the spec

- Run `bash -n` and `shellcheck` on it (via `docker run --rm -v
  "$PWD:/mnt" -w /mnt koalaman/shellcheck:stable` when shellcheck is not
  installed) and fix what they report.
- Run its offline part once: a `FAIL` because the new code is missing is
  expected, but every tool it calls must accept its flags and every summary
  it greps must appear. A branch that cannot run before the new code exists
  (a server that does not start yet) is not faked with stub code; the spec
  names it, and the task group that adds the code (S/M: the implementation,
  before its commit) runs that check once.
- Open every live URL it uses once: use `check_url`.

## At validation

- The approved `validate.sh` is part of the spec: read it before changing
  it, extend it rather than replace it, and record under "Döntések" what
  was added or dropped.
- A test that `run_suite` flags as flaky: find its cause (often a time
  upper bound) before calling the checks passed.
- Run the probes and their fix rounds first; after each fix round run only
  the test modules it touches (plus lint and types). Run `validate.sh` on
  the final commit, after the last fix.
- No probe round runs while `validate.sh` runs: `suite_lock` only keeps
  scripts apart.
