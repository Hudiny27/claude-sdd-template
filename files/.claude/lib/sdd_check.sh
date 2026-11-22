# shellcheck shell=bash
# sdd_check.sh: shared library for a feature's validate.sh.
#
# Template-owned: `install.sh --update` overwrites it. Do not edit it in a
# project; propose missing features in the template's backlog/ instead.
#
# Usage (from Plans/<dir>/validate.sh):
#   source "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/.claude/lib/sdd_check.sh"
#   sdd_init "$@"
#   check T1 "unit tests" full_once run_suite python3 -m pytest -q -rf
#   sdd_finish
#
# Variables set by sdd_init:
#   SDD_ROOT   repository root (the working directory after sdd_init)
#   SDD_DIR    absolute folder of the calling script (never hard-code Plans/<dir>)
#   SDD_TMP    private temp dir, removed at exit
#   SDD_LIVE   1 with --live, else 0
#   SDD_QUICK  1 with --quick, else 0
#   SDD_ARGS   the remaining arguments (array)
#
# With --live, .claude/local.env is loaded if present: git-ignored KEY=value
# lines for local settings (sample paths, hosts). Never secrets: API keys come
# from the environment or the key store named in specs/tech-stack.md.
#
# File descriptor 9 is reserved for suite_lock. Do not set your own EXIT trap.
# A script that exits before sdd_finish (errexit outside check, an explicit
# exit, a signal, or no sdd_finish at all) still prints a FAIL line and the
# SUMMARY, and exits non-zero.

SDD_PASSED=0
SDD_FAILED=0
SDD_SKIPPED=0
SDD_FAILED_IDS=()
SDD_SEEN_IDS=" "
SDD_BG_PIDS=()
SDD_BG_NAMES=()
SDD_LIVE=0
SDD_QUICK=0
SDD_ARGS=()
SDD_TMP=""
SDD_FINISHED=0

# Print an error to stderr, prefixed with the library name.
_sdd_err() { printf 'sdd_check: %s\n' "$*" >&2; }

# One-line, length-limited evidence from a log file: its last non-empty line.
_sdd_evidence() {
  local line
  line="$(grep -v '^[[:space:]]*$' "$1" 2>/dev/null | tail -n 1 || true)"
  line="${line//$'\t'/ }"
  [ "${#line}" -gt 160 ] && line="${line:0:157}..."
  printf '%s' "${line:-no output}"
}

_sdd_summary() {
  echo "----"
  printf 'SUMMARY: %d passed, %d failed, %d skipped\n' "$SDD_PASSED" "$SDD_FAILED" "$SDD_SKIPPED"
  [ "$SDD_FAILED" -gt 0 ] && printf 'FAILED: %s\n' "${SDD_FAILED_IDS[*]}"
  return 0
}

