import warnings

AGENTOPS_INSTALLED = False
AGENTOPS_LANGCHAIN_INSTALLED = False
LITELLM_INSTALLED = False
VLLM_INSTALLED = False

try:
    from . import agentops

    AGENTOPS_INSTALLED = True
except ImportError:
    pass

try:
    from . import litellm

    LITELLM_INSTALLED = True
except ImportError:
    pass


try:
    from . import agentops_langchain

    AGENTOPS_LANGCHAIN_INSTALLED = True
except ImportError:
    pass


def instrument_all():
    if AGENTOPS_INSTALLED:
        from .agent_tracing import instrument_agentops

        instrument_agentops()
    else:
        warnings.warn("agentops is not installed. It's therefore not instrumented.")

    if LITELLM_INSTALLED:
        from .provider_gateway import instrument_litellm

        instrument_litellm()
    else:
        warnings.warn("litellm is not installed. It's therefore not instrumented.")

    if VLLM_INSTALLED:
        from .model_server import instrument_vllm

        instrument_vllm()
    else:
        warnings.warn("vllm is not installed. It's therefore not instrumented.")

    if AGENTOPS_LANGCHAIN_INSTALLED:
        from .agent_tracing_langchain import instrument_agentops_langchain

        instrument_agentops_langchain()
    else:
        warnings.warn("Agentops-langchain integration is not installed. It's therefore not instrumented.")


def uninstrument_all():
    if AGENTOPS_INSTALLED:
        try:
            from .agent_tracing import uninstrument_agentops

            uninstrument_agentops()
        except ImportError:
            warnings.warn("agentops is installed but uninstrument_agentops could not be imported.")
    else:
        warnings.warn("agentops is not installed. It's therefore not uninstrumented.")

    if LITELLM_INSTALLED:
        try:
            from .provider_gateway import uninstrument_litellm

            uninstrument_litellm()
        except ImportError:
            warnings.warn("litellm is installed but uninstrument_litellm could not be imported.")
    else:
        warnings.warn("litellm is not installed. It's therefore not uninstrumented.")

    if VLLM_INSTALLED:
        try:
            from .model_server import uninstrument_vllm

            uninstrument_vllm()
        except ImportError:
            warnings.warn("vllm is installed but uninstrument_vllm could not be imported.")
    else:
        warnings.warn("vllm is not installed. It's therefore not uninstrumented.")

    if AGENTOPS_LANGCHAIN_INSTALLED:
        try:
            from .agent_tracing_langchain import uninstrument_agentops_langchain

            uninstrument_agentops_langchain()
        except ImportError:
            warnings.warn("agentops_langchain is installed but uninstrument_agentops_langchain could not be imported.")
    else:
        warnings.warn("Agentops-langchain integration is not installed. It's therefore not uninstrumented.")
