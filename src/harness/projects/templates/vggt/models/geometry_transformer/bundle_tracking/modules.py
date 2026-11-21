# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


"""Preserve the VGGSfM tracker imports and its checkpoint normalization."""

from functools import partial

import torch.nn as nn

from vggt.layers.tracking import Mlp, ResidualBlock, _ntuple, default, exists, to_2tuple
from vggt.layers.tracking import attention


_layer_norm = partial(nn.LayerNorm, elementwise_affine=False, eps=1e-6)


class AttnBlock(attention.AttnBlock):
    _normalization = _layer_norm


class CrossAttnBlock(attention.CrossAttnBlock):
    _normalization = _layer_norm
