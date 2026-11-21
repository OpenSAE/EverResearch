"""Built-in evaluations grouped by research purpose."""

from lighteval.tasks import _task_family_paths


__path__ = [*__path__, *_task_family_paths(__file__)]
