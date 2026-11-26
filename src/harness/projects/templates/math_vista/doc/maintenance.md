# MathVista maintenance

## Purpose and main function

Record the source and verified entry points for MathVista visual reasoning.

## Scope of application

Use this page after copying the template to install MathVista and choose an evaluation.

Source snapshot [lupantech/MathVista at 24b1478](https://github.com/lupantech/MathVista/tree/24b1478132e9bb6d32880ebf68ce57b7a0df92b5).

The `mathvista` entry point reads official image-question pairs from `datasets/`.
The Qwen adapter lives in `models/qwen_vision/`. Generation, answer extraction,
and scoring run under `tasks/` using compatible local or hosted backends.

1. Follow the [environment guide](environment/README.md) for dataset access and official local Qwen weights.
2. Run `python -IS .everresearch/maintain.py check` from the copied project.
3. Follow the [run choices](experiment.md) for the precheck commands, 10-item timings, 1,000-item estimates, and provider requirements.

The reference RTX 5090 ran the full three-stage pipeline on ten official
`testmini` pairs. Published result archives remain under `assets/`.
