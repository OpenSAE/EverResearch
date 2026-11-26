"""Select classifiers and load a backend only when it is used."""

from typing import Any

from .base import ConversationTurn, LegacySafetyClassifierBase, Role, SafetyClassifierBase


def load_classifier_model(model_name: str, **kwargs) -> SafetyClassifierBase:
    named_openai_classifiers = {
        "GPTHarmfulDetectorV0UserRequestOnly",
        "GPTRefusalDetectorV0JSON",
    }

    if model_name in {"QwenGuardPrompt", "QwenGuardResponse"}:
        from .qwen_guard import QwenGuard

        return QwenGuard(response_moderation=model_name == "QwenGuardResponse", **kwargs)
    elif model_name == "WildGuard":
        from src.classifier_models.wild_guard import WildGuard

        return WildGuard(**kwargs)
    elif model_name == "LlamaGuardUserRequest":
        from src.classifier_models.llama_guard import LlamaGuardUserRequest

        return LlamaGuardUserRequest(**kwargs)
    elif model_name == "LlamaGuardModelResponse":
        from src.classifier_models.llama_guard import LlamaGuardModelResponse

        return LlamaGuardModelResponse(**kwargs)
    elif model_name == "HarmbenchClassifier":
        from src.classifier_models.harmbench_classifier import HarmbenchClassifier

        return HarmbenchClassifier(**kwargs)
    elif model_name == "HarmbenchValidationClassifier":
        from src.classifier_models.harmbench_classifier import HarmbenchValidationClassifier

        return HarmbenchValidationClassifier(**kwargs)
    elif model_name == "AegisLlamaGuardPermissive":
        from src.classifier_models.aegis import AegisLlamaGuardPermissive

        return AegisLlamaGuardPermissive(**kwargs)
    elif model_name == "AegisLlamaGuardDefensive":
        from src.classifier_models.aegis import AegisLlamaGuardDefensive

        return AegisLlamaGuardDefensive(**kwargs)
    elif model_name == "LlamaGuard2":
        from src.classifier_models.llama_guard import LlamaGuard2

        return LlamaGuard2(**kwargs)
    elif model_name == "BeaverDam":
        from src.classifier_models.beaver_dam import BeaverDam

        return BeaverDam(**kwargs)
    elif model_name == "sorrybench":
        from src.classifier_models.sorry_bench import SorryBenchClassifier

        return SorryBenchClassifier(**kwargs)
    elif model_name == "StrongRejectClassifier":
        from src.classifier_models.strong_reject_classifier import StrongRejectClassifier

        return StrongRejectClassifier(**kwargs)
    elif model_name == "StrongRejectLogitClassifier":
        from src.classifier_models.strong_reject_logit_classifier import StrongRejectLogitClassifier

        return StrongRejectLogitClassifier(**kwargs)
    elif model_name == "Qwen3MC":
        from src.classifier_models.qwen_mc_match import QwenMC

        return QwenMC(**kwargs)
    elif model_name == "StrongRejectLogProbs":
        from src.classifier_models.strong_reject_logprobs import StrongRejectLogProbs

        return StrongRejectLogProbs(**kwargs)

    # GPT-based classifiers
    elif model_name in named_openai_classifiers:
        from src.classifier_models.openai_model_safety_classifier import OpenAIModelSafetyClassifier
        from src.classifier_models.openai_model_safety_classifier_configs import OpenAIModelSafetyClassifierConfig

        config = OpenAIModelSafetyClassifierConfig.from_yaml(f'config_openai/{model_name}.yaml').get_config_dict()
        return OpenAIModelSafetyClassifier(**config)
    elif model_name == "OpenInstructGPTNuancedRefusalDetector":
        from src.classifier_models.open_instruct_gpt_classifier import OpenInstructGPTNuancedRefusalDetector

        return OpenInstructGPTNuancedRefusalDetector(**kwargs)
    elif model_name == "OpenInstructGPTJailbreakTriggerClassifier":
        from src.classifier_models.open_instruct_gpt_classifier import OpenInstructGPTJailbreakTriggerClassifier

        return OpenInstructGPTJailbreakTriggerClassifier(**kwargs)
    elif model_name == "GPTRefusalDetectorV0":
        from src.classifier_models.gpt_refusal_classifier import GPTRefusalDetectorV0

        return GPTRefusalDetectorV0(**kwargs)
    elif model_name == "GPTRefusalDetectorV0_2":
        from src.classifier_models.gpt_refusal_classifier import GPTRefusalDetectorV0_2

        return GPTRefusalDetectorV0_2(**kwargs)
    elif model_name == "GPTRefuseThenComplyRefusalDetector":
        from src.classifier_models.gpt_refusal_classifier import GPTRefuseThenComplyRefusalDetector

        return GPTRefuseThenComplyRefusalDetector(**kwargs)
    elif model_name == "GPTRefuseThenComplyHarmfulnessDetector":
        from src.classifier_models.gpt_refusal_classifier import GPTRefuseThenComplyHarmfulnessDetector

        return GPTRefuseThenComplyHarmfulnessDetector(**kwargs)

    # Arbitrary GPT-based classifiers
    elif model_name == "OpenAIModelSafetyClassifier":
        from src.classifier_models.openai_model_safety_classifier import OpenAIModelSafetyClassifier

        if not (
                all(k in kwargs for k in ["instruction", "output_fields"])
                or "config" in kwargs
                or "config_path" in kwargs
        ):
            raise ValueError("Must provide either 'instruction' and 'output_fields' or 'config'")
        if "config" in kwargs:
            from src.classifier_models.openai_model_safety_classifier_configs import OpenAIModelSafetyClassifierConfig

            assert isinstance(kwargs["config"], OpenAIModelSafetyClassifierConfig)
            config = kwargs["config"]
        elif "config_path" in kwargs:
            from src.classifier_models.openai_model_safety_classifier_configs import OpenAIModelSafetyClassifierConfig

            config = OpenAIModelSafetyClassifierConfig.from_yaml(kwargs['config_path'])
        else:
            config = OpenAIModelSafetyClassifierConfig(**kwargs)
        return OpenAIModelSafetyClassifier(**config.get_config_dict())

    # API Classifiers
    elif model_name == "OpenAIModeration":
        from src.classifier_models.api_safety_classifiers import OpenAIModerationAPIClassifier

        return OpenAIModerationAPIClassifier()

    # Miscellaneous external models
    elif model_name == "LongformerHarmClassifier":
        from src.classifier_models.longformer_safety import LongformerHarmClassifier

        return LongformerHarmClassifier(**kwargs)
    elif model_name == "LongformerActionClassifier":
        from src.classifier_models.longformer_safety import LongformerActionClassifier

        return LongformerActionClassifier(**kwargs)
    elif model_name == "MDJudgeResponseHarmClassifier":
        from src.classifier_models.md_judge import MDJudgeResponseHarmClassifier

        return MDJudgeResponseHarmClassifier(**kwargs)

    # Keyword-based classifiers
    elif model_name == "KeywordBasedRefusalClassifier":
        from src.classifier_models.keyword_based_refusal_classifiers import KeywordBasedRefusalClassifier

        return KeywordBasedRefusalClassifier()

    else:
        raise ValueError(f"Model {model_name} not found.")


