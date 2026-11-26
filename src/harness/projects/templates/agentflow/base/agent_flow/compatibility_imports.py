"""Keep old import paths for implementations that moved during project adoption."""

import importlib
from importlib.abc import Loader, MetaPathFinder
from importlib.util import find_spec, spec_from_loader
import sys

_ALIASES = {
    "cli.vllm": "cli.serve_model",
    "litagent": "worker_agent",
    "trainer": "training.trainer",
    "reward": "training.reward",
    "models.formatters": "models.response_formats",
    "models.initializer": "models.initialize_tools",
    "models.utils": "models.serialization",
    "engine.dashscope": "engine.provider_dashscope",
    "engine.deepseek": "engine.provider_deepseek",
    "engine.litellm": "engine.provider_gateway",
    "engine.ollama": "engine.provider_ollama",
    "engine.openai": "engine.provider_openai",
    "engine.vllm": "engine.provider_vllm",
    "engine.xai": "engine.provider_xai",
    "instrumentation.agentops": "instrumentation.agent_tracing",
    "instrumentation.agentops_langchain": "instrumentation.agent_tracing_langchain",
    "instrumentation.litellm": "instrumentation.provider_gateway",
    "instrumentation.vllm": "instrumentation.model_server",
    "tracer.agentops": "tracer.agent_tracing",
    "tracer.http": "tracer.http_trace",
    "verl.dataset": "training_data.verl_dataset",
    "verl.entrypoint": "verl.main",
}


class AliasImport(MetaPathFinder, Loader):
    def find_spec(self, fullname, path=None, target=None):
        relative = fullname.removeprefix("agentflow.")
        if relative == fullname:
            return None
        legacy_package = relative.startswith("agentflow.")
        replacement = relative.removeprefix("agentflow.") if legacy_package else relative
        canonical = _ALIASES.get(replacement, replacement)
        if not legacy_package and canonical == relative:
            return None
        canonical = f"agentflow.{canonical}"
        spec = find_spec(canonical)
        if spec is None:
            return None
        alias = spec_from_loader(
            fullname, self, is_package=spec.submodule_search_locations is not None
        )
        alias.loader_state = canonical
        return alias

    def create_module(self, spec):
        return importlib.import_module(spec.loader_state)

    def exec_module(self, module):
        pass


def install_aliases():
    sys.meta_path.insert(0, AliasImport())
