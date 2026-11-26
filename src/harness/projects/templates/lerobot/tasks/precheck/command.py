"""Preview LeRobot training with the same configuration and admission checks."""

import json

from lerobot import policies, rewards  # noqa: F401 - register built-in config choices
from lerobot.configs import parser
from lerobot.configs.train import TrainPipelineConfig
from lerobot.utils.import_utils import register_third_party_plugins


@parser.wrap()
def precheck(cfg: TrainPipelineConfig) -> None:
    """Resolve the requested run without starting workers or writing outputs."""
    cfg.validate()
    model = cfg.trainable_config
    print(json.dumps({
        "dataset": cfg.dataset.repo_id,
        "dataset_root": cfg.dataset.root,
        "model": model.type,
        "device": model.device,
        "output_directory": str(cfg.output_dir),
    }, indent=2))


def main() -> None:
    """Run the configuration preview with the usual installed plugins."""
    register_third_party_plugins()
    precheck()  # type: ignore[call-arg]  # parser.wrap reads the CLI when no config is passed
