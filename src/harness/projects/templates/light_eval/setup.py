# MIT License

# Copyright (c) 2024 The HuggingFace Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import find_namespace_packages, setup


source_roots = {
    "lighteval": "base/evaluation",
    "lighteval.chance_baseline": "tasks/chance_baseline",
    "lighteval.data": "datasets/evaluation_batches",
    "lighteval.dataset_inputs": "datasets/huggingface_hub",
    "lighteval.models": "models/adapters",
    "lighteval.metrics": "tasks/metrics",
    "lighteval.precheck": "tasks/precheck",
    "lighteval.study_configuration": "conf",
    "lighteval.tasks": "tasks/benchmarks",
    "lighteval.tasks.tasks": "tasks/core_benchmarks",
    "lighteval.tasks.multilingual.tasks": "tasks/multilingual_benchmarks",
    "lighteval.tasks.multilingual.utils": "tasks/language_support",
    "lighteval.tasks.templates": "tasks/prompt_templates",
}

packages = list(source_roots)
for public_root, directory in source_roots.items():
    packages.extend(
        f"{public_root}.{name}" for name in find_namespace_packages(where=directory, exclude=["*__pycache__*"])
    )

setup(packages=packages, package_dir=source_roots)
