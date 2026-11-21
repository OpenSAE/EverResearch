# LLMLingua-2 Experiments

## Getting Started

From the checkout root, install the package used by the reproduction launchers:

```bash
python -m pip install -e .
```

To collect your own data using GPT-4, install the following packages:
```bash
python -m pip install openai==0.28 datasets spacy
python -m spacy download en_core_web_sm
```

Set `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` before running teacher compression or downstream generation. The `--model_name` or `--model_name_or_path` used by those commands names an Azure deployment. `OPENAI_API_VERSION` can override the default API version.

To train your own compressor on the collected data, install:
```bash
pip install scikit-learn
pip install tensorboard
```

## Data collection

We release our collected GPT-4 compression result at [HF](https://huggingface.co/datasets/microsoft/MeetingBank-LLMCompressed) after review. We also provide the whole data collection pipeline at [**collect_data.sh**](data_collection/collect_data.sh) to help you construct your custom compression dataset.

## Model Training

After running the collection script, run [train.sh](model_training/train.sh) to train a compressor. Both scripts resolve paths from the checkout and use `experiment/` by default. Set `LLMLINGUA_EXPERIMENT_ROOT` to the same absolute directory for both stages to share the filtered annotations. The training script writes its model artifacts and TensorBoard logs in the training destination. Use annotation files from your own or another trusted run.

## Evaluation

Run [compress.sh](evaluation/scripts/compress.sh) to produce the four benchmark prompt files. Run [evaluate.sh](evaluation/scripts/evaluate.sh) to score those outputs with the downstream answer model. Both scripts can be launched from any working directory. Their inputs default to the checkout's `data/` directory and outputs to `experiment/`. Set `LLMLINGUA_DATA_ROOT` and `LLMLINGUA_EXPERIMENT_ROOT` to absolute paths to use other locations. The scripts list the required input filenames and matching output destinations for each benchmark. For GSM8K, evaluation reads both the compressed demonstrations and the separate test questions and reference answers.

For a new single-benchmark run with its own configuration and manifest, use [the package batch command](../../doc/README.md#batch-compression). For an existing result, the standalone Python programs still accept explicit input and output paths.


The reproduction names below also identify the packaged implementations called by the existing launchers.

| Workflow | Implementation |
| --- | --- |
| Format MeetingBank transcripts, label original words, and filter aligned samples | [Prompt annotation datasets](../../datasets/prompt_annotation/) |
| Generate teacher compressions | [Distillation task](../../tasks/distillation/compress.py), [Azure teacher adapter](../../models/azure_completion/teacher.py), and [compression instructions](../../conf/tasks/distillation/compression_instructions.json) |
| Train the MeetingBank classifier | [MeetingBank training task](../../tasks/classifier_training/meetings.py), [training data adapter](../../datasets/classifier_training/__init__.py), and [Transformer factory](../../models/transformer_compression/__init__.py) |
| Compress benchmark inputs | [Indexed compression task](../../tasks/compression/__init__.py), dispatched by [the shared runtime](../../base/prompt_compression/runtime/compression.py) |
| Score benchmark predictions | [Benchmark evaluation tasks](../../tasks/benchmark_evaluation/) and the [Azure completion adapter](../../models/azure_completion/client.py) |

For downstream scoring, the MeetingBank and LongBench evaluators use the packages imported by the [metric implementation](../../tasks/benchmark_evaluation/metrics.py). ZERO-SCROLLS uses the benchmark's separately distributed metric and a `datasets` version that provides `load_metric`. The separate reasoning evaluator accepts `--load_data_from` for its test questions.
