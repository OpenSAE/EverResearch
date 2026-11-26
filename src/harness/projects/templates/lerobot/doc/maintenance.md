# LeRobot maintenance

## Purpose and main function

Record the source revision, component ownership, and verification evidence for this template.

## Scope of application

Use this page after copying the template to choose resources, run a bounded check, or plan a full research workload.

Source snapshot: [huggingface/lerobot@b07adcc5e3](https://github.com/huggingface/lerobot/tree/b07adcc5e3ce42c26a248236dbb3571f84c28c43). The upstream code, notices, and applicable license files travel with the template.

The [source ownership table](code/source_ownership.md) maps the 693 preserved Python module paths to their data, model, task and shared implementations. The project retains the `lerobot-*` commands and package imports.

The reference check used official Aloha and SO-101 data, exercised ACT training, and ran local and served simulator evaluation. The served evaluation produced scores and hit a PyAV frame-rate error when encoding video. Physical replay and rollout require the robot, cameras and calibration documented in the guide.

## Verify a copied template

1. Follow the [environment guide](environment/README.md) to install project dependencies and obtain the selected data or model weights.
2. Run `python -IS .everresearch/maintain.py check` from the project root. When EverResearch is installed, `rh projects project check . --strict` runs the central layout check.
3. Use the project command and the smallest relevant real input to verify loading, computation, and result readback. Retain the effective settings and evidence in the copied project's experiment directory.

## Formal run choices

See [the command and workload guide](experiment.md#formal-run-choices) for concrete dataset and model choices, measured sample sizes, output formats, estimated time ranges, and known blockers. Estimates describe the reference machine. Recheck throughput on the target hardware with about ten work units and a five-minute cap before committing to long runs.
