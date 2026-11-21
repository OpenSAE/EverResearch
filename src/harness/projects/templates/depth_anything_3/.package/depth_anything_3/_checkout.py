"""Preserve Depth Anything 3 imports across a source tree split by responsibility."""

from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location
import sys

from .runtime.paths import CHECKOUT


# The wheel uses the public import paths directly. The editable checkout uses the
# source directory names below, with the same fully-qualified Python names.
_SOURCE_MODULES = {
    "model": "models/model",
    "model.da3": "models/model/depth_network.py",
    "model.dinov2": "models/backbone",
    "model.dinov2.dinov2": "models/backbone/encoder.py",
    "bench": "tasks/evaluation/bench",
    "bench.dataset": "datasets/benchmark/dataset.py",
    "bench.datasets": "datasets/benchmark/datasets",
    "services.input_handlers": "datasets/media/input_handlers.py",
    "services.inference_service": "tasks/inference/service.py",
    "utils.io": "datasets/media/processing",
    "utils.io.output_processor": "tasks/inference/output_processor.py",
    "streaming_frames": "datasets/media/streaming_frames.py",
    "utils.export": "tasks/inference/export",
    "inference_task": "tasks/inference/operation.py",
    "precheck": "tasks/precheck/gate.py",
    "streaming_task": "tasks/streaming",
    "utils.alignment": "base/depth_anything/helpers/geometry_helpers/alignment.py",
    "utils.geometry": "base/depth_anything/helpers/geometry_helpers/geometry.py",
    "utils.pose_align": "base/depth_anything/helpers/geometry_helpers/pose_align.py",
    "utils.ray_utils": "base/depth_anything/helpers/geometry_helpers/ray_utils.py",
    "utils.camera_trj_helpers": "base/depth_anything/helpers/drawing/camera_trj_helpers.py",
    "utils.gsply_helpers": "base/depth_anything/helpers/drawing/gsply_helpers.py",
    "utils.pca_utils": "base/depth_anything/helpers/drawing/principal_components.py",
    "utils.sh_helpers": "base/depth_anything/helpers/drawing/sh_helpers.py",
    "utils.visualize": "base/depth_anything/helpers/drawing/visualize.py",
    "api": "base/depth_anything/interface.py",
    "cfg": "base/depth_anything/config.py",
    "cli": "base/depth_anything/commands.py",
    "services.backend": "base/depth_anything/services/server.py",
    "app.gradio_app": "base/depth_anything/interface_web/gradio_interface.py",
    "app.modules.utils": "base/depth_anything/interface_web/modules/helpers.py",
    "app": "base/depth_anything/interface_web",
    "utils": "base/depth_anything/helpers",
    "bench.datasets.dtu": "datasets/benchmark/datasets/dtu_reader.py",
    "bench.datasets.dtu64": "datasets/benchmark/datasets/dtu_pose_reader.py",
    "bench.datasets.eth3d": "datasets/benchmark/datasets/eth_reader.py",
    "bench.datasets.hiroom": "datasets/benchmark/datasets/hiroom_reader.py",
    "bench.datasets.scannetpp": "datasets/benchmark/datasets/scannet_reader.py",
    "bench.datasets.sevenscenes": "datasets/benchmark/datasets/seven_scenes.py",
    "model.dinov2.layers.mlp": "models/backbone/layers/dense_layer.py",
    "model.dinov2.layers.swiglu_ffn": "models/backbone/layers/gated_feedforward.py",
    "model.dpt": "models/model/prediction_head.py",
    "model.dualdpt": "models/model/dual_prediction_head.py",
    "model.gsdpt": "models/model/gaussian_prediction_head.py",
    "model.utils": "models/model/helpers",
    "bench.utils": "tasks/evaluation/bench/helpers.py",
    "utils.export.colmap": "tasks/inference/export/colmap_writer.py",
    "utils.export.glb": "tasks/inference/export/glb_writer.py",
    "utils.export.npz": "tasks/inference/export/npz_writer.py",
    "utils.export.utils": "tasks/inference/export/helpers.py",
    "streaming_task.fastloop": "tasks/streaming/solver",
}


class _CheckoutImports(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        prefix = __package__ + "."
        relative = _SOURCE_MODULES.get(fullname[len(prefix):]) if fullname.startswith(prefix) else None
        if relative is None:
            return None
        source = CHECKOUT / relative
        if source.is_file():
            return spec_from_file_location(fullname, source)
        if (source / "__init__.py").is_file():
            return spec_from_file_location(
                fullname, source / "__init__.py", submodule_search_locations=[str(source)]
            )
        spec = ModuleSpec(fullname, loader=None, is_package=True)
        spec.submodule_search_locations = [str(source)]
        return spec


def install():
    """Resolve the historical public modules from their current source files."""
    if not any(isinstance(finder, _CheckoutImports) for finder in sys.meta_path):
        sys.meta_path.append(_CheckoutImports())
