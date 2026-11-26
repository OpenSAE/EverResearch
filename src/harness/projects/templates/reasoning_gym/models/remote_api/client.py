"""Construct the OpenAI-compatible client used by remote evaluation.

The remote evaluator supplies the endpoint, optional credentials, and timeout.
"""

from openai import AsyncOpenAI


def create_client(base_url: str, api_key: str | None, timeout: int) -> AsyncOpenAI:
    # Some compatible local providers need no credentials, but the SDK always
    # expects a value for the authorization header.
    return AsyncOpenAI(base_url=base_url, api_key=api_key or "unused", timeout=timeout)
