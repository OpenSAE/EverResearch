"""Locate DINOv2 packages in the research checkout and during distribution builds.

The mapping preserves public import names while grouping the source by responsibility.
"""

from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

PACKAGES = {
    'dinov2': 'base/dino',
    'dinov2.configs': 'base/dino/configuration',
    'dinov2.data': 'datasets/images',
    'dinov2.data.cell_dino': 'datasets/images/cell_transforms',
    'dinov2.data.datasets': 'datasets/image_sources',
    'dinov2.data.datasets.cell_dino': 'datasets/image_sources/microscopy',
    'dinov2.distributed': 'base/dino/distributed',
    'dinov2.eval': 'tasks/classification',
    'dinov2.eval.cell_dino': 'tasks/cell_classification',
    'dinov2.eval.depth': 'tasks/depth_estimation',
    'dinov2.eval.depth.models': 'tasks/depth_estimation/models',
    'dinov2.eval.depth.models.backbones': 'tasks/depth_estimation/models_backbones',
    'dinov2.eval.depth.models.decode_heads': 'tasks/depth_estimation/models_decode_heads',
    'dinov2.eval.depth.models.depther': 'tasks/depth_estimation/models_estimator',
    'dinov2.eval.depth.models.losses': 'tasks/depth_estimation/models_losses',
    'dinov2.eval.depth.ops': 'tasks/depth_estimation/operators',
    'dinov2.eval.segmentation': 'tasks/semantic_segmentation',
    'dinov2.eval.segmentation.hooks': 'tasks/semantic_segmentation/hooks',
    'dinov2.eval.segmentation.models': 'tasks/semantic_segmentation/models',
    'dinov2.eval.segmentation.models.backbones': 'tasks/semantic_segmentation/models_backbones',
    'dinov2.eval.segmentation.models.decode_heads': 'tasks/semantic_segmentation/models_decode_heads',
    'dinov2.eval.segmentation.utils': 'tasks/semantic_segmentation/utilities',
    'dinov2.eval.segmentation_m2f': 'tasks/mask_segmentation',
    'dinov2.eval.segmentation_m2f.core': 'tasks/mask_segmentation/core',
    'dinov2.eval.segmentation_m2f.core.anchor': 'tasks/mask_segmentation/core_anchor',
    'dinov2.eval.segmentation_m2f.core.box': 'tasks/mask_segmentation/core_box',
    'dinov2.eval.segmentation_m2f.core.box.samplers': 'tasks/mask_segmentation/core_box_samplers',
    'dinov2.eval.segmentation_m2f.core.utils': 'tasks/mask_segmentation/core_utilities',
    'dinov2.eval.segmentation_m2f.models': 'tasks/mask_segmentation/models',
    'dinov2.eval.segmentation_m2f.models.backbones': 'tasks/mask_segmentation/models_backbones',
    'dinov2.eval.segmentation_m2f.models.decode_heads': 'tasks/mask_segmentation/models_decode_heads',
    'dinov2.eval.segmentation_m2f.models.losses': 'tasks/mask_segmentation/models_losses',
    'dinov2.eval.segmentation_m2f.models.plugins': 'tasks/mask_segmentation/models_plugins',
    'dinov2.eval.segmentation_m2f.models.segmentors': 'tasks/mask_segmentation/models_segmentors',
    'dinov2.eval.segmentation_m2f.models.utils': 'tasks/mask_segmentation/models_utilities',
    'dinov2.eval.segmentation_m2f.ops': 'tasks/mask_segmentation/operators',
    'dinov2.eval.segmentation_m2f.ops.modules': 'tasks/mask_segmentation/operators_modules',
    'dinov2.fsdp': 'base/dino/parameter_shards',
    'dinov2.hub': 'models/hub',
    'dinov2.hub.cell_dino': 'models/hub/cell_dino',
    'dinov2.hub.depth': 'models/hub/depth',
    'dinov2.hub.text': 'models/hub/text',
    'dinov2.hub.xray_dino': 'models/hub/radiograph',
    'dinov2.layers': 'models/layers',
    'dinov2.logging': 'base/dino/logging',
    'dinov2.loss': 'tasks/training/loss',
    'dinov2.models': 'models/vision_transformer',
    'dinov2.run': 'base/dino/run',
    'dinov2.run.eval': 'base/dino/run/evaluation',
    'dinov2.run.eval.cell_dino': 'base/dino/run/evaluation/cell_dino',
    'dinov2.run.train': 'base/dino/run/train',
    'dinov2.thirdparty': 'third_party/clip',
    'dinov2.thirdparty.CLIP': 'third_party/clip/CLIP',
    'dinov2.thirdparty.CLIP.clip': 'third_party/clip/CLIP/clip',
    'dinov2.train': 'tasks/training',
    'dinov2.utils': 'base/dino/utilities',
    'dinov2.configs.bundled': 'conf',
    'dinov2.precheck': 'tasks/precheck',
}

