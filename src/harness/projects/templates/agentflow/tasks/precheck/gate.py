"""Check benchmark inputs before execution and optionally probe an engine."""

from agentflow.benchmark_data.questions import load_questions


def check_benchmark(path, index, task_description=""):
    questions = load_questions(path, task_description)
    if index is not None and not 0 <= index < len(questions):
        raise ValueError(f"Benchmark index {index} is outside 0–{len(questions) - 1}")
    return questions


def precheck(path, index, model=None, *, base_url=None, probe_model=False):
    questions = check_benchmark(path, index)
    result = {"dataset": str(path), "count": len(questions), "sample_index": index}
    if model:
        from agentflow.engine.factory import create_llm_engine

        engine = create_llm_engine(model, base_url=base_url)
        result["model"] = model
        result["provider"] = type(engine).__name__
        if probe_model:
            answer = engine.generate(questions[index]["query"], max_tokens=64)
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("The selected model did not return text for the sample")
            result["model_probe"] = "passed"
    return result
