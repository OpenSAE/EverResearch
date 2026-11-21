from pathlib import Path

from setuptools import find_packages, setup


package_source = Path("base/flag_embedding")
public_package = "FlagEmbedding"

# The wheel and editable installation both expose the original import namespace.
public_package_parts = {
    "interfaces": "abc",
    "fine_tuning": "finetune",
    "embedding": "embedder",
    "ranking": "reranker",
    "layer_wise": "layerwise",
    "multifunctional": "m3",
    "in_context": "icl",
    "beir_benchmark": "beir",
    "miracl_benchmark": "miracl",
    "mkqa_benchmark": "mkqa",
    "mldr_benchmark": "mldr",
    "msmarco_benchmark": "msmarco",
    "mteb_benchmark": "mteb",
    "compatibility": "utils",
    "metrics": "utils",
    "text_processing": "utils",
    "abstract_arguments": "AbsArguments",
    "abstract_dataset": "AbsDataset",
    "abstract_modeling": "AbsModeling",
    "abstract_runner": "AbsRunner",
    "abstract_trainer": "AbsTrainer",
    "abstract_embedding": "AbsEmbedder",
    "abstract_ranking": "AbsReranker",
}

package_locations = {}


def register_package(source, logical_path="", *, exclude=()):
    """Publish a source directory and its packages at their established import paths."""
    source = Path(source)
    for child in ["", *find_packages(source, exclude=exclude)]:
        parts = [part for part in (logical_path, child) if part]
        logical_parts = ".".join(parts).split(".") if parts else ()
        public_parts = [public_package, *(public_package_parts.get(part, part) for part in logical_parts)]
        package_locations[".".join(public_parts)] = str(source.joinpath(*child.split(".")))


register_package(package_source)
register_package("tasks/evaluation", "evaluation", exclude=("answer_metrics",))
register_package("tasks/evaluation/answer_metrics", "evaluation.mkqa_benchmark.text_processing")
register_package("tasks/precheck", "precheck")
register_package("models/embedding", "inference.embedding", exclude=("in_context", "multifunctional"))
register_package("models/embedding/in_context", "inference.embedding.decoder_only.in_context")
register_package("models/embedding/multifunctional", "inference.embedding.encoder_only.multifunctional")
register_package("models/ranking", "inference.ranking", exclude=("backbones", "layer_wise"))
register_package("models/ranking/backbones", "inference.ranking.decoder_only.models")
register_package("models/ranking/layer_wise", "inference.ranking.decoder_only.layer_wise")

for loader in sorted(Path("datasets/evaluation").glob("*/__init__.py")):
    name = loader.parent.name
    parent = "interfaces.evaluation" if name == "common" else f"evaluation.{name}"
    register_package(loader.parent, f"{parent}.data_loader")

for component in ("evaluator", "searcher", "metrics"):
    register_package(f"tasks/retrieval/{component}", f"interfaces.evaluation.{component}")

fine_tuning_variants = {
    "embedding": {
        "decoder": "decoder_only.base",
        "encoder": "encoder_only.base",
        "in_context": "decoder_only.in_context",
        "multifunctional": "encoder_only.multifunctional",
    },
    "ranking": {
        "decoder": "decoder_only.base",
        "encoder": "encoder_only.base",
        "layer_wise": "decoder_only.layer_wise",
    },
}
for kind, variants in fine_tuning_variants.items():
    shared = f"interfaces.fine_tuning.{kind}"
    register_package(f"datasets/fine_tuning/{kind}", f"{shared}.abstract_dataset")
    register_package(f"models/{kind}_training/common", f"{shared}.abstract_modeling")
    register_package(f"tasks/fine_tuning_support/{kind}", f"{shared}.abstract_trainer")
    for name, variant in variants.items():
        logical_path = f"fine_tuning.{kind}.{variant}"
        register_package(f"tasks/{kind}_tuning/{name}", logical_path)
        for initializer in sorted(Path(f"models/{kind}_training").glob(f"{name}_*/__init__.py")):
            module = initializer.parent.name[len(name) + 1:]
            register_package(initializer.parent, f"{logical_path}.{module}")

register_package("datasets/fine_tuning/in_context", "fine_tuning.embedding.decoder_only.in_context.dataset")

register_package("conf", "_defaults")

with open("README.md", mode="r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name='FlagEmbedding',
    version='1.4.2',
    description='FlagEmbedding',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='2906698981@qq.com',
    url='https://github.com/FlagOpen/FlagEmbedding',
    packages=list(package_locations),
    package_dir=package_locations,
    package_data={f"{public_package}._defaults": ["config.json"]},
    include_package_data=True,
    install_requires=[
        'torch>=1.6.0',
        'transformers>=4.44.2,<6.0.0',
        'datasets>=2.19.0',
        'accelerate>=0.20.1',
        'sentence_transformers',
        'peft',
        'ir-datasets',
        'sentencepiece',
        'protobuf'
    ],
    extras_require={
        'finetune': ['deepspeed', 'flash-attn'],
        'evaluation': ['faiss-cpu', 'pytrec-eval-terrier'],
    },
)