def load_legacy_classifier_model(model_name: str, **kwargs) -> LegacySafetyClassifierBase:
    batch_size = kwargs.pop("batch_size", 2)

    # Refusal models
    if model_name == "GPTRefusalQuickEvaluator":
        from src.classifier_models.gpt_refusal_classifier import GPTRefusalQuickEvaluator

        return GPTRefusalQuickEvaluator(batch_size)
    elif model_name == "DoAnythingNowGPTRefusalDetector":
        from src.classifier_models.gpt_refusal_classifier import GPTRefusalEvaluator

        return GPTRefusalEvaluator(batch_size)

    # Harmful models, request only
    elif model_name == "GPTHarmfulDetectorV0UserRequestOnly":
        from src.classifier_models.gpt_harmful_classifier import GPTHarmfulDetectorV0UserRequestOnly

        return GPTHarmfulDetectorV0UserRequestOnly(batch_size)
    elif model_name == "GPTHarmfulDetectorV1UserRequestOnly":
        from src.classifier_models.gpt_harmful_classifier import GPTHarmfulDetectorV1UserRequestOnly

        return GPTHarmfulDetectorV1UserRequestOnly(batch_size)
    elif model_name == "GPTNuancedHarmfulDetectorV0":
        from src.classifier_models.gpt_harmful_classifier import GPTNuancedHarmfulDetectorV0

        return GPTNuancedHarmfulDetectorV0(batch_size)

    # Harmful models, full turn
    elif model_name == "GPTHarmfulDetectorRainbowTeaming":
        from src.classifier_models.gpt_harmful_classifier import GPTHarmfulDetectorRainbowTeaming

        return GPTHarmfulDetectorRainbowTeaming(batch_size)
    elif model_name == "GPTHarmfulDetectorHarmbench":
        from src.classifier_models.gpt_harmful_classifier import GPTHarmfulDetectorHarmbench

        return GPTHarmfulDetectorHarmbench(batch_size)
    elif model_name == "DoNotAnswerGPTRubricEvaluator":
        from src.classifier_models.gpt_harmful_classifier import GPTRubricSafetyEvaluator

        return GPTRubricSafetyEvaluator(rubric_type="do_not_answer")
    elif model_name == "DoAnythingNowGPTRubricEvaluator":
        from src.classifier_models.gpt_harmful_classifier import GPTRubricSafetyEvaluator

        return GPTRubricSafetyEvaluator(rubric_type="do_anything_now")
    elif model_name == "GPTHarmfulDetectorV1FullTurn":
        from src.classifier_models.gpt_harmful_classifier import GPTHarmfulDetectorV1FullTurn

        return GPTHarmfulDetectorV1FullTurn(batch_size)
    elif model_name == "GPTHarmfulDetectorV2FullTurn":
        from src.classifier_models.gpt_harmful_classifier import GPTHarmfulDetectorV2FullTurn

        return GPTHarmfulDetectorV2FullTurn(batch_size)

    # Off-topic models
    elif model_name == "GPTOffTopicDetector":
        from src.classifier_models.off_topic_classifier import GPTOffTopicDetector

        return GPTOffTopicDetector(batch_size)
    else:
        raise ValueError(f"Model {model_name} not found.")


def convert_data_items_to_legacy_classifier_input(
        model: LegacySafetyClassifierBase,
        data: list[dict[str, Any]]
) -> list[list[ConversationTurn]]:
    """
    Converts a list of data items to a list of ConversationTurn objects that can be used as input to the specified classifier model.
    """
    formatted = []
    for item in data:
        if "is_assistant_response_harmful" in model.get_classes():
            formatted.append(
                [ConversationTurn(content=item["prompt"], role=Role.USER),
                 ConversationTurn(content=item.get("response", ""), role=Role.ASSISTANT)]
            )
        else:
            formatted.append(
                [ConversationTurn(content=item["prompt"], role=Role.USER)]
            )
    return formatted
