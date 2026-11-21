"""Map public VGGT packages to the source directories that implement them."""

from importlib.abc import Loader, MetaPathFinder
from importlib import import_module
from importlib.util import spec_from_loader
from importlib.machinery import PathFinder
from pathlib import Path
import sys


PACKAGES = {
    "vggt": "base/geometry_runtime",
    "vggt.demos": "base/geometry_runtime/demos",
    "vggt.runtime": "base/geometry_runtime/runtime",
    "vggt.runtime.train_utils": "base/geometry_runtime/runtime/train_utils",
    "vggt.models": "models/geometry_transformer/models",
    "vggt.heads": "models/geometry_transformer/heads",
    "vggt.heads.track_modules": "models/geometry_transformer/point_tracking",
    "vggt.layers": "models/geometry_transformer/layers",
    "vggt.layers.tracking": "models/geometry_transformer/tracking_layers",
    "vggt.utils": "models/geometry_transformer/utilities",
    "vggt.dependency": "models/geometry_transformer/dependency",
    "vggt.dependency.track_modules": "models/geometry_transformer/bundle_tracking",
    "vggt.scene_data": "datasets/multi_view",
    "vggt.co3d": "datasets/common_objects_3d/reader",
    "vggt.virtual_kitti": "datasets/virtual_kitti_2/reader",
    "vggt.fine_tune": "tasks/fine_tune/training",
    "vggt.colmap": "tasks/reconstruction/reconstruction",
    "vggt.viewer": "tasks/viewer/application",
    "vggt.precheck": "tasks/precheck/runtime",
    "vggt.configuration": "conf",
}


COMPATIBLE_MODULES = {
    "vggt.demos.colmap": "vggt.demos.colmap_export",
    "vggt.demos.gradio_app": "vggt.demos.gradio_viewer",
    "vggt.demos.viser_app": "vggt.demos.viser_viewer",
    "vggt.dependency.track_modules.utils": "vggt.dependency.track_modules.sampling",
    "vggt.dependency.vggsfm_utils": "vggt.dependency.vggsfm_features",
    "vggt.heads.utils": "vggt.heads.embedding",
    "vggt.layers.mlp": "vggt.layers.feedforward_layer",
    "vggt.layers.swiglu_ffn": "vggt.layers.gated_feedforward",
    "vggt.models.aggregator": "vggt.models.token_aggregation",
    "vggt.models.vggt": "vggt.models.geometry_transformer",
    "vggt.heads.track_modules.utils": "vggt.heads.track_modules.sampling",
    "vggt.layers.tracking.mlp": "vggt.layers.tracking.feedforward_layer",
    "vggt.colmap.colmap": "vggt.colmap.export",
    "vggt.viewer.gradio_app": "vggt.viewer.gradio_viewer",
    "vggt.viewer.viser_app": "vggt.viewer.viser_viewer",
}


class CompatibleModule(Loader):
    """Return the same module object for an earlier public import."""

    def __init__(self, module):
        self.module = module

    def create_module(self, spec):
        return import_module(self.module)

    def exec_module(self, module):
        pass


class CompatibilityFinder(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        module = COMPATIBLE_MODULES.get(fullname)
        if module is not None:
            return spec_from_loader(fullname, CompatibleModule(module))
        return None


class SourceLayout(MetaPathFinder):
    """Resolve source-tree packages using the same mapping as the wheel build."""

    def __init__(self, root):
        self.root = root

    def find_spec(self, fullname, path=None, target=None):
        if fullname not in PACKAGES or fullname == "vggt":
            return None
        directory = self.root / PACKAGES[fullname]
        if self.root in directory.parents and directory.is_dir():
            from importlib.util import spec_from_file_location

            return spec_from_file_location(
                fullname, directory / "__init__.py", submodule_search_locations=[str(directory)]
            )
        return PathFinder.find_spec(fullname, path, target)


def enable_source_layout():
    sys.meta_path.insert(0, CompatibilityFinder())
    root = Path(__file__).resolve().parents[2]
    if (root / "base/geometry_runtime/source_layout.py").is_file():
        sys.meta_path.insert(0, SourceLayout(root))
