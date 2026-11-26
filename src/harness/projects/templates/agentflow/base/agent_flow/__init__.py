"""Public AgentFlow interfaces for inference, serving, and training."""

from importlib import import_module

from .compatibility_imports import install_aliases

__version__ = "0.1.2"

_EXPORTS = {
    "AgentFlowClient": "client",
    "DevTaskLoader": "client",
    "flow_cli": "config",
    "LitAgent": "worker_agent",
    "configure_logger": "logging",
    "reward": "training.reward",
    "AgentFlowServer": "server",
    "Trainer": "training.trainer",
}
_TYPE_EXPORTS = (
    "Triplet", "Rollout", "Task", "TaskInput", "TaskIfAny", "RolloutRawResult",
    "Resource", "LLM", "PromptTemplate", "ResourceUnion", "NamedResources",
    "ResourcesUpdate", "GenericResponse", "ParallelWorkerBase",
)
__all__ = [*_EXPORTS, *_TYPE_EXPORTS]

install_aliases()


def __getattr__(name):
    if name in _EXPORTS:
        module = _EXPORTS[name]
    elif name in _TYPE_EXPORTS:
        module = "types"
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(f".{module}", __name__), name)
    globals()[name] = value
    return value
