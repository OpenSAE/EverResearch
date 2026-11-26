#!/usr/bin/env bash
# Install the Python distribution in the active environment without building in the source tree.
# Run with an optional comma-separated selection from training, pointcloud, and demo.
set -euo pipefail

project="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build="$(mktemp -d)"
trap 'rm -rf -- "$build"' EXIT
cp -a "$project"/{base,conf,datasets,models,tasks,pyproject.toml,LICENSE} "$build"
if [[ -n "${1:-}" ]]; then
    python -m pip install "$build[$1]"
else
    python -m pip install "$build"
fi
