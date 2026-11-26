# CogVideoX generation results

## Purpose and main function

Locate generated videos and the settings needed to inspect or repeat a run.

## Scope of application

This guide covers the managed output of `cogvideo generate`. Passing `--output_path` exports directly to the specified file.

Use the [formal run choices](formal_runs.md) to select a complete workload and plan GPU time.

A managed generation writes to `experiment/<input>/<model>/video_generation/<purpose>/executions/<execution>/`. The command prints the directory and artifact path. Use `--purpose` and `--execution` to name experiments and repeated runs. Each run stores `config.json`, `metadata/manifest.json`, and `artifacts/generated_video.mp4` after a successful export.

Run `cogvideo inspect <run-directory>` to read the saved configuration and manifest. The [VAE encoding asset](../../assets/history_experiment/vae_encoding/README.md) preserves the pretrained demo's original encoded tensor and points to its decoding command.
