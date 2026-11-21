"""Register the supported vision-language models and preserve the architecture import."""
import sys

from . import upgrade, vision_architecture
from .language_model.llava_llama import LlavaLlamaForCausalLM, LlavaConfig
from .language_model.mosaic_language import LlavaMptForCausalLM, LlavaMptConfig
from .language_model.llava_mistral import LlavaMistralForCausalLM, LlavaMistralConfig
from .language_model.qwen_language import LlavaQwen2ForCausalLM, LlavaConfig

llava_arch = vision_architecture
sys.modules[f"{__name__}.llava_arch"] = vision_architecture

utils = upgrade
sys.modules[f"{__name__}.utils"] = upgrade
