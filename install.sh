#!/usr/bin/env bash
# Install the spec-driven development (SDD) template into a project directory.
#
# Idempotent and non-destructive: existing files are never overwritten (an
# existing CLAUDE.md gets the rules as CLAUDE.sdd.md instead), and .gitignore
# is only appended to. Safe to re-run after the template was updated: only
# missing files are added.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install.sh [TARGET_DIR] [--with-ci]

  TARGET_DIR  project directory (default: current directory)
  --with-ci   also install .github/workflows/sdd-check.yml (GitHub PR check)
EOF
}

TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILES_DIR="$TEMPLATE_DIR/files"
CI_FILE=".github/workflows/sdd-check.yml"
TARGET="."
WITH_CI=0

for arg in "$@"; do
  case "$arg" in
    --with-ci) WITH_CI=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option: $arg" >&2; usage >&2; exit 2 ;;
    *) TARGET="$arg" ;;
  esac
done

for bin in git python3; do
  command -v "$bin" >/dev/null || { echo "Missing required command: $bin" >&2; exit 1; }
done

mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"
echo "Installing SDD template into $TARGET"

# --- git repository: never hijack a parent repository
toplevel="$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$toplevel" ]; then
  git -C "$TARGET" init -q -b main
  echo "  git     init (branch main)"
elif [ "$toplevel" != "$TARGET" ]; then
  echo "ERROR: $TARGET is inside another git repository ($toplevel)." >&2
  echo "       Install into the repository root, or create a separate repository first." >&2
  exit 1
fi

# --- files
SKIPPED=()
install_file() {
  local rel="$1" dest="$1"
  # A foreign CLAUDE.md is kept; the SDD rules go next to it. Ours (same
  # first line) counts as already installed.
  if [ "$rel" = "CLAUDE.md" ] && [ -e "$TARGET/CLAUDE.md" ] \
     && [ "$(head -n1 "$TARGET/CLAUDE.md")" != "$(head -n1 "$FILES_DIR/CLAUDE.md")" ]; then
    dest="CLAUDE.sdd.md"
  fi
  if [ -e "$TARGET/$dest" ]; then
    echo "  skip    $dest (exists)"
    SKIPPED+=("$dest")
    return
  fi
  mkdir -p "$(dirname "$TARGET/$dest")"
  cp -p "$FILES_DIR/$rel" "$TARGET/$dest"
  echo "  create  $dest"
}

while IFS= read -r -d '' src; do
  rel="${src#"$FILES_DIR"/}"
  case "$rel" in
    gitignore) continue ;;
    "$CI_FILE") [ "$WITH_CI" -eq 1 ] || continue ;;
  esac
  install_file "$rel"
done < <(find "$FILES_DIR" -type f -not -path '*/__pycache__/*' -print0 | sort -z)

chmod +x "$TARGET/.githooks/pre-commit" "$TARGET/.claude/hooks/sdd_guard.py" 2>/dev/null || true

# --- .gitignore: append missing lines only
touch "$TARGET/.gitignore"
added=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  if ! grep -qxF -- "$line" "$TARGET/.gitignore"; then
    if [ "$added" -eq 0 ] && [ -s "$TARGET/.gitignore" ]; then
      [ -n "$(tail -c1 "$TARGET/.gitignore")" ] && printf '\n' >> "$TARGET/.gitignore"
      printf '\n' >> "$TARGET/.gitignore"
    fi
    printf '%s\n' "$line" >> "$TARGET/.gitignore"
    added=1
  fi
done < "$FILES_DIR/gitignore"
[ "$added" -eq 1 ] && echo "  update  .gitignore"

# --- git hooks
current="$(git -C "$TARGET" config --local --get core.hooksPath || true)"
if [ -z "$current" ]; then
  git -C "$TARGET" config --local core.hooksPath .githooks
  echo "  git     core.hooksPath = .githooks"
elif [ "$current" != ".githooks" ]; then
  echo "  WARNING core.hooksPath is already '$current': the SDD pre-commit hook is NOT active."
fi

# --- self-test of the guard in this project
log="$(mktemp)"
if PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$TARGET/.claude/hooks" -p 'test_*.py' >"$log" 2>&1; then
  echo "  test    $(grep -E '^Ran [0-9]+ tests' "$log") — OK"
else
  echo "  TEST FAILURE: the SDD guard tests failed:" >&2
  tail -20 "$log" >&2
  rm -f "$log"
  exit 1
fi
rm -f "$log"

# --- report
echo
for f in ${SKIPPED[@]+"${SKIPPED[@]}"}; do
  case "$f" in
    .claude/settings.json)
      echo "ACTION NEEDED: .claude/settings.json already existed, so the SDD hooks are NOT wired."
      echo "  Merge the \"hooks\" block from $FILES_DIR/.claude/settings.json into it." ;;
    CLAUDE.sdd.md)
      echo "ACTION NEEDED: CLAUDE.md already existed and CLAUDE.sdd.md too; nothing was added."
      echo "  Make sure CLAUDE.md contains the line: @CLAUDE.sdd.md" ;;
  esac
done
if [ -e "$TARGET/CLAUDE.sdd.md" ] && ! grep -qxF '@CLAUDE.sdd.md' "$TARGET/CLAUDE.md"; then
  echo "ACTION NEEDED: CLAUDE.md already existed; the SDD rules are in CLAUDE.sdd.md."
  echo "  Add this line to CLAUDE.md to load them: @CLAUDE.sdd.md"
fi

cat <<'EOF'
Next steps:
  1. Restart Claude Code in this directory: hooks and skills load at session start.
  2. Commit the scaffold on main: chore(sdd): scaffold spec-driven workflow
  3. Run /constitution
EOF
