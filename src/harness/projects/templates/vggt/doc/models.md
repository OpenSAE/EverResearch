# Models

## VGGT-1B

The public `vggt.models.vggt.VGGT` class implements the geometry transformer with optional camera, depth, point-map and tracking heads. It accepts preprocessed RGB tensors shaped `[S, 3, H, W]` or `[B, S, 3, H, W]`. Tracking takes query pixels. The viewer and export commands load the published VGGT-1B checkpoint through PyTorch's weight cache. The fine-tuning recipe uses the camera and depth heads with a frozen aggregator and an explicit initial checkpoint path.

## VGGSfM tracker for bundle adjustment

The COLMAP `--use_ba` path uses the VGGSfM tracker to produce observations for refinement. Shared tracking layers and position embeddings serve both trackers. Each tracker keeps its own feature sampling, correlation and normalization behavior.
