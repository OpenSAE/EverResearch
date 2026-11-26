# WhisperResearch guide

## Purpose and main function

Find the Whisper entry points, the implementations they call, and the checks for a local installation.

## Scope of application

Read this guide when setting up, running, or maintaining this checkout.

| Guide | Contents |
| --- | --- |
| [Environment](environment/README.md) | Installation, audio and model requirements, and test commands. |
| [Experiments](experiment/README.md) | Formal run choices, measured runtimes, precheck, and result readback. |
| [Configuration](conf.md) | Command defaults and run options. |
| [Evaluation data](data.md) | Data selections and annotations used for the upstream paper. |
| [Model card](knowledge/model_card.md) | Whisper variants, training provenance, and limitations. |
| [Notebooks](../scripts/examples/README.md) | LibriSpeech and multilingual evaluation workflows. |

## Source ownership

| Source | Used by |
| --- | --- |
| [base/whisper](../base/whisper/) | Command parsing, public Python exports, utility functions and result writing. |
| [datasets/audio](../datasets/audio/) | Audio decoding, resampling and log-Mel features shared by the command and Python API. |
| [models/whisper](../models/whisper/) | Model architecture, official checkpoint catalog, weight loading and tokenizer. |
| [tasks/speech](../tasks/speech/) | Transcription and translation, token decoding, language identification, and word timing with optional GPU acceleration. |
| [tasks/evaluation/text](../tasks/evaluation/text/) | Text normalization used in evaluation notebooks and the Python API. |
| [tasks/precheck](../tasks/precheck/) | Bounded audio read and decoding check before a recorded experiment. |
| [assets](../assets/) | Runtime feature and text tables, released evaluation references, and documentation figures. |
| [tests](../tests/) | Audio, tokenization, alignment, normalization and model regressions. |

The package mapping in [pyproject.toml](../pyproject.toml) connects these source paths to the public `whisper` modules. After install, either `whisper` or `python -m whisper` starts the command.

- [Maintenance and formal run choices](maintenance.md) records ownership, validation evidence, and run conditions.
