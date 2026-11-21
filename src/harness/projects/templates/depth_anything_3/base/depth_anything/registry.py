# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict

from omegaconf import OmegaConf

from depth_anything_3.runtime.paths import CONFIG_ROOT


MODEL_PRESETS = CONFIG_ROOT / "models" / "model" / "config.yaml"


def get_all_models() -> OrderedDict:
    """Map public model names to references resolved by the configuration loader."""
    return OrderedDict(
        (name, f"depth_anything_3.configs.{name}")
        for name in sorted(OmegaConf.load(MODEL_PRESETS))
    )


MODEL_REGISTRY = get_all_models()
