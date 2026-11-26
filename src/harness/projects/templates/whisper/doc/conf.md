# Whisper configuration

## Purpose and main function

Identify the configuration that supplies command defaults and the flags that can override them.

## Scope of application

Read when selecting an inference mode, adjusting command defaults, or reproducing a recorded run.

The command loads [conf/config.json](../conf/config.json) from the installed package or the checkout in an editable installation. Its defaults are `turbo` for the model, `transcribe` for the task and `all` for transcript formats. The corresponding flags `--model`, `--task`, and `--output_format` override them. For the remainder of the defaults and available values, run `whisper --help`.

Pass `--language` to select the spoken language or let a multilingual model detect it. Use `--task translate` with a translation-capable multilingual model such as `medium`. Choose resources with `--device` and `--model_dir`. Use `--word_timestamps True` for timed words in the transcript. The Python API takes model and decoding arguments directly.
