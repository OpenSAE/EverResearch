"""Package the evaluation suite using its project-owned implementation directories."""

from setuptools import find_packages, setup


TASK_PATHS = {
    "classification": {
        "beavertails": "beaver_tails",
        "harmbench": "harm_bench",
        "saferlhf": "safe_feedback",
        "simplesafetytests": "simple_safety_tests",
        "toxicchat": "toxic_chat",
    },
    "generation": {
        "alpacaeval": "alpaca_evaluation",
        "bbh": "big_bench_hard",
        "bbq": "bias_benchmark",
        "gsm8k": "grade_school_math",
        "harmbench": "harm_bench",
        "mmlu": "multitask_understanding",
        "mtbench": "multi_turn_bench",
        "strongreject": "strong_reject",
        "toxigen": "toxicity_generation",
        "trustllm_jailbreaktrigger": "trust_jailbreak_trigger",
        "truthfulqa": "truthful_answers",
        "wildbench": "wild_bench",
        "wildguardtest": "wild_guard_test",
        "wildjailbreak": "wild_jailbreak",
        "wmdp": "hazardous_knowledge",
        "xstest": "exaggerated_safety_test",
    },
}


package_dirs = {
    "evaluation": "base/evaluation",
    "evaluation.eval": "base/evaluation_entry",
    "evaluation.utils": "base/evaluation_utilities",
    "evaluation.models": "models/generators",
    "evaluation.tasks": "tasks",
    "src": "base/shared_code",
    "src.classifier_models": "models/classifier_models",
    "ai2_safety_datasets": "datasets",
    "ai2_safety_configuration": "conf",
    "ai2_safety_benchmark_inputs": "assets/source_data/benchmark_inputs/files",
}
for mode, names in TASK_PATHS.items():
    for public_name, directory_name in names.items():
        package_dirs[f"evaluation.tasks.{mode}.{public_name}"] = f"tasks/{mode}/{directory_name}"

packages = set(package_dirs)
packages.update(f"src.{name}" for name in find_packages("base/shared_code"))
packages.add("src.templates")
packages.update(f"ai2_safety_datasets.{name}" for name in find_packages("datasets"))
for mode in TASK_PATHS:
    packages.add(f"evaluation.tasks.{mode}")
    for name in find_packages(f"tasks/{mode}"):
        if name not in TASK_PATHS[mode].values():
            packages.add(f"evaluation.tasks.{mode}.{name}")
packages.update(("evaluation.tasks.metrics", "evaluation.tasks.precheck"))

setup(
    name="safety-eval",
    version="1.0",
    description="Evaluation of generative language models and safety classifiers",
    author="Allen Institute for AI",
    python_requires=">=3.10",
    package_dir=package_dirs,
    packages=sorted(packages),
    package_data={
        "ai2_safety_configuration": ["*.yaml", "tasks/*/*.yaml", "models/*/*.yaml"],
        "ai2_safety_benchmark_inputs": ["*/*/*.*", "*/*/*/*.*"],
    },
    entry_points={
        "console_scripts": [
            "safety-eval=evaluation.eval:main",
            "safety-eval-classification=evaluation.run_all_classification_benchmarks:cli",
            "safety-eval-generation=evaluation.run_all_generation_benchmarks:cli",
        ],
    },
)
