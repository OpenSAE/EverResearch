# Evaluation configuration

## Purpose and main function

The suite reads its project configuration to find the presets for generation, classification, and API-based classifiers.

## Scope of application

The configuration applies to the installed evaluation command, task loader, and classifier loader.

- [Project configuration](../conf/config.yaml)
- [Classification task presets](../conf/tasks/classification/presets.yaml)
- [Generation task presets](../conf/tasks/generation/presets.yaml)
- [OpenAI classifier presets](../conf/models/classifier_models/openai_presets.yaml)

The evaluation command still accepts task selections such as `xstest_response_refusal` and `bbq:openchoice`. A bare task name selects the `default` preset. Generation overrides replace the supplied keys in the selected preset's `hparams` map.

The CPU preset `bbq:cpu_multiple_choice` uses the generation model's tokenizer and a 64-token generation cap. `xstest:benign_only` measures over-refusal on the original benign prompts with the project keyword refusal grader. The existing BBQ and XSTest presets retain their original settings.
