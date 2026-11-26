# Whisper maintenance

## Purpose and main function

Record the source revision, component ownership, and verification evidence for this template.

## Scope of application

Use this page after copying the template to choose resources, run a bounded check, or plan a full research workload.

Source snapshot: [openai/whisper@86098128c0](https://github.com/openai/whisper/tree/86098128c0b4f24f0e2aa2994de830614b474227). The upstream code, notices, and applicable license files travel with the template.

Audio reading and feature extraction live in `datasets/audio/`, model construction and weights in `models/whisper/`, and recognition and evaluation in `tasks/`. The installed command and Python API use those implementations.

The reference run loaded official Turbo, Medium, and Base English weights on LibriSpeech and FLEURS. The timed workloads cover transcription, translation, timestamps, word error rate, and language identification. An invalid audio input was rejected before formal work. Full dataset runs are available as separate choices.

## Verify a copied template

1. Follow the [environment guide](environment/README.md) to install project dependencies and obtain the selected data or model weights.
2. Run `python -IS .everresearch/maintain.py check` from the project root. When EverResearch is installed, `rh projects project check . --strict` runs the central layout check.
3. Use the project command and the smallest relevant real input to verify loading, computation, and result readback. Retain the effective settings and evidence in the copied project's experiment directory.

## Formal run choices

See [the command and workload guide](experiment/README.md#formal-run-choices) for concrete dataset and model choices, measured sample sizes, output formats, estimated time ranges, and known blockers. Estimates describe the reference machine. Recheck throughput on the target hardware with about ten work units and a five-minute cap before committing to long runs.
