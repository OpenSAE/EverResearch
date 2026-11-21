"""Resolve public Python module names after source paths are renamed.

Keep task discovery and direct imports on the same names so a built-in task
module is imported only once and retains its original identity.
"""

import sys
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location
from pathlib import Path


SOURCE_NAMES = {
    "lighteval": {
        "cli_args": "command_arguments",
        "utils": "utilities",
    },
    "lighteval.metrics": {
        "utils": "utilities",
    },
    "lighteval.metrics.imports": {
        "summac": "summac_consistency",
    },
    "lighteval.metrics.utils": {
        "stderr": "standard_error",
    },
    "lighteval.models": {
        "nanotron": "nanotron_adapter",
        "sglang": "sglang_adapter",
        "utils": "model_utilities",
        "vllm": "vllm_adapter",
    },
    "lighteval.tasks.multilingual": {
        "utils": "language_utilities",
    },
    "lighteval.tasks.multilingual.tasks": {
        "acva": "arabic_values",
        "afri_mgsm": "african_math",
        "afri_mmlu": "african_subjects",
        "afri_xnli": "african_entailment",
        "arcd": "arabic_reading",
        "belebele": "belebele_reading",
        "c3": "chinese_reading",
        "ceval": "chinese_exams",
        "chegeka": "russian_trivia",
        "cmath": "chinese_math",
        "cmmlu": "chinese_subjects",
        "cmnli": "chinese_multigenre_entailment",
        "cmrc2018": "chinese_machine_reading",
        "enem": "brazilian_entrance_exam",
        "faquad": "portuguese_reading",
        "flores200": "flores_translation",
        "fquad_v2": "french_reading_unanswerable",
        "germanquad": "german_reading",
        "hellaswag_tel": "telugu_situations",
        "hellaswag_tha": "thai_situations",
        "hellaswag_tur": "turkish_situations",
        "indicqa": "indic_questions",
        "kenswquad": "kenyan_reading",
        "m3exams": "multilingual_exams",
        "mgsm": "multilingual_grade_school_math",
        "mkqa": "multilingual_knowledge_questions",
        "mlmm_hellaswag": "translated_situations",
        "mlmm_mmlu": "translated_subjects",
        "mlmm_truthfulqa": "translated_truthfulness",
        "mlqa": "multilingual_extractive_questions",
        "ocnli": "chinese_native_entailment",
        "openai_mmlu": "openai_translated_subjects",
        "parus": "russian_causality",
        "rcb": "russian_commitment",
        "soqal": "french_open_questions",
        "thaiqa": "thai_questions",
        "tquad_v2": "thai_reading_unanswerable",
        "tydiqa": "typological_questions",
        "xcodah": "cross_lingual_adversarial_reasoning",
        "xcopa": "cross_lingual_causality",
        "xcsqa": "cross_lingual_commonsense",
        "xnli": "cross_lingual_entailment",
        "xnli2": "cross_lingual_entailment_pairs",
        "xquad": "translated_reading",
        "xstory": "cross_lingual_story",
        "xwinograd": "winograd_pronouns",
    },
    "lighteval.tasks.tasks": {
        "agieval": "human_exams",
        "aime": "invitational_math",
        "aimo": "math_olympiad",
        "anli": "adversarial_entailment",
        "arc_agi_2": "arc_agi_second",
        "asdiv": "arithmetic_word_problems",
        "bbq": "social_bias_questions",
        "bigbench": "big_bench",
        "boolq": "boolean_questions",
        "commonsenseqa": "commonsense_questions",
        "coqa": "conversational_questions",
        "entitymatching": "entity_matching",
        "gpqa": "graduate_science",
        "gsm8k": "grade_school_math",
        "headqa": "health_exams",
        "hellaswag": "situation_completion",
        "hle": "humanity_exam",
        "ifbench": "instruction_following_benchmark",
        "ifeval": "instruction_following_evaluation",
        "imdb": "movie_sentiment",
        "lcb": "live_code_bench",
        "legalsupport": "legal_support",
        "lexglue": "legal_understanding",
        "lextreme": "multilingual_legal_tasks",
        "logiqa": "logical_reading",
        "lsat_qa": "law_school_reasoning",
        "math_500": "math_five_hundred",
        "mathqa": "math_questions",
        "mathvista": "visual_math",
        "med": "medical_questions",
        "mgsm": "multilingual_grade_school_math",
        "mmlu": "academic_subjects",
        "musr": "multistep_reasoning",
        "narrativeqa": "narrative_questions",
        "openbookqa": "open_book_science",
        "piqa": "physical_reasoning",
        "prost": "physical_operations",
        "pubmedqa": "biomedical_questions",
        "qa4mre": "machine_reading_evaluation",
        "qasper": "paper_questions",
        "quac": "questions_in_context",
        "sacrebleu": "translation_scoring",
        "sciq": "science_questions",
        "simpleqa": "short_factual_questions",
        "siqa": "social_reasoning",
        "squad_v2": "reading_with_unanswerable_questions",
        "storycloze": "story_completion",
        "toxigen": "toxicity_generation",
        "triviaqa": "trivia_questions",
        "truthfulqa": "truthfulness_questions",
        "twitterAAE": "twitter_dialect",
        "webqs": "web_questions",
        "wikifact": "wiki_facts",
        "wikitext": "wiki_language_modeling",
        "winogrande": "winograd_pronoun_reasoning",
        "xcopa": "cross_lingual_causality",
        "xstory_cloze": "cross_lingual_story_completion",
        "xwinograd": "winograd_pronouns",
    },
    "lighteval.tasks.templates": {
        "boolq": "boolean_questions",
        "copa": "causal_reasoning",
        "hellaswag": "situation_completion",
        "multichoice": "multiple_choice",
        "nli": "natural_language_inference",
        "qa": "question_answering",
        "utils": "template_utilities",
    },
    "lighteval.utils": {
        "utils": "common_utilities",
    },
}


PUBLIC_NAMES = {
    package: {source: public for public, source in names.items()} for package, names in SOURCE_NAMES.items()
}


def public_module_name(package: str, source: str) -> str:
    """Get the import name used for a module or package found on disk."""
    return PUBLIC_NAMES.get(package, {}).get(source, source)


class SourceNameFinder:
    """Load renamed LightEval files under their original module names."""

    def find_spec(self, fullname, path=None, target=None):
        package, _, name = fullname.rpartition(".")
        if package.rsplit(".", 1)[-1].startswith("family_"):
            package = package.rsplit(".", 1)[0]
        source = SOURCE_NAMES.get(package, {}).get(name)
        if source is None or path is None:
            return None

        for entry in path:
            module = Path(entry) / (source + ".py")
            if module.is_file():
                return spec_from_file_location(fullname, module)

            directory = Path(entry) / source
            initializer = directory / "__init__.py"
            if initializer.is_file():
                return spec_from_file_location(fullname, initializer)
            if directory.is_dir():
                namespace = ModuleSpec(fullname, loader=None, is_package=True)
                namespace.submodule_search_locations = [str(directory)]
                return namespace
        return None


def register_source_names() -> None:
    """Register public module names for both editable and installed packages."""
    if not any(isinstance(finder, SourceNameFinder) for finder in sys.meta_path):
        sys.meta_path.append(SourceNameFinder())