_sdd_cleanup() {
  local rc=$? cmd="$BASH_COMMAND" i pid
  if [ "$SDD_FINISHED" -eq 0 ]; then
    SDD_FAILED=$((SDD_FAILED + 1))
    SDD_FAILED_IDS+=("EXIT")
    if [ "$rc" -eq 0 ]; then
      printf 'FAIL  EXIT  script ended without sdd_finish\n'
      rc=1
    else
      printf 'FAIL  EXIT  script stopped early (exit %s at: %s)\n' "$rc" "${cmd:0:120}"
    fi
    _sdd_summary
  fi
  for ((i = ${#SDD_BG_PIDS[@]} - 1; i >= 0; i--)); do
    pid="${SDD_BG_PIDS[$i]}"
    [ -n "$pid" ] || continue
    kill -0 "$pid" 2>/dev/null || continue
    # start_bg puts each process in its own process group: stop the group.
    kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  done
  for ((i = ${#SDD_BG_PIDS[@]} - 1; i >= 0; i--)); do
    pid="${SDD_BG_PIDS[$i]}"
    [ -n "$pid" ] || continue
    local n=0
    while kill -0 "$pid" 2>/dev/null && [ "$n" -lt 50 ]; do
      sleep 0.1
      n=$((n + 1))
    done
    if kill -0 "$pid" 2>/dev/null; then
      _sdd_err "background '${SDD_BG_NAMES[$i]}' (pid $pid) ignored SIGTERM; sending SIGKILL"
      kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
  done
  if [ -n "$SDD_TMP" ] && [ -d "$SDD_TMP" ]; then
    rm -rf -- "$SDD_TMP"
  fi
  return "$rc"
}

# sdd_init "$@": enter the repo root, strict mode, switches, temp dir, traps.
sdd_init() {
  local caller="${BASH_SOURCE[1]:-$0}"
  SDD_DIR="$(cd "$(dirname "$caller")" && pwd)"
  SDD_ROOT="$(git -C "$SDD_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    _sdd_err "$SDD_DIR is not inside a git repository"
    exit 2
  }
  cd "$SDD_ROOT" || exit 2
  set -euo pipefail
  local arg
  for arg in "$@"; do
    case "$arg" in
      --live) SDD_LIVE=1 ;;
      --quick) SDD_QUICK=1 ;;
      *) SDD_ARGS+=("$arg") ;;
    esac
  done
  if [ "$SDD_LIVE" -eq 1 ] && [ -f "$SDD_ROOT/.claude/local.env" ]; then
    set -a
    # shellcheck source=/dev/null
    . "$SDD_ROOT/.claude/local.env"
    set +a
    echo "sdd: loaded .claude/local.env"
  fi
  SDD_TMP="$(mktemp -d "${TMPDIR:-/tmp}/sdd-check.XXXXXX")"
  trap _sdd_cleanup EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM
  export SDD_ROOT SDD_DIR SDD_TMP SDD_LIVE SDD_QUICK
}

# check ID NAME CMD...: run CMD (a command or function, errexit on inside),
# print one PASS/FAIL line with short evidence, remember a failure, continue.
check() {
  if [ "$#" -lt 3 ]; then
    _sdd_err "usage: check ID NAME CMD..."
    SDD_FAILED=$((SDD_FAILED + 1))
    SDD_FAILED_IDS+=("?")
    return 0
  fi
  local id="$1" name="$2" log rc opts="$-"
  shift 2
  if [[ "$SDD_SEEN_IDS" == *" $id "* ]]; then
    _sdd_err "duplicate check id: $id"
  fi
  SDD_SEEN_IDS+="$id "
  log="$SDD_TMP/check-$id.log"
  set +e
  ( set -e; "$@" ) >"$log" 2>&1
  rc=$?
  [[ "$opts" == *e* ]] && set -e
  if [ "$rc" -eq 0 ]; then
    SDD_PASSED=$((SDD_PASSED + 1))
    printf 'PASS  %s  %s  (exit 0: %s)\n' "$id" "$name" "$(_sdd_evidence "$log")"
  else
    SDD_FAILED=$((SDD_FAILED + 1))
    SDD_FAILED_IDS+=("$id")
    printf 'FAIL  %s  %s  (exit %s: %s)\n' "$id" "$name" "$rc" "$(_sdd_evidence "$log")"
    tail -n 15 "$log" | sed 's/^/      | /'
  fi
  return 0
}

# live_only [check ID NAME CMD...]: run the rest only with --live, else
# print a SKIP line. Without arguments: succeed only with --live.
live_only() {
  if [ "$SDD_LIVE" -eq 1 ]; then
    [ "$#" -eq 0 ] && return 0
    "$@"
    return
  fi
  [ "$#" -eq 0 ] && return 1
  SDD_SKIPPED=$((SDD_SKIPPED + 1))
  if [ "$1" = "check" ] && [ "$#" -ge 3 ]; then
    printf 'SKIP  %s  %s  (needs --live)\n' "$2" "$3"
  else
    printf 'SKIP  %s  (needs --live)\n' "$*"
  fi
  return 0
}

# sdd_finish: print the summary; exit non-zero on any failure or if no check ran.
sdd_finish() {
  local total=$((SDD_PASSED + SDD_FAILED + SDD_SKIPPED))
  SDD_FINISHED=1
  _sdd_summary
  [ "$SDD_FAILED" -gt 0 ] && exit 1
  if [ "$total" -eq 0 ]; then
    echo "FAILED: no check ran"
    exit 1
  fi
  exit 0
}

# start_bg NAME CMD...: start CMD in the background in its own process group;
# its stdout and stderr both go to $SDD_TMP/NAME.log. Sets SDD_BG_PID. The
# EXIT trap stops it by PID (process group), failed runs included; stop_bg
# stops it earlier. Call it in the main shell only.
start_bg() {
  if [ "$#" -lt 2 ]; then
    _sdd_err "usage: start_bg NAME CMD..."
    return 2
  fi
  if [ "${BASHPID:-$$}" != "$$" ]; then
    _sdd_err "start_bg must run in the main shell, not inside \$(...), a pipe or check"
    return 2
  fi
  local name="$1"
  shift
  set -m
  "$@" >"$SDD_TMP/$name.log" 2>&1 9>&- &
  SDD_BG_PID=$!
  set +m
  SDD_BG_PIDS+=("$SDD_BG_PID")
  SDD_BG_NAMES+=("$name")
  echo "sdd: started $name (pid $SDD_BG_PID, log \$SDD_TMP/$name.log)"
}

# stop_bg NAME: stop the process start_bg started as NAME (SIGTERM to its
# process group, SIGKILL after 5s) and wait for it, so NAME.log is complete
# before you check it. A process that buffers stdout loses the unflushed part
# on SIGTERM: run it unbuffered (python3 -u). Call it in the main shell only.
stop_bg() {
  local name="${1:-}" i pid n=0 rc=0
  if [ "${BASHPID:-$$}" != "$$" ]; then
    _sdd_err "stop_bg must run in the main shell, not inside \$(...), a pipe or check"
    return 2
  fi
  for ((i = ${#SDD_BG_NAMES[@]} - 1; i >= 0; i--)); do
    [ "${SDD_BG_NAMES[$i]}" = "$name" ] && [ -n "${SDD_BG_PIDS[$i]}" ] && break
  done
  if [ -z "$name" ] || [ "$i" -lt 0 ]; then
    _sdd_err "stop_bg: no background process named $name"
    return 2
  fi
  pid="${SDD_BG_PIDS[$i]}"
  kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  while kill -0 "$pid" 2>/dev/null && [ "$n" -lt 50 ]; do
    sleep 0.1
    n=$((n + 1))
  done
  if kill -0 "$pid" 2>/dev/null; then
    _sdd_err "background '$name' (pid $pid) ignored SIGTERM; sending SIGKILL"
    kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
  fi
  wait "$pid" 2>/dev/null || rc=$?
  SDD_BG_PIDS[i]=""
  echo "sdd: stopped $name (pid $pid, exit status $rc)"
}

# free_port: print a TCP port that is free on 127.0.0.1 right now.
free_port() {
  command -v python3 >/dev/null 2>&1 || { _sdd_err "free_port needs python3"; return 1; }
  python3 -c 'import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()'
}

# wait_port PORT [SECONDS]: wait until something listens on 127.0.0.1:PORT.
wait_port() {
  local port="$1" limit="${2:-10}" n=0
  while ! (exec 3<>"/dev/tcp/127.0.0.1/$port") 2>/dev/null; do
    n=$((n + 1))
    if [ "$n" -ge $((limit * 10)) ]; then
      _sdd_err "nothing listens on port $port after ${limit}s"
      return 1
    fi
    sleep 0.1
  done
}

# export_main DIR [REF]: export REF (default main) from the repo into DIR
# with git archive; fail if the export is empty.
export_main() {
  local dir="$1" ref="${2:-main}"
  mkdir -p "$dir"
  if ! git -C "$SDD_ROOT" rev-parse --verify -q "$ref^{commit}" >/dev/null; then
    _sdd_err "export_main: no such ref: $ref"
    return 1
  fi
  if [ -z "$(git -C "$SDD_ROOT" ls-tree --name-only "$ref" | head -n 1)" ]; then
    _sdd_err "export_main: the export of $ref into $dir is empty"
    return 1
  fi
  git -C "$SDD_ROOT" archive --format=tar "$ref" | python3 -c '
import sys, tarfile
with tarfile.open(fileobj=sys.stdin.buffer, mode="r|") as t:
    t.extractall(sys.argv[1])
' "$dir"
  if [ -z "$(ls -A "$dir")" ]; then
    _sdd_err "export_main: the export of $ref into $dir is empty"
    return 1
  fi
  echo "exported $ref ($(git -C "$SDD_ROOT" rev-parse --short "$ref")) to $dir"
}

# Failed test names from a pytest-style log (lines "FAILED <nodeid> ...").
_sdd_failed_names() {
  grep -E '^(FAILED|ERROR) ' "$1" 2>/dev/null | cut -d' ' -f2 | sort -u || true
}

# run_suite CMD...: run the test suite twice; report failed test names (from
# pytest-style FAILED lines, so use -rf) and flag tests failing in only one
# run as flaky. Fails if either run fails.
run_suite() {
  local dir rc1=0 rc2=0 f1 f2 flaky both
  dir="$(mktemp -d "$SDD_TMP/suite.XXXXXX")"
  "$@" >"$dir/run1.log" 2>&1 || rc1=$?
  "$@" >"$dir/run2.log" 2>&1 || rc2=$?
  tail -n 5 "$dir/run2.log"
  if [ "$rc1" -eq 0 ] && [ "$rc2" -eq 0 ]; then
    echo "suite: 2 runs green"
    return 0
  fi
  f1="$(_sdd_failed_names "$dir/run1.log")"
  f2="$(_sdd_failed_names "$dir/run2.log")"
  both="$(comm -12 <(printf '%s\n' "$f1") <(printf '%s\n' "$f2") | grep -v '^$' | paste -sd' ' - || true)"
  flaky="$(comm -3 <(printf '%s\n' "$f1") <(printf '%s\n' "$f2") | tr -d '\t' | grep -v '^$' | paste -sd' ' - || true)"
  if [ "$rc1" -ne "$rc2" ] && [ -z "$flaky" ]; then
    flaky="(one run failed: exit $rc1 then $rc2; no FAILED lines to name the tests)"
  fi
  echo "suite failed (exit $rc1, $rc2); failed in both runs: ${both:-none named}; flaky: ${flaky:-none}"
  return 1
}

# Hash of the code in the working tree: the content of tracked and
# untracked-not-ignored files, without the paths the guard does not count
# as code (specs/, Plans/, docs/, .claude/, .githooks/, *.md, .gitignore).
_sdd_code_hash() {
  (
    cd "$SDD_ROOT" || exit 1
    git ls-files -co --exclude-standard -z -- . ':!specs/' ':!Plans/' ':!docs/' \
      ':!.claude/' ':!.githooks/' ':!*.md' ':!.gitignore' \
      | sort -zu \
      | while IFS= read -r -d '' f; do
          [ -f "$f" ] && printf '%s\0' "$f"
        done \
      | xargs -0 -r sha256sum
  ) | sha256sum | cut -c1-16
}

# full_once CMD...: run CMD unless the same code tree already had a green
# run of the same command (cache under .git/). --quick skips it outright.
full_once() {
  local cache key hash
  if [ "$SDD_QUICK" -eq 1 ]; then
    echo "skipped: --quick"
    return 0
  fi
  cache="$(git -C "$SDD_ROOT" rev-parse --git-path sdd-full-once.cache)"
  case "$cache" in /*) ;; *) cache="$SDD_ROOT/$cache" ;; esac
  hash="$(_sdd_code_hash)"
  key="$hash $(printf '%s ' "$@" | sha256sum | cut -c1-16)"
  if [ -f "$cache" ] && grep -qxF "$key" "$cache"; then
    echo "skipped: already green on code tree $hash"
    return 0
  fi
  "$@" || return
  echo "$key" >>"$cache"
  echo "green on code tree $hash (recorded)"
}

# check_url URL [--host HOST]: HTTP status and final host after redirects;
# fails on a non-2xx status or, with --host, on a different final host.
check_url() {
  local url="$1" want="" out code final host
  [ "${2:-}" = "--host" ] && want="${3:-}"
  out="$(curl -sS -L -o /dev/null --max-time 20 -w '%{http_code} %{url_effective}' "$url")" || {
    _sdd_err "check_url: curl failed for $url"
    return 1
  }
  code="${out%% *}"
  final="${out#* }"
  host="${final#*://}"
  host="${host%%/*}"
  host="${host##*@}"
  host="${host%%:*}"
  echo "$url -> $code $host ($final)"
  case "$code" in 2??) ;; *) return 1 ;; esac
  if [ -n "$want" ] && [ "$host" != "$want" ]; then
    _sdd_err "check_url: final host $host, expected $want"
    return 1
  fi
}

# check_http URL [--status N] [--body-contains TEXT] [--body-equals TEXT]:
# one GET without following redirects; fails unless the status is N (default:
# any 2xx) and the body contains TEXT / equals TEXT (trailing newlines
# ignored). Prints the status, body size and the first 80 characters of the
# body. For a live URL's status and final host after redirects: check_url.
check_http() {
  local url="${1:-}" want="" contains="" equals="" has_c=0 has_e=0 file code body preview
  if [ -z "$url" ]; then
    echo "usage: check_http URL [--status N] [--body-contains TEXT] [--body-equals TEXT]"
    return 2
  fi
  shift
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --status) want="${2:-}"; shift 2 || shift ;;
      --body-contains) contains="${2:-}"; has_c=1; shift 2 || shift ;;
      --body-equals) equals="${2:-}"; has_e=1; shift 2 || shift ;;
      *) echo "check_http: unknown option $1"; return 2 ;;
    esac
  done
  file="$(mktemp "${SDD_TMP:-${TMPDIR:-/tmp}}/http.XXXXXX")"
  code="$(curl -sS -o "$file" --max-time 20 -w '%{http_code}' "$url")" || {
    rm -f -- "$file"
    echo "check_http: curl failed for $url"
    return 1
  }
  body="$(tr -d '\000' <"$file")"
  preview="${body:0:80}"
  preview="${preview//[$'\n\r\t']/ }"
  echo "GET $url -> $code, $(wc -c <"$file" | tr -d ' ') bytes: ${preview:-(empty body)}"
  rm -f -- "$file"
  if [ -n "$want" ]; then
    [ "$code" = "$want" ] || { echo "expected status $want, got $code"; return 1; }
  else
    case "$code" in 2??) ;; *) echo "expected a 2xx status, got $code"; return 1 ;; esac
  fi
  if [ "$has_c" -eq 1 ] && [[ "$body" != *"$contains"* ]]; then
    echo "body does not contain: $contains"
    return 1
  fi
  if [ "$has_e" -eq 1 ] && [ "$body" != "$equals" ]; then
    echo "body is not equal to: $equals"
    return 1
  fi
  return 0
}

# assert_absent PATTERN TARGET --proof SAMPLE | --proof-file FILE [--allow-empty]:
# "there is no PATTERN in TARGET" (file or folder, grep -E), valid only if
# PATTERN first matches the known positive SAMPLE. Fails on a missing TARGET,
# and on an empty one (a file of 0 bytes, a folder without a non-empty file)
# unless --allow-empty is given. A log of a start_bg process: stop_bg first.
assert_absent() {
  local usage="usage: assert_absent PATTERN TARGET --proof SAMPLE | --proof-file FILE [--allow-empty]"
  local pattern="${1:-}" target="${2:-}" hit mode="" proof="" allow_empty=0
  if [ "$#" -lt 2 ]; then
    echo "$usage"
    return 2
  fi
  shift 2
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --proof|--proof-file) mode="$1"; proof="${2:-}"; shift 2 || shift ;;
      --allow-empty) allow_empty=1; shift ;;
      *) echo "$usage"; return 2 ;;
    esac
  done
  case "$mode" in
    --proof)
      printf '%s\n' "$proof" | grep -qE -- "$pattern" || {
        echo "proof sample does not match /$pattern/: the absence would prove nothing"
        return 1
      } ;;
    --proof-file)
      grep -qE -- "$pattern" "${proof:-/dev/null}" || {
        echo "proof file $proof does not match /$pattern/: the absence would prove nothing"
        return 1
      } ;;
    *)
      echo "$usage"
      return 2 ;;
  esac
  if [ ! -e "$target" ]; then
    echo "target $target does not exist"
    return 1
  fi
  if [ "$allow_empty" -eq 0 ] && [ -z "$(find "$target" -type f -size +0c -print -quit 2>/dev/null)" ]; then
    echo "target $target is empty: the absence would prove nothing (--allow-empty if expected)"
    return 1
  fi
  hit="$(grep -rnE -- "$pattern" "$target" | head -n 1 || true)"
  if [ -n "$hit" ]; then
    echo "found /$pattern/: $hit"
    return 1
  fi
  echo "absent: /$pattern/ in $target (proof sample matched)"
}

# prove_red --base REF --timeout S [--files PATH...] -- CMD...: the new test
# must fail on the old code. Exports REF to a temp dir, copies PATH... (the
# new test files) from the working tree into it, runs CMD there alone with a
# timeout, and succeeds only if CMD fails (a timeout does not count).
prove_red() {
  local base="" limit="" files=() dir rc f
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --base) base="$2"; shift 2 ;;
      --timeout) limit="$2"; shift 2 ;;
      --files) shift
        while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do files+=("$1"); shift; done ;;
      --) shift; break ;;
      *) echo "prove_red: unknown option $1"; return 2 ;;
    esac
  done
  if [ -z "$base" ] || [ -z "$limit" ] || [ "$#" -eq 0 ]; then
    echo "usage: prove_red --base REF --timeout S [--files PATH...] -- CMD..."
    return 2
  fi
  dir="$(mktemp -d "$SDD_TMP/red.XXXXXX")"
  export_main "$dir" "$base" >/dev/null || return 1
  for f in ${files[@]+"${files[@]}"}; do
    mkdir -p "$dir/$(dirname "$f")"
    cp -p "$SDD_ROOT/$f" "$dir/$f"
  done
  rc=0
  (cd "$dir" && timeout "$limit" "$@") >"$dir.log" 2>&1 || rc=$?
  tail -n 5 "$dir.log"
  if [ "$rc" -eq 124 ]; then
    echo "timed out after ${limit}s on $base: not a proof of red"
    return 1
  fi
  if [ "$rc" -eq 0 ]; then
    echo "passed on $base: the test does not catch the bug"
    return 1
  fi
  echo "red on $base as expected (exit $rc)"
}

# suite_lock [SECONDS]: hold a repo-wide lock (fd 9) until the script exits,
# so suite, live and probe runs do not overlap. Waits SECONDS (default 3600).
suite_lock() {
  local limit="${1:-3600}" common lock
  common="$(cd "$SDD_ROOT" && cd "$(git rev-parse --git-common-dir)" && pwd)"
  lock="$common/sdd-suite.lock"
  exec 9>"$lock"
  if ! flock -n 9; then
    echo "sdd: waiting for the suite lock ($lock)"
    flock -w "$limit" 9 || { _sdd_err "suite lock still held after ${limit}s"; return 1; }
  fi
}
