"""Predict metric depth using the shared Depth Anything V2 backbone and a bounded depth head.

Use with the official metric checkpoints and their corresponding depth limits.
"""

from torch import nn

from .dpt import DepthAnythingV2


class MetricDepthAnythingV2(DepthAnythingV2):
    def __init__(self, *args, max_depth=20.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_depth = max_depth
        self.depth_head.scratch.output_conv2 = nn.Sequential(
            *list(self.depth_head.scratch.output_conv2.children())[:3], nn.Sigmoid()
        )

    def forward(self, x):
        patch_h, patch_w = x.shape[-2] // 14, x.shape[-1] // 14
        features = self.pretrained.get_intermediate_layers(
            x, self.intermediate_layer_idx[self.encoder], return_class_token=True
        )
        return (self.depth_head(features, patch_h, patch_w) * self.max_depth).squeeze(1)
