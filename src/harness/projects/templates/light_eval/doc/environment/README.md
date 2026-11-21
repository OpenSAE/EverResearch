# Execution environment

## Purpose and scope

Set up the interpreter, model backend, datasets and caches for local evaluation. Consult the run records when reproducing saved results.

## Installation and resources

- Python 3.10 or newer is required by [pyproject.toml](../../pyproject.toml). From the checkout use `python -m pip install -e .`. Use `.[dev]` for development or select the backend extra declared in the installation file, such as `.[vllm]` or `.[sglang]`. Install dependencies into the interpreter that will run the evaluation.
- The Accelerate backend uses Transformers. Device and model requirements depend on the chosen checkpoint and backend. The CUDA GPT-2 example and saved TruthfulQA runs are documented in [experiment records](../experiment.md). Multilingual evaluation, vLLM, SGLang, and Nanotron require their corresponding optional dependencies.
- The workbench binding can be read with `rh projects resources lighteval`. The configured dataset inputs and model caches must be available to the selected interpreter. See the [quick tour](../code/evaluation/source/quicktour.mdx) and [configuration](../conf.md).

## Quick verification and run evidence

From the selected environment, run `python -c "import sys, lighteval; print(sys.executable, lighteval.__file__)"` and `lighteval tasks --help` to check the interpreter, import and command. Use the [maintenance record](../maintenance.md) for the scope of previous offline and backend checks. For a saved evaluation, open its manifest and effective configuration using the links in [experiment records](../experiment.md); these establish the model, data and options used in that execution.
