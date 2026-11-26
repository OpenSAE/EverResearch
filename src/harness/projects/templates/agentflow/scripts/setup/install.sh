#!/usr/bin/env bash
# Create the isolated AgentFlow environment. GPU training is opt-in.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

case "${1:-}" in
    "") extras=".[agent,experiment]" ;;
    --dev) extras=".[agent,experiment,dev]" ;;
    --training) extras=".[agent,experiment,dev]" ;;
    *) printf 'Usage: %s [--dev|--training]\n' "$0" >&2; exit 2 ;;
esac
if ! command -v uv >/dev/null; then
    printf 'Install uv before running this script.\n' >&2
    exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
    uv venv --python 3.11
fi
uv pip install --python .venv/bin/python -e "$extras"

if [[ "${1:-}" == --training ]]; then
    source .venv/bin/activate
    bash scripts/setup_stable_gpu.sh
fi
