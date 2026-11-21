"""Resolve SAM 2 public names across source and installed layouts."""
import importlib.abc
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

PACKAGE_DIRECTORIES = {
    "sam2": "base/segment_anything",
    "sam2.modeling": "models/segment_anything",
    "sam2.modeling.backbones": "models/segment_anything/backbones",
    "sam2.modeling.sam": "models/segment_anything/sam",
    "sam2.utils": "base/segment_anything/utility",
    "sam2.tasks": "tasks/image_segmentation",
    "sam2.precheck": "tasks/precheck",
    "sam2.video": "tasks/video_segmentation",
    "sam2.evaluation": "tasks/evaluation",
    "sam2.benchmarking": "tasks/benchmarking",
    "sam2.annotations": "datasets/annotations",
    "sam2.example_images": "datasets/notebook_images",
    "sam2.recipes": "conf",
    "training": "base/training",
    "training.utils": "base/training/runtime",
    "training.dataset": "datasets/video_objects",
    "training.model": "models/segment_anything/training",
    "training.finetuning": "tasks/fine_tuning",
}

MODULE_ALIASES = {
    "sam2.build_sam": "sam2.modeling.build",
    "sam2.automatic_mask_generator": "sam2.tasks.automatic_masks",
    "sam2.utils.misc": "sam2.utils.media",
    "sam2.utils.amg": "sam2.utils.mask_generator",
    "sam2.modeling.backbones.hieradet": "sam2.modeling.backbones.hiera_encoder",
    "sam2.modeling.backbones.utils": "sam2.modeling.backbones.windowing",
    "training.dataset.utils": "training.dataset.sampling",
    "sam2.sam2_image_predictor": "sam2.modeling.predictor",
    "sam2.sam2_video_predictor": "sam2.video.predictor",
    "sam2.sam2_video_predictor_legacy": "sam2.video.legacy_predictor",
    "sam2.modeling.sam2_base": "sam2.modeling.base",
    "sam2.modeling.sam2_utils": "sam2.modeling.layers",
    "sam2.benchmark": "sam2.benchmarking.benchmark",
    "training.dataset.sam2_datasets": "training.dataset.mixed_datasets",
    "training.model.sam2": "training.model.model",
    "training.trainer": "training.finetuning.trainer",
    "training.loss_fns": "training.finetuning.loss_fns",
    "training.optimizer": "training.finetuning.optimizer",
}


def source_root():
    source = Path(__file__).resolve()
    root = source.parents[2]
    return root if root / "base" / "segment_anything" / "imports.py" == source else None


def _package_spec(fullname, package):
    initializer = package / "__init__.py"
    if initializer.is_file():
        return importlib.util.spec_from_file_location(
            fullname, initializer, submodule_search_locations=[str(package)]
        )
    spec = importlib.machinery.ModuleSpec(fullname, loader=None, is_package=True)
    spec.submodule_search_locations = [str(package)]
    return spec


class PublicAlias(importlib.abc.Loader):
    def __init__(self, target):
        self.target = target

    def create_module(self, spec):
        return importlib.import_module(self.target)

    def exec_module(self, module):
        pass

    def get_code(self, fullname):
        canonical = importlib.util.find_spec(self.target)
        return canonical.loader.get_code(self.target)


class PublicImports(importlib.abc.MetaPathFinder):
    def __init__(self, root):
        self.root = root

    def find_spec(self, fullname, path=None, target=None):
        if self.root is not None and fullname in PACKAGE_DIRECTORIES:
            package = self.root / PACKAGE_DIRECTORIES[fullname]
            return _package_spec(fullname, package)
        if self.root is not None and fullname == "sam2._C":
            extension = self.root / "assets/native_extension/connected_components/files/connected_components.so"
            if extension.is_file():
                return importlib.util.spec_from_file_location(fullname, extension)
        alias = MODULE_ALIASES.get(fullname)
        if alias is not None:
            return importlib.util.spec_from_loader(fullname, PublicAlias(alias))
        return None


def install_public_imports():
    if not any(type(finder).__name__ == "PublicImports" for finder in sys.meta_path):
        sys.meta_path.insert(0, PublicImports(source_root()))
