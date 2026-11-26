"""Load AgentFlow benchmark records from their prepared JSON inputs."""

import json
from pathlib import Path


def load_questions(path, task_description=""):
    """Read a benchmark and normalize question and attachment fields."""
    path = Path(path)
    with path.open(encoding="utf-8") as stream:
        questions = json.load(stream)
    if not isinstance(questions, list) or not questions:
        raise ValueError(f"{path} must contain a nonempty list of benchmark questions")
    for index, problem in enumerate(questions):
        if not isinstance(problem, dict):
            raise ValueError(f"{path} record {index} must be a JSON object")
        query = problem.get("query", problem.get("question"))
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"{path} record {index} must contain a nonempty question")
        problem["query"] = task_description + query
        if problem.get("image"):
            image_path = (path.parent / problem["image"]).resolve()
            if not image_path.is_file():
                raise FileNotFoundError(f"Benchmark attachment does not exist: {image_path}")
            problem["image"] = str(image_path)
    return questions
