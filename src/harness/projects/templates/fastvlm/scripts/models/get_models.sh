#!/usr/bin/env bash
#
# For licensing see accompanying assets/licensing/upstream/files/LICENSE_MODEL file.
# Copyright (C) 2025 Apple Inc. All Rights Reserved.
#
set -euo pipefail

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
workspace=$(dirname -- "$project_root")
if [[ "$(basename -- "$workspace")" == templates && -f "$project_root/../../../../../src/harness/cli.py" ]]; then
    workspace=$(cd -- "$project_root/../../../../../.." && pwd)
fi
checkpoints="$workspace/data/fastvlm/checkpoints"
download_url=https://ml-site.cdn-apple.com/datasets/fastvlm

mkdir -p "$checkpoints"
archive=$(mktemp "$checkpoints/.download.XXXXXX")
trap 'rm -f -- "$archive"' EXIT

for size in 0.5b 1.5b 7b; do
    for stage in 2 3; do
        checkpoint="llava-fastvithd_${size}_stage${stage}"
        wget -O "$archive" "$download_url/$checkpoint.zip"
        unzip -qq "$archive" -d "$checkpoints"
    done
done
