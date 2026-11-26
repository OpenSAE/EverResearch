# AgentFlow maintenance and verification

## Purpose and main function

Describe the EverResearch entry points and the source paths behind the original AgentFlow workflows.

## Scope of application

Use this page when maintaining the supplied AgentFlow snapshot or reproducing its adoption checks.
See the [environment guide](environment/README.md) for installation, model setup, and prechecks.

| Original workflow | Current implementation | Entry point |
| --- | --- | --- |
| Inference under `agentflow/agentflow/` and `quick_start.py` | [Solver](../tasks/inference/solver), [provider adapters](../models/providers/engine), [agent components](../models/components/models), and [tools](../base/agent_flow/tools) | `agentflow infer` or `python scripts/examples/quick_start.py` |
| Benchmark dispatch and scoring under `test/` | [Benchmark task](../tasks/benchmarks), [question loader](../datasets/benchmarks), and [batch launchers](../scripts/benchmarks) | `agentflow benchmark`, `agentflow score`, or a batch script |
| Training and rollout under `train/` and `agentflow/verl/` | [Training task](../tasks/training), [training data adapter](../datasets/training), [prechecks](../tasks/precheck), and [settings](../conf/config.yaml) | `agentflow train` and the [training launchers](../scripts/training) |
| Data preparation under `data/` | [Preparation code](../datasets/preparation) and [prepared data paths](../assets/prepared_data) | `python datasets/preparation/get_train_data.py` and `python datasets/preparation/prepare_aime.py` |
| Package, serving, and diagnostic scripts | [Package configuration](../pyproject.toml), [shared runtime](../base/agent_flow), [setup](../scripts/setup), and [diagnostics](../scripts/diagnostics) | `bash scripts/setup/install.sh` and the documented serving and diagnostic commands |

The package maps public `agentflow` imports to the owning source directories. Existing solver and
provider import paths resolve through compatibility aliases. The old nested distribution metadata is
kept [as provenance](code/legacy_package/source/pyproject.toml). The current package metadata
builds the actual provider, model, task, and dataset modules.

## Verification in a copied template

The documented development installation completed with Python 3.11. The offline
launcher and central strict check passed after installation and after building
the wheel. Setuptools writes its packaging output under `.build/`.

- The public Bamboogle precheck loaded the first of 125 bundled questions.
- The training preview resolved the Flow-GRPO arguments. With `BASE_DATA_DIR`
  pointing to the prepared data, the public training precheck opened 182,190
  training rows and 30 validation rows. The [input guide](../assets/prepared_data/training_inputs/README.md)
  records the source revisions and preparation commands.
- Both tests passed. The scoring reader opened the saved Bamboogle response and
  matched it to the bundled reference answer.

The preceding adoption trial also exercised inference and the benchmark writer
with a locally served HuggingFaceTB/SmolLM2-135M-Instruct model. Four other
benchmarks passed a live model probe: AIME 2024 with HuggingFaceTB/SmolLM2-360M-Instruct,
HotpotQA with Qwen/Qwen2.5-0.5B-Instruct, 2Wiki with Qwen/Qwen3-0.6B, and MuSiQue
with HuggingFaceTB/SmolLM-135M-Instruct.

Full Flow-GRPO training and external batch scoring remain unverified. The
published training configuration calls for eight GPUs plus CUDA, veRL, Ray,
and model services. The trial machine had one GPU. External scoring requires
credentials for the selected scoring provider.

## Read a saved benchmark response

After installing AgentFlow, run this from the template copy to exercise the
same reader used by `agentflow score` without contacting a scoring service.

```bash
python - <<'PYTHON'
from agentflow.benchmarks.calculate_score_unified import load_data

results = load_data(
    "assets/prepared_data/benchmark_questions/files/bamboogle/data.json",
    "assets/examples/benchmark_result/files",
    "base_response",
    task_name="bamboogle",
)
assert results["0"]["correct_answer"] == ["james madison"]
print(results["0"]["response"])
PYTHON
```
