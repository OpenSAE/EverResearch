# Point tracking, evaluation, and training

## Purpose and main function

Locate the research workflows and identify their outputs.

## Scope of application

Use this page to choose a command or maintain a task implementation.

- [Point tracking](../tasks/tracking/) uses the selected model and input frames. `track` runs the [precheck](../tasks/precheck/tracking.py) before writing coordinates, visibility, and an overlay video.
- [Benchmark evaluation](../tasks/evaluation/) runs the original TAP-Vid or Dynamic Replica workflow and writes the metrics and elapsed time to `result_eval_.json`.
- [Training](../tasks/training/) contains the original Kubric and pseudo-labeled real-video runners and the trajectory losses. Resume uses the selected checkpoint directory as before.