RENAMED_MODULES = {
    'dinov2.data.datasets.image_net_22k': 'image_net_large.py',
    'dinov2.data.datasets.cell_dino.chammi_cp': 'chammi_cell_painting.py',
    'dinov2.data.datasets.cell_dino.chammi_hpa': 'chammi_protein_atlas.py',
    'dinov2.data.datasets.cell_dino.chammi_wtc': 'chammi_stem_cells.py',
    'dinov2.data.datasets.cell_dino.hpafov': 'protein_atlas_fields.py',
    'dinov2.data.datasets.cell_dino.hpaone': 'protein_atlas_cells.py',
    'dinov2.eval.knn': 'nearest_neighbors.py',
    'dinov2.eval.utils': 'utilities.py',
    'dinov2.eval.cell_dino.knn': 'nearest_neighbors.py',
    'dinov2.eval.cell_dino.utils': 'utilities.py',
    'dinov2.eval.depth.models.losses.gradientloss': 'gradient_loss.py',
    'dinov2.eval.depth.models.losses.sigloss': 'scale_invariant_loss.py',
    'dinov2.eval.segmentation.utils.colormaps': 'color_maps.py',
    'dinov2.eval.segmentation_m2f.core.utils.dist_utils': 'distributed_utilities.py',
    'dinov2.eval.segmentation_m2f.core.utils.misc': 'miscellaneous.py',
    'dinov2.eval.segmentation_m2f.models.backbones.vit': 'vision_transformer.py',
    'dinov2.eval.segmentation_m2f.models.decode_heads.mask2former_head': 'maskformer_head.py',
    'dinov2.eval.segmentation_m2f.models.segmentors.encoder_decoder_mask2former': 'encoder_decoder_maskformer.py',
    'dinov2.hub.depthers': 'depth_models.py',
    'dinov2.hub.dinotxt': 'image_text_model.py',
    'dinov2.hub.utils': 'utilities.py',
    'dinov2.hub.text.dinov2_wrapper': 'vision_model_wrapper.py',
    'dinov2.layers.mlp': 'multilayer_perceptron.py',
    'dinov2.layers.swiglu_ffn': 'gated_feed_forward.py',
    'dinov2.run.eval.knn': 'nearest_neighbors.py',
    'dinov2.run.eval.cell_dino.knn': 'nearest_neighbors.py',
    'dinov2.utils.config': 'runtime_configuration.py',
    'dinov2.utils.dtype': 'tensor_types.py',
    'dinov2.utils.utils': 'utilities.py',
}



class CheckoutPackages(MetaPathFinder):
    """Provide the installed import names when a launcher runs from source."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname in PACKAGES:
            directory = ROOT / PACKAGES[fullname]
            initializer = directory / "__init__.py"
            if initializer.is_file():
                return spec_from_file_location(fullname, initializer)
            spec = ModuleSpec(fullname, loader=None, is_package=True)
            spec.submodule_search_locations = [str(directory)]
            return spec
        if fullname in RENAMED_MODULES:
            package, _, _ = fullname.rpartition(".")
            filename = ROOT / PACKAGES[package] / RENAMED_MODULES[fullname]
            return spec_from_file_location(fullname, filename)
        return None


def use_checkout_packages():
    if not any(isinstance(finder, CheckoutPackages) for finder in sys.meta_path):
        sys.meta_path.insert(0, CheckoutPackages())
