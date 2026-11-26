# Ai2 Safety Eval maintenance

## Purpose and main function

Describe the upstream source, supported workflows, and verification for this template.

## Scope of application

Use this guide after copying the template to install dependencies, check the structure, or choose a real research workload.

Source snapshot [allenai/safety-eval at 060cc90](https://github.com/allenai/safety-eval/tree/060cc903d64703214c549b5c3a30ea8ceef2e588).

Real safety classification, refusal scoring, local generation, and aggregate reports. Nine classification presets and two generation evaluations ran locally. Five additional presets require authorized access to WildGuardMix or XSTest-Response.

1. Follow the [environment guide](environment/README.md) to install the project and prepare inputs.
2. Run `python -IS .everresearch/maintain.py check` from the copied project root.
3. See the [run and verification guide](experiment/defensive_evaluation.md) for commands, recorded evidence, and requirements.
