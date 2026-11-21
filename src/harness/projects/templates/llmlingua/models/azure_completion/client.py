# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

import os
from time import sleep

import tiktoken


def query_llm(
    prompt,
    model,
    model_name,
    max_tokens,
    tokenizer=None,
    chat_completion=False,
    **kwargs,
):
    SLEEP_TIME_FAILED = 62

    request = {
        "temperature": kwargs["temperature"] if "temperature" in kwargs else 0.0,
        "top_p": kwargs["top_p"] if "top_p" in kwargs else 1.0,
        "seed": kwargs["seed"] if "seed" in kwargs else 42,
        "max_tokens": max_tokens,
        "n": 1,
        "stream": False,
    }
    if chat_completion:
        request["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    else:
        request["prompt"] = prompt

    answer = None
    response = None
    while answer is None:
        try:
            response = model.create(engine=model_name, **request)
            answer = (
                response["choices"][0]["message"]["content"]
                if chat_completion
                else response["choices"][0]["text"]
            )
        except Exception as e:
            answer = None
            print(f"error: {e}, response: {response}")
            sleep(SLEEP_TIME_FAILED)
    # sleep(SLEEP_TIME_SUCCESS)
    return answer


def load_model_and_tokenizer(model_name_or_path, chat_completion=False):
    api_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    api_base = os.environ.get("AZURE_OPENAI_ENDPOINT") or os.environ.get(
        "OPENAI_API_BASE"
    )
    if not api_key or not api_base:
        raise ValueError(
            "Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT for this recipe."
        )

    import openai

    openai.api_key = api_key
    openai.api_base = api_base
    openai.api_type = "azure"
    openai.api_version = os.environ.get("OPENAI_API_VERSION", "2023-05-15")

    if chat_completion:
        model = openai.ChatCompletion
    else:
        model = openai.Completion

    tokenizer = tiktoken.encoding_for_model("gpt-4")
    return model, tokenizer
