"""Multilingual evaluations grouped by language or shared benchmark."""

from lighteval.tasks import _task_family_paths


__path__ = [*__path__, *_task_family_paths(__file__)]
