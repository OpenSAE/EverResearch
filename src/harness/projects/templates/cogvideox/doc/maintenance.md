# CogVideoX maintenance

## Purpose and main function

Record the source revision, component ownership, and verification evidence for this template.

## Scope of application

Use this page after copying the template to choose resources, run a bounded check, or plan a full research workload.

Source snapshot: [THUDM/CogVideo@7a1af71545](https://github.com/THUDM/CogVideo/tree/7a1af7154511e0ce4e4be8d62faa8c5e5a3532d2). The upstream code, notices, and applicable license files travel with the template.

The installed `cogvideo` command calls the runtime in `base/`. Media input, pipeline loading, generation and training live under `datasets/`, `models/` and `tasks/`. Local demo, SAT and fine-tuning setup use the linked project guides.

Official 2B and 5B image-to-video checkpoints ran on the reference GPU. Generation, VAE output, and LoRA checkpoint readback were verified with Steamboat Willie sample workloads. The [run choices](experiment/formal_runs.md) record the per-workload counts and the stopping point of the five-minute LoRA profile.

## Verify a copied template

1. Follow the [environment guide](environment/README.md) to install project dependencies and obtain the selected data or model weights.
2. Run `python -IS .everresearch/maintain.py check` from the project root. When EverResearch is installed, `rh projects project check . --strict` runs the central layout check.
3. Use the project command and the smallest relevant real input to verify loading, computation, and result readback. Retain the effective settings and evidence in the copied project's experiment directory.

## Formal run choices

See [the command and workload guide](experiment/formal_runs.md) for concrete dataset and model choices, measured sample sizes, output formats, estimated time ranges, and known blockers. Estimates describe the reference machine. Recheck throughput on the target hardware with about ten work units and a five-minute cap before committing to long runs.
