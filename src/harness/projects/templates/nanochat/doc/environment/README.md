# Environment

Use `uv sync --extra cpu --group dev` on CPU or `uv sync --extra gpu --group dev`
on a supported CUDA system. Activate `.venv` or run the commands with its Python.
These commands install the project along with PyTorch, PyArrow, and tokenizer dependencies.

`NANOCHAT_BASE_DIR` locates the tokenizer, checkpoints and original cache directory.
The optional `NANOCHAT_CLIMBMIX_DIR` and `NANOCHAT_TASK_DATA_DIR` point to existing
ClimbMix parquet shards and conversational parquet exports. With EverResearch online,
`rh projects resources nanochat` displays the local resource bindings.

Run `rh projects project check --strict .` for structure and
`python -m pytest -m 'not slow'` for quick code checks.

Choose a writable state directory outside the source tree. The downloader
writes a training shard and the fixed validation shard beneath that directory.

```sh
export NANOCHAT_BASE_DIR="$PWD/../data/nanochat"
python -m nanochat.dataset -n 1
```

To reuse existing data, set `NANOCHAT_CLIMBMIX_DIR` to the directory containing
the ClimbMix shards and `NANOCHAT_TASK_DATA_DIR` to the directory containing
conversation data. Otherwise NanoChat prepares those datasets in its cache
on first use. Run `python -m nanochat precheck --help` for task and model
options. Use `--config /path/to/NanoChat/conf/config.json` outside the checkout.
