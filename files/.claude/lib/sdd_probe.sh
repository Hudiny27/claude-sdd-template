# shellcheck shell=bash
# sdd_probe.sh: setup for fresh-subagent probes (and deep-review subagents).
#
# Template-owned: `install.sh --update` overwrites it. Do not edit it in a
# project; propose missing features in the template's backlog/ instead.
#
# Usage (from Plans/<dir>/prepare-probe.sh; any working directory):
#   source "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/.claude/lib/sdd_probe.sh"
#   probe_upgrade() { ...bring "$1" (the base copy) up to date, no paid step...; }
#   probe_regen()   { ...regenerate generated documents in "$1/repo"...; }
#   SDD_PROBE_ROOT=/abs/scratch/probes
#   probe_base samples/demo-project
#   probe_copy "$1" interactive     # prints the copy's path
#
# SDD_PROBE_ROOT must be an absolute folder outside the repository (the
# session scratchpad). A copy has this layout:
#   <copy>/repo     tracked and untracked-not-ignored files of the repository
#                   (ignored files, such as real data, stay out)
#   <copy>/sample   a copy of the base sample, if probe_base ran
# The hooks probe_upgrade and probe_regen are optional project functions.

_sdd_probe_err() { printf 'sdd_probe: %s\n' "$*" >&2; }

# The folder of the script that sourced this library: the repo is found from
# there, so the script works from any working directory.
_SDD_PROBE_CALLER_DIR="$(cd "$(dirname "${BASH_SOURCE[1]:-./x}")" && pwd)"

_sdd_probe_root() {
  if [ -n "${SDD_ROOT:-}" ]; then
    printf '%s' "$SDD_ROOT"
  else
    git -C "$_SDD_PROBE_CALLER_DIR" rev-parse --show-toplevel
  fi
}

# Check SDD_PROBE_ROOT: set, absolute, outside the repository.
_sdd_probe_scratch() {
  local root
  root="$(_sdd_probe_root)" || return 1
  case "${SDD_PROBE_ROOT:-}" in
    /*) ;;
    *) _sdd_probe_err "set SDD_PROBE_ROOT to an absolute scratch folder outside the repo"; return 1 ;;
  esac
  case "$SDD_PROBE_ROOT/" in
    "$root"/*) _sdd_probe_err "SDD_PROBE_ROOT ($SDD_PROBE_ROOT) is inside the repository"; return 1 ;;
  esac
  mkdir -p "$SDD_PROBE_ROOT"
}

# A path segment we may create and remove under SDD_PROBE_ROOT.
_sdd_probe_name_ok() {
  [[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]
}

# Content hash of a folder (paths and bytes).
_sdd_probe_hash() {
  (
    cd "$1" || exit 1
    find . -type f -print0 | sort -z | xargs -0 -r sha256sum
  ) | sha256sum | cut -c1-16
}

# probe_base SAMPLE: one up-to-date base copy of the sample project at
# $SDD_PROBE_ROOT/base, rebuilt only when the sample changed; the project
# hook probe_upgrade BASE runs on a fresh copy. Prints the base path.
probe_base() {
  local sample="$1" root base stamp want
  [ -n "$sample" ] || { _sdd_probe_err "usage: probe_base SAMPLE"; return 2; }
  _sdd_probe_scratch || return 1
  root="$(_sdd_probe_root)"
  case "$sample" in /*) ;; *) sample="$root/$sample" ;; esac
  [ -d "$sample" ] || { _sdd_probe_err "sample folder not found: $sample"; return 1; }
  base="$SDD_PROBE_ROOT/base"
  stamp="$SDD_PROBE_ROOT/base.stamp"
  want="$(_sdd_probe_hash "$sample")"
  if [ -d "$base" ] && [ -f "$stamp" ] && [ "$(cat "$stamp")" = "$want" ]; then
    printf '%s\n' "$base"
    return 0
  fi
  rm -rf -- "$base" "$stamp"
  cp -a "$sample" "$base"
  if declare -F probe_upgrade >/dev/null; then
    probe_upgrade "$base" >&2 || { _sdd_probe_err "probe_upgrade failed on $base"; return 1; }
  fi
  printf '%s\n' "$want" >"$stamp"
  printf '%s\n' "$base"
}

# probe_copy ROUND NAME: a fresh, full copy for one probe of one round at
# $SDD_PROBE_ROOT/round-ROUND/NAME (removed first if it exists), then the
# project hook probe_regen COPY. Prints the copy's path.
probe_copy() {
  local round="$1" name="$2" root dest
  if ! _sdd_probe_name_ok "$round" || ! _sdd_probe_name_ok "$name"; then
    _sdd_probe_err "usage: probe_copy ROUND NAME (letters, digits, . _ -)"
    return 2
  fi
  _sdd_probe_scratch || return 1
  root="$(_sdd_probe_root)"
  dest="$SDD_PROBE_ROOT/round-$round/$name"
  rm -rf -- "$dest"
  mkdir -p "$dest/repo"
  (
    cd "$root" || exit 1
    git ls-files -co --exclude-standard -z \
      | sort -zu \
      | while IFS= read -r -d '' f; do
          if [ -e "$f" ] || [ -L "$f" ]; then printf '%s\0' "$f"; fi
        done \
      | xargs -0 -r cp -P --parents -t "$dest/repo"
  ) || { _sdd_probe_err "copying the repository into $dest/repo failed"; return 1; }
  if [ -d "$SDD_PROBE_ROOT/base" ]; then
    cp -a "$SDD_PROBE_ROOT/base" "$dest/sample"
  fi
  if declare -F probe_regen >/dev/null; then
    probe_regen "$dest" >&2 || { _sdd_probe_err "probe_regen failed on $dest"; return 1; }
  fi
  printf '%s\n' "$dest"
}

_sdd_probe_snapshot_file() {
  if [ -n "${1:-}" ]; then
    printf '%s' "$1"
    return 0
  fi
  local root path
  root="$(_sdd_probe_root)" || return 1
  path="$(git -C "$root" rev-parse --git-path sdd-probe-status.snapshot)"
  case "$path" in /*) ;; *) path="$root/$path" ;; esac
  printf '%s' "$path"
}

# snapshot_status [FILE]: record `git status` before a probe or reviewer
# runs (default file under .git/).
snapshot_status() {
  local file root
  file="$(_sdd_probe_snapshot_file "${1:-}")" || return 1
  root="$(_sdd_probe_root)" || return 1
  git -C "$root" status --porcelain=v1 -uall | sort >"$file"
  echo "status snapshot: $(wc -l <"$file") entries"
}

# assert_no_new_files [FILE]: fail if `git status` shows an entry that was
# not in the snapshot (a file the probe or reviewer left in the repo).
assert_no_new_files() {
  local file root new
  file="$(_sdd_probe_snapshot_file "${1:-}")" || return 1
  [ -f "$file" ] || { _sdd_probe_err "no snapshot at $file: run snapshot_status first"; return 1; }
  root="$(_sdd_probe_root)" || return 1
  new="$(comm -13 "$file" <(git -C "$root" status --porcelain=v1 -uall | sort))"
  if [ -n "$new" ]; then
    echo "new or changed since the snapshot:"
    printf '%s\n' "$new" | sed 's/^/  /'
    return 1
  fi
  echo "git status unchanged since the snapshot"
}
