"""Define evaluation task interfaces and expose historical generator imports."""

from __future__ import annotations

import abc
from collections import Counter
from typing import TYPE_CHECKING

from src.classifier_models.base import SafetyClassifierBase

if TYPE_CHECKING:
    from evaluation.models.generator_models import GeneratorModelBase


def __getattr__(name):
    if name not in {"GeneratorModelBase", "HfGeneratorModel", "VllmGeneratorModel", "APIGeneratorModel"}:
        raise AttributeError(name)

    from evaluation.models import generator_models

    return getattr(generator_models, name)


class TaskBase(abc.ABC):
    def __init__(self, **kwargs):
        """
        Initialize the task for evaluation.
        """
        self.data = self.put_id_on_data(self.load())
        assert len(self.data) > 0, "No data loaded for the task."
        assert all("id" in d for d in self.data), "All data must have an 'id' field."

    def put_id_on_data(self, data: list[dict]) -> list[dict]:
        """
        Put an 'id' field on the data.

        Args:
            data: List of data.

        Returns:
            List of data with 'id' field.
        """
        return [
            {"id": f"{self.__class__.__name__}/{i}", **d} for i, d in enumerate(data)
        ]

    @abc.abstractmethod
    def required_input_fields(self) -> list[str]:
        """
        Get the required input fields for the task.

        Returns:
            List of required input fields.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load(self) -> list[dict]:
        """
        Load the task data. It will load data to self.data.

        Returns:
            List of task data.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _evaluate(
            self, model: GeneratorModelBase | SafetyClassifierBase
    ) -> tuple[dict, list[dict]]:
        """
        Evaluate the model on the given task.

        Args:
            model: Model to evaluate.

        Returns:
            A dictionary of evaluation results, and a list of individual evaluation results per instance.
        """
        raise NotImplementedError

    def evaluate(
            self, model: GeneratorModelBase | SafetyClassifierBase
    ) -> tuple[dict, list[dict]]:
        report, individual_results = self._evaluate(model)
        if getattr(self, "thinker_eval", None) is not None and len(self.thinker_eval) > 1:
            for v in individual_results:
                assert all(
                "id" in d for d in individual_results[v]
            ), "All individual results must have an 'id' field."
            assert len(set(d["id"] for d in individual_results[v])) == len(
                individual_results[v]
            ), "All individual results must have unique 'id' field."
        else:
            assert all(
                "id" in d for d in individual_results
            ), "All individual results must have an 'id' field."
            assert len(set(d["id"] for d in individual_results)) == len(
                individual_results
            ), "All individual results must have unique 'id' field."
        return report, individual_results


class ClassificationTaskBase(TaskBase, abc.ABC):
    @abc.abstractmethod
    def required_output_fields(self) -> list[list[str]]:
        """
        Get the required output fields for the task.

        Returns:
            List of required output field lists.
            Each list within the return is a valid set of required output fields.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def label_field(self) -> str:
        """
        Get the label field for the task.

        Returns:
            Label field.
        """
        raise NotImplementedError

    def display_data_stats(self):
        print(f"Field: {self.label_field}")
        counter = Counter([d[self.label_field] for d in self.data])
        for k, v in counter.items():
            print(f"{k}: {v}")

    def validate_if_model_is_compatible(self, model: SafetyClassifierBase) -> bool:
        """
        Validate if the model is compatible with the task.

        Args:
            model: Model to validate.

        Returns:
            True if the model is compatible with the task, False otherwise.
        """
        input_compatible = all(
            field in model.get_possible_input_fields()
            for field in self.required_input_fields()
        )
        assert input_compatible, (
            f"Model input fields {model.get_possible_input_fields()} "
            f"are not compatible with the task input fields {self.required_input_fields()}"
        )
        output_compatible = any(
            all(field in model.get_output_fields() for field in fieldset)
            for fieldset in self.required_output_fields()
        )
        assert output_compatible, (
            f"Model output fields {model.get_output_fields()} "
            f"are not compatible with the task output fields {self.required_output_fields()}"
        )
        return input_compatible and output_compatible

    @abc.abstractmethod
    def _evaluate(self, model: SafetyClassifierBase) -> tuple[dict, list[dict]]:
        raise NotImplementedError


class OpenEndedTaskBase(TaskBase, abc.ABC):
    def validate_if_model_is_compatible(self, model: GeneratorModelBase) -> bool:
        """
        Validate if the model is compatible with the task.

        Args:
            model: Model to validate.

        Returns:
            True if the model is compatible with the task, False otherwise.
        """
        input_compatible = all(
            field in model.model_input_template
            for field in self.required_input_fields()
        )
        assert input_compatible, (
            f"Model input fields {model.model_input_template} "
            f"are not compatible with the task input fields {self.required_input_fields()}"
        )
        return input_compatible

    @abc.abstractmethod
    def _evaluate(self, model: GeneratorModelBase) -> tuple[dict, list[dict]]:
        raise NotImplementedError


class JailbreakBase(abc.ABC):
    def __init__(self, task: OpenEndedTaskBase, **kwargs):
        """
        Initialize the jailbreak attack for the given task.
        """
        self.task = task

    @abc.abstractmethod
    def apply_attack(self) -> list[dict]:
        """
        Apply the attack to the task data.

        Returns:
            List of attacked data.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _evaluate(self, model: GeneratorModelBase) -> tuple[dict, list[dict]]:
        """
        Evaluate the model on the given task.
            There are mainly two stages: first, apply attack to the task data. Then, evaluate the model on the attacked data.

        Args:
            model: Model to evaluate.

        Returns:
            A dictionary of evaluation results, and a list of individual evaluation results per instance.
        """
        raise NotImplementedError
