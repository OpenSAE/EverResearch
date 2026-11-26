from typing import List

from vllm.entrypoints.cli.main import main

from agentflow.instrumentation.model_server import instrument_vllm


if __name__ == "__main__":
    instrument_vllm()
    main()
