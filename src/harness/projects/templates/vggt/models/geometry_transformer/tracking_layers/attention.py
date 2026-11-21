# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


"""Implement self-attention and cross-attention for the two trackers."""

from typing import Callable

import torch.nn as nn

from .feedforward_layer import Mlp


class AttnBlock(nn.Module):
    _normalization = nn.LayerNorm

    def __init__(
        self,
        hidden_size,
        num_heads,
        attn_class: Callable[..., nn.Module] = nn.MultiheadAttention,
        mlp_ratio=4.0,
        **block_kwargs,
    ):
        """
        Self attention block
        """
        super().__init__()

        self.norm1 = self._normalization(hidden_size)
        self.norm2 = self._normalization(hidden_size)

        self.attn = attn_class(embed_dim=hidden_size, num_heads=num_heads, batch_first=True, **block_kwargs)

        mlp_hidden_dim = int(hidden_size * mlp_ratio)

        self.mlp = Mlp(in_features=hidden_size, hidden_features=mlp_hidden_dim, drop=0)

    def forward(self, x, mask=None):
        # Keep the optional mask argument accepted by both trackers.
        x = self.norm1(x)
        attn_output, _ = self.attn(x, x, x)

        # Add & Norm
        x = x + attn_output
        x = x + self.mlp(self.norm2(x))
        return x


class CrossAttnBlock(nn.Module):
    _normalization = nn.LayerNorm

    def __init__(self, hidden_size, context_dim, num_heads=1, mlp_ratio=4.0, **block_kwargs):
        """
        Cross attention block
        """
        super().__init__()

        self.norm1 = self._normalization(hidden_size)
        self.norm_context = nn.LayerNorm(hidden_size)
        self.norm2 = self._normalization(hidden_size)

        self.cross_attn = nn.MultiheadAttention(
            embed_dim=hidden_size, num_heads=num_heads, batch_first=True, **block_kwargs
        )

        mlp_hidden_dim = int(hidden_size * mlp_ratio)

        self.mlp = Mlp(in_features=hidden_size, hidden_features=mlp_hidden_dim, drop=0)

    def forward(self, x, context, mask=None):
        # Normalize inputs
        x = self.norm1(x)
        context = self.norm_context(context)

        # Apply cross attention
        # Note: nn.MultiheadAttention returns attn_output, attn_output_weights
        attn_output, _ = self.cross_attn(x, context, context, attn_mask=mask)

        # Add & Norm
        x = x + attn_output
        x = x + self.mlp(self.norm2(x))
        return x
