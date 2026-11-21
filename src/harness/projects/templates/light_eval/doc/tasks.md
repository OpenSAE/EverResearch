# Evaluation tasks

## Purpose and main functions

`tasks/` contains benchmark definitions, prompt preparation, sample and corpus metrics, a chance baseline, and checks of evaluation inputs.

## Scope

Use this page when selecting an evaluation or checking which implementation consumes a dataset or constructs a metric. Installed public imports remain under `lighteval.tasks` and `lighteval.metrics`.

## Shared parameters

Commands accept benchmark identifiers, comma-separated selections, and task lists. A suffix such as `truthfulqa:mc|0` selects a few-shot count. `lighteval tasks precheck <selection>` validates a sample for each selected task. Pipeline and baseline commands check loaded sample prompts and scoring choices before evaluation. Inspect AI checks that each selected dataset contains an evaluation sample before dispatching the evaluator. [Evaluation inputs and configuration](conf.md)

## Task implementations

- **Core benchmarks** group evaluations by research purpose. The registry reads each module's `TASKS_TABLE`, including the task identifiers, input splits, prompts, and selected metrics. [Core benchmark definitions](../tasks/core_benchmarks/)
- **Multilingual benchmarks** use language- and benchmark-specific source groups. The registry loads this collection when asked for multilingual tasks. [Multilingual benchmark definitions](../tasks/multilingual_benchmarks/)
- **Chance baseline** computes the uniform guessing rate for multiple-choice metrics, then uses the normal score writer. It can be run with `lighteval baseline truthfulqa:mc`. [Chance baseline implementation](../tasks/chance_baseline/__init__.py)

Pipeline results contain scores and optional sample details. The experiment guide explains how to reopen evaluation results. [Inspect saved evaluations](experiment.md)
