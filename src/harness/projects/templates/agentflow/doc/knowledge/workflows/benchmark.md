## Benchmarking Guide
Here we provide a detailed benchmarking guide to reproduce the paper’s results across ten benchmarks.

### Serving Models with VLLM

We provide an automated VLLM serving script in [`scripts/serve_vllm.sh`](../../../scripts/serve_vllm.sh). 

```bash
bash scripts/serve_vllm.sh
```

**Configuration**

You can configure the following parameters in [`scripts/serve_vllm.sh`](../../../scripts/serve_vllm.sh):

| Parameter | Description | Default                            |
|-----------|-------------|------------------------------------|
| MODEL | Model path to serve (HuggingFace or local) | `"AgentFlow/agentflow-planner-7b"` |
| GPU | GPU device ID(s) to use | `"0"`                              |
| PORT | VLLM serving port | `8000`                             |
| TP | Tensor-parallel-size | `1`                                |


We provide task-specific scripts to run benchmarks. These scripts execute our agentic system, save the outputs, and automatically invoke the LLM for evaluation.

To run a specific benchmark (e.g., Bamboogle):
```bash
bash scripts/benchmarks/bamboogle_questions/run.sh
```

You can configure benchmark settings in each task's `run.sh` script (e.g., `scripts/benchmarks/bamboogle_questions/run.sh`).

Example configuration in `scripts/benchmarks/bamboogle_questions/run.sh`:
```bash
#!/bin/bash

# Configuration
TASK="bamboogle"
THREADS=20
DATA_FILE_NAME="data.json"

MODELS=(
    "8000:vllm-AgentFlow/agentflow-planner-7b,AgentFlow-7B,\
Base_Generator_Tool|Python_Coder_Tool|Google_Search_Tool|Wikipedia_Search_Tool,\
gpt-4o-mini|gpt-4o-mini|Default|Default,\
trainable|gpt-4o|gpt-4o|gpt-4o"
)
```

**Step:**

**1. Set Parallelism**
Set the data parallelism for inference (too high a value may exceed API thresholds).
```bash
THREADS=20  # Number of parallel workers
```

**2. Select Tasks**

Choose a launcher in `scripts/benchmarks/`. Each launcher selects one prepared dataset.

**3. Define Models**

Specify models with their configurations:
```bash
MODELS=(
      "8000:vllm-AgentFlow/agentflow-planner-7b,AgentFlow-7B,Base_Generator_Tool|Python_Coder_Tool|Google_Search_Tool|Wikipedia_Search_Tool,dashscope-qwen2.5-7b-instruct|dashscope-qwen2.5-7b-instruct|Default|Default"
)
```

**Format:** `"port:model_path,label,Tool1|Tool2,engine1|engine2,planner|fixed|verifier|executor"`
- **port**: VLLM serving port (leave empty for API-based models)
- **model_path**: Model engine name (e.g., `gpt-4o` or `vllm-AgentFlow/agentflow-planner-7b`)
- **label**: Display name for results (used for folder naming)
- **tools**: Pipe-separated tool list (e.g., `Tool1|Tool2`)
- **tool_engine**: Pipe-separated engines for each tool
- **model_engines**: Configuration for the four agent modules (e.g., `trainable|gpt-4o|gpt-4o|gpt-4o`)

**Note**: For all agents except the `planner`, we now use [gpt-4o](https://github.com/lupantech/AgentFlow/blob/main/models/components/models/planner.py#L11) by default to ensure high-quality reasoning.



### Results Organization

Batch runs use `experiment/<dataset>/benchmark/official_run/` by default.
The `logs` directory holds per-question logs, and `artifacts` holds answers and scores.
Both directories group files by the original model display label. Intermediate caches
go under `tmp`. Set `AGENTFLOW_OUTPUT_ROOT` to use a separate run destination.
To read an earlier run, pass its result directory to `agentflow score --result_dir`.

### Key Result Files

| File | Description |
|------|-------------|
| `final_scores_direct_output.json` | Aggregate metrics: accuracy, correct/wrong counts, tool usage statistics |
| `final_results_direct_output.json` | Detailed per-problem results with verification and analysis |
| `output_{i}.json` | Complete execution trace: query, response, memory, tool calls |
| `final_score_direct_output.log` | Detailed scoring process log |
