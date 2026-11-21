#!/usr/bin/env bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

set -euo pipefail

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf 'Usage: %s [DATASET_DIR]\nDefault dataset directory: ./vkitti\n' "$0"
    exit 0
fi
if [[ $# -gt 1 ]]; then
    printf 'Usage: %s [DATASET_DIR]\n' "$0" >&2
    exit 2
fi

dataset_dir=${1:-vkitti}
mkdir -p -- "$dataset_dir"
cd -- "$dataset_dir"

wget https://download.europe.naverlabs.com//virtual_kitti_2.0.3/vkitti_2.0.3_rgb.tar
tar -xvf vkitti_2.0.3_rgb.tar

wget https://download.europe.naverlabs.com//virtual_kitti_2.0.3/vkitti_2.0.3_depth.tar
tar -xvf vkitti_2.0.3_depth.tar

wget https://download.europe.naverlabs.com//virtual_kitti_2.0.3/vkitti_2.0.3_textgt.tar.gz
tar -xvf vkitti_2.0.3_textgt.tar.gz

