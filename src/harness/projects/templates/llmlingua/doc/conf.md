# Compression configuration

The public [library API](code/interface.md) defines its Python method defaults. Explicit arguments override them. The batch command and standalone evaluation compression script share [argument definitions](../base/prompt_compression/runtime/compression.py). Both read the default checkpoint from [config.yaml](../conf/config.yaml). The managed command also uses the dataset aliases from that file to choose result paths. An explicit command-line value takes precedence over the configured checkpoint. Use `--help` to list flags or `--show-config` to see the effective settings before data or model loading.

| Batch setting | Default and effect |
| --- | --- |
| `--model_name` | `microsoft/llmlingua-2-xlm-roberta-large-meetingbank`. Chooses the LLMLingua-2 token classifier. |
| `--model_revision` | Uses the model repository's default revision when omitted. Supply a commit, tag, or branch to select a specific Hugging Face checkpoint and record it in the run configuration. |
| `--device_map` | `cuda`. Use `cpu` to place the compressor on the CPU. |
| `--load_origin_from`, `--load_key`, `--save_key` | Input path is required. Read `prompt` and write `compressed_prompt` by default. Reading `prompt_list` also writes `compressed_prompt_list` when the compressor returns segments. |
| `--compression_rate`, `--target_token` | A default retained fraction of `0.5`. A positive token target overrides the fraction during token-level compression. The default `-1` leaves the token target unset. |
| `--use_token_level_filter`, `--use_context_level_filter` | Token filtering is enabled and context filtering is disabled by default. Use the matching `--no-` flag to turn either off explicitly. |
| `--target_context`, `--context_level_compression_rate`, `--context_level_target_token` | Defaults are `-1`, `1.0` and `-1`. With context filtering enabled, a context token target takes precedence over the context count and retention fraction. When all context settings are at their default, the algorithm derives a context budget from the selected overall rate or token target. |
| `--force_tokens`, `--drop_consecutive`, `--force_reserve_digit` | By default there are no forced tokens, consecutive forced tokens can be deduplicated, and digit retention is disabled. List tokens separated by commas and write `\n` for a newline. |
| `--dataset`, `--name`, `--limit` | Supply the dataset identity. The default purpose is `prompt_compression`. Supply a positive limit to select a prefix of the non-null samples. |
| `--experiment-root` | Defaults to the LLMLingua checkout's `experiment/`. Supply a destination when running the wheel outside a checkout. |
| `--show-config` | Prints the effective settings and canonical component paths as JSON. |
| `--precheck` | Builds the selected compressor and writes one eligible sample through the normal result writer. Uses the purpose `compression_precheck` unless explicitly named. |
| Standalone `--save_path` | Specifies the direct destination of the original evaluation compression script. The managed command determines its own run path. |

Python callers can still choose the default causal compressor or explicitly select LLMLingua-2 and SecurityLingua through the `PromptCompressor` constructor. The model configuration forwards options such as `revision`, `trust_remote_code` and `torch_dtype` to the Transformers loader. The loader applies `pad_to_left` internally and uses its own copy of the given settings.
