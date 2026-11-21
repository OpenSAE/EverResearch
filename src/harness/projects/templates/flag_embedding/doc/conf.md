# Evaluation and fine-tuning configuration

The Python evaluation commands parse options with Hugging Face Transformers. The [shared evaluation arguments](../base/flag_embedding/interfaces/evaluation/arguments.py) load the retrieval and report defaults from [conf/config.json](../conf/config.json). Each benchmark can specialize them. Use `python -m FlagEmbedding.evaluation.custom --help` or `python -m FlagEmbedding.evaluation.beir --help` to view the options accepted by that command.

| Option | Effect |
| --- | --- |
| `--dataset_dir`, `--dataset_names`, `--splits` | Select the data location, named collections and splits. Custom evaluation uses local JSON Lines files and defaults to the test split. BEIR can obtain its supported datasets when local files are unavailable. |
| `--embedder_name_or_path`, `--embedder_model_class`, `--reranker_name_or_path` | Select the mandatory embedding model, its implementation when the model name cannot identify it, and an optional reranker. |
| `--devices`, `--use_fp16` | Select the inference devices and precision. Precision support depends on the model and device. |
| `--search_top_k`, `--rerank_top_k`, `--k_values` | Select the number of dense and reranked candidates and the cutoffs used for metrics. The shared defaults are 1,000 dense candidates, 100 reranked candidates and cutoffs of 1, 3, 5, 10, 100 and 1,000. The retrieval precheck requires a positive candidate count for each stage that computes new rankings. |
| `--output_dir`, `--eval_output_path`, `--eval_output_method` | Place rankings and the combined report. The shared defaults are `./search_results` and `./eval_results.md`, relative to the calling working directory. Select the report format explicitly if using a different extension. |
| `--overwrite`, `--precheck_only` | Evaluation can reuse rankings unless overwrite is enabled. Custom evaluation also accepts `--precheck_only` to verify one local sample per selected split and exit before writing full rankings. |

The [evaluation launchers](../scripts/examples/evaluation/README.md) supply their own preset models, output paths, and other values. The custom launcher controls the dataset identity, data directory, embedder and output paths through its positional arguments. Pass optional model, device, split and metric settings after them.

The [fine-tuning examples](../scripts/examples/fine_tuning/) use Transformers command options and pass a DeepSpeed JSON file with `--deepspeed`. The [full-parameter configuration](../scripts/examples/fine_tuning/deepspeed_full_parameters.json) uses ZeRO stage 0. The [partitioned optimizer configuration](../scripts/examples/fine_tuning/deepspeed_partition_optimizer.json) uses stage 1. The example launchers select the file for each model family.
