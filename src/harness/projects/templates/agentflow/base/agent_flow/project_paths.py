"""Locate AgentFlow configuration in editable and wheel installations."""

from pathlib import Path
import sysconfig


def config_directory():
    installed = Path(sysconfig.get_path("data")) / "share" / "agentflow"
    source = Path(__file__).resolve().parents[2] / "conf"
    if (source / "config.yaml").is_file():
        return source
    return installed
