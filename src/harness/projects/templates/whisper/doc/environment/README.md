# Whisper runtime and checks

## Purpose and main function

Prepare the environment, audio and model files required by the command and the Python API.

## Scope of application

Use this guide for local installation, building the distribution, and running representative checks.

From the checkout, install into your selected Python environment and make FFmpeg available:

```sh
python -m pip install -e '.[dev]'
ffmpeg -version
python -m whisper --help
```

The package declares Python 3.8 or newer, PyTorch, NumPy, Numba, tiktoken and the platform-specific dependencies in [requirements.txt](../../requirements.txt). [pyproject.toml](../../pyproject.toml) declares the build and development dependencies. The command chooses CUDA when PyTorch can use it and CPU otherwise. Use `--device cpu --fp16 False` to choose full precision on CPU.

Pass readable audio to the command or supply mono 16 kHz samples through the Python API. The repository includes the [JFK test audio](../../tests/fixtures/speech/jfk.flac). The checkpoints are downloaded and verified against the original catalog when selected by name. Use `--model_dir PATH` or `whisper.load_model(..., download_root=PATH)` to reuse a local cache.

## Representative checks

```sh
python -m pytest -q tests --ignore=tests/test_transcribe.py
python -m pytest -q tests -k 'test_transcribe[tiny.en]'
python -m whisper tests/fixtures/speech/jfk.flac --model tiny.en --device cpu --threads 2 --precheck
```

The first command covers the audio loader, tokenizers, timing and normalizers. The latter checks use the official `tiny.en` weights. The [experiment guide](../experiment/README.md) shows full inference and readback.
