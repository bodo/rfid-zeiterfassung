#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="$HERE/.venv"
if [ -f "$VENV/bin/activate" ]; then
  # activate virtualenv if present
  # shellcheck disable=SC1090
  source "$VENV/bin/activate"
fi
pytest "$@"
