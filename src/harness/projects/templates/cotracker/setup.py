"""Build CoTracker and map public Python imports to their owning source directories."""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in LICENSE.md.

from pathlib import Path

from setuptools import setup
from setuptools.command.egg_info import egg_info


class ProjectEggInfo(egg_info):
    def finalize_options(self):
        if self.egg_base is None:
            self.egg_base = ".build"
            Path(self.egg_base).mkdir(exist_ok=True)
        super().finalize_options()



package_dirs = {
    "cotracker": "base/tracking",
    "cotracker.utils": "base/tracking/shared",
    "cotracker.datasets": "datasets/video_tracking",
    "cotracker.datasets.dataclass_utils": "datasets/video_tracking/annotation_records",
    "cotracker.datasets.utils": "datasets/video_tracking/batching",
    "cotracker.models": "models/tracking",
    "cotracker.models.core": "models/network",
    "cotracker.models.core.cotracker": "models/network/point_tracking",
    "cotracker.models.core.cotracker.cotracker": "models/network/second_generation",
    "cotracker.models.core.cotracker.cotracker3_offline": "models/network/offline",
    "cotracker.models.core.cotracker.cotracker3_online": "models/network/online",
    "cotracker.models.core.cotracker.losses": "tasks/training/point_losses",
    "cotracker.predictor": "models/tracking/predictor_api",
    "cotracker.evaluation": "tasks/evaluation",
    "cotracker.evaluation.core": "tasks/evaluation/core",
    "cotracker.evaluation.core.eval_utils": "tasks/evaluation/point_metrics",
    "cotracker.training": "tasks/training",
    "cotracker.tracking": "tasks/tracking",
    "cotracker.precheck": "tasks/precheck",
    "cotracker.config_data": "conf",
    "cotracker.evaluation.preset_data": "conf/tasks/evaluation",
}

setup(
    name="cotracker",
    version="3.0",
    packages=list(package_dirs),
    package_dir=package_dirs,
    cmdclass={"egg_info": ProjectEggInfo},
    options={"build": {"build_base": ".build/wheel"}},
    package_data={
        "cotracker.config_data": ["config.yaml"],
        "cotracker.evaluation.preset_data": ["presets.yaml"],
    },
    install_requires=["torch", "torchvision", "numpy", "imageio[ffmpeg]", "matplotlib", "PyYAML"],
    extras_require={
        "all": ["matplotlib"],
        "dev": ["flake8", "black", "pytest"],
        "evaluation": ["hydra-core>=1.3,<1.4", "mediapy", "opencv-python", "tqdm"],
    },
    entry_points={"console_scripts": ["cotracker=cotracker.commands:main"]},
)
