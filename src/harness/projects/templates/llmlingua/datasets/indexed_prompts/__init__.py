"""Read indexed prompt samples used by the LLMLingua-2 reproduction."""

import json


def read_prompt_samples(path, text_key):
    rows = read_prompt_json(path)
    if not isinstance(rows, list):
        raise ValueError("Prompt input must be a JSON array of samples.")

    samples = {}
    seen_ids = set()
    for row in rows:
        if not isinstance(row, dict) or "idx" not in row or text_key not in row:
            raise ValueError(f"Each sample requires 'idx' and {text_key!r} fields.")
        try:
            index = str(int(row["idx"]))
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Invalid sample index {row['idx']!r}.") from exc
        if index in seen_ids:
            raise ValueError(f"Duplicate sample index {index}.")
        seen_ids.add(index)
        prompt = row[text_key]
        if prompt is None:
            continue
        if not isinstance(prompt, str) and not (
            isinstance(prompt, list) and all(isinstance(item, str) for item in prompt)
        ):
            raise ValueError(f"Sample {index} requires text or a list of strings.")
        samples[index] = row
    return samples


def read_prompt_json(path):
    """Read a UTF-8 JSON collection used by prompt workflows."""
    with open(path, encoding="utf-8") as source:
        return json.load(source)


def evaluation_rows(value):
    """Retain the order of an array or a sample-indexed result object."""
    return value.values() if isinstance(value, dict) else value
