#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '\n==> %s\n' "$1"
}

run() {
  printf '+ %s\n' "$*"
  "$@"
}

if [[ ! -f "pyproject.toml" ]]; then
  echo "Run this script from the Runtrace repository root." >&2
  exit 1
fi

PYTHON_BIN="${PYTHON:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "Python is required but neither python3 nor python was found." >&2
    exit 1
  fi
fi

SMOKE_DIR="${RUNTRACE_SMOKE_DIR:-$(mktemp -d /tmp/runtrace-smoke-XXXXXX)}"
VENV_DIR="$SMOKE_DIR/.venv"
WORK_DIR="$SMOKE_DIR/work"
cleanup() {
  if [[ -z "${RUNTRACE_SMOKE_KEEP:-}" && -d "$SMOKE_DIR" ]]; then
    rm -rf "$SMOKE_DIR"
  fi
}
trap cleanup EXIT

log "Creating isolated smoke environment"
run "$PYTHON_BIN" -m venv "$VENV_DIR"
PY="$VENV_DIR/bin/python"
RUNTRACE="$VENV_DIR/bin/runtrace"
PYTEST="$VENV_DIR/bin/pytest"
RUFF="$VENV_DIR/bin/ruff"
mkdir -p "$WORK_DIR"

log "Installing Runtrace into the smoke environment"
run "$PY" -m pip install --upgrade pip >/dev/null
run "$PY" -m pip install -e '.[dev]'

log "Checking CLI help"
run "$RUNTRACE" --help >/dev/null
run "$PY" -m runtrace --help >/dev/null

log "Running demo in a clean working directory"
(
  cd "$WORK_DIR"
  run "$RUNTRACE" demo
  run "$RUNTRACE" list >/dev/null
  run "$RUNTRACE" show latest >/dev/null
  run "$RUNTRACE" report >/dev/null
)

log "Running tests"
run "$PYTEST" -q

if [[ -x "$RUFF" ]]; then
  log "Running ruff"
  run "$RUFF" check .
else
  log "Skipping ruff (not installed)"
fi

log "Smoke test passed"
