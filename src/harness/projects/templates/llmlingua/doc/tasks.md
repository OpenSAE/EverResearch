# Compression, preparation and evaluation tasks

The public `PromptCompressor` API compresses plain text and structured prompts, and exposes context-specific settings for retrieval. Use the [API guide](code/interface.md) to select an algorithm and interpret the returned token counts.

For an indexed batch, run `python -m llmlingua compress`. It loads the selected text field and model, checks the first eligible result, processes the remaining inputs and writes the compressed rows. The run saves the checked sample ID and count in `reports/precheck.json`. The manifest records how long startup took through precheck, whether formal execution started and any precheck failure. Add `--precheck` to inspect a single result using the same input, model and result writer. The [experiment guide](experiment.md) explains result readback.

The standalone benchmark compression script shares the checked batch implementation and can resume an explicitly named result. The paper workflows prepare classifier labels, train a token classifier and perform benchmark-specific downstream evaluation. Their [reproduction guide](../scripts/benchmark_reproduction/README.md) identifies the scripts and data expected at each stage.


| Reproduction task | Recorded or emitted result |
| --- | --- |
| [Teacher prompt compression](../tasks/distillation/compress.py) | Indexed prompts and compressed chunks consumed by word labeling. |
| [MeetingBank](../tasks/classifier_training/meetings.py) and [SecurityLingua](../tasks/classifier_training/security_pairs.py) training | Selected classifier weights and training metrics. Both trainers check a labeled forward pass before their training loop. |
| [Downstream generation and evaluation](../tasks/benchmark_evaluation/) | Benchmark-specific predictions, reference comparisons and scores. An input precheck opens the selected dataset and checks the first row before starting generation. |

The trainer reports its historical token accuracy convention and uses validation accuracy for checkpoint selection. Benchmark evaluators retain their original prompts and scoring functions. See their source and [reproduction commands](../scripts/benchmark_reproduction/README.md) for the inputs and explicit result paths.
