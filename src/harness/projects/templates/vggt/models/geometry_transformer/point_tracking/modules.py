# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


"""Preserve imports for the original VGGT tracker layers."""

from vggt.layers.tracking import Mlp, ResidualBlock, _ntuple, default, exists, to_2tuple
from vggt.layers.tracking import attention


class AttnBlock(attention.AttnBlock):
    """VGGT attention with affine layer normalization."""


class CrossAttnBlock(attention.CrossAttnBlock):
    """VGGT attention with affine layer normalization."""
