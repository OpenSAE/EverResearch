# Copyright 2020-2026 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from importlib.util import find_spec
from pathlib import Path
from collections.abc import Callable
from typing import Any

from accelerate.commands.launch import launch_command, launch_command_parser


def training_script_path(script_name: str) -> Path:
    """Resolve an installed trainer's executable module without importing it."""
    module = find_spec(f"trl.scripts.{Path(script_name).stem}")
    if module is None or module.origin is None:
        raise ValueError(f"Unknown TRL training script: {script_name}")
    path = Path(module.origin)
    return path.with_name("__main__.py") if path.name == "__init__.py" else path


def launch_training_script(
    script_name: str,
    launch_args: list[str],
    training_script_args: list[str],
    *,
    launch_command_fn: Callable[[Any], None] = launch_command,
    launch_parser_fn: Callable[[], Any] = launch_command_parser,
) -> None:
    """
    Launch a TRL training script through `accelerate launch`.

    Parameters:
        script_name (`str`):
            Script filename in `trl/scripts`, e.g. `"dpo.py"`.
        launch_args (`list[str]`):
            Arguments consumed by `accelerate launch`.
        training_script_args (`list[str]`):
            Arguments forwarded to the training script.
        launch_command_fn (`Callable[[Any], None]`, *optional*):
            Function used to execute accelerate launch.
        launch_parser_fn (`Callable[[], Any]`, *optional*):
            Factory creating the accelerate launch parser.
    """
    training_script = training_script_path(script_name)
    accelerate_args = launch_parser_fn().parse_args(launch_args + [str(training_script)] + training_script_args)
    launch_command_fn(accelerate_args)
