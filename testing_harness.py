import os
import time
from functools import cache

import anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


MODEL_CONFIGS = {
    "gpt-4o-mini": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "max_tokens": 2048,
        "context_window": 128_000,
    },
    "claude-haiku-5-5": {
        "provider": "anthropic",
        "model": "claude-haiku-5-5",
        # Thinking is on by default and counts against max_tokens.
        "max_tokens": 16000,
        "context_window": 1_000_000,
    },
}


def format_openai_request(prompt, config):
    return {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        "temperature": prompt["temperature"],
        "max_tokens": config["max_tokens"],
    }


def format_anthropic_request(prompt, config):
    # Haiku 5.5 rejects non-default temperature, so it isn't sent.
    return {
        "model": config["model"],
        "system": prompt["system"],
        "messages": [
            {"role": "user", "content": prompt["user"]},
        ],
        "max_tokens": config["max_tokens"],
    }


FORMATTERS = {
    "openai": format_openai_request,
    "anthropic": format_anthropic_request,
}


@cache
def openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@cache
def anthropic_client():
    return anthropic.Anthropic()


def call_llm(config, request):
    if config["provider"] == "openai":
        response = openai_client().chat.completions.create(**request)
        return {
            "response": response.choices[0].message.content or "",
            "tokens_used": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }

    if config["provider"] == "anthropic":
        response = anthropic_client().messages.create(**request)
        return {
            "response": "".join(block.text for block in response.content if block.type == "text"),
            "tokens_used": {
                "prompt": response.usage.input_tokens,
                "completion": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
            },
            "finish_reason": response.stop_reason,
        }

    raise ValueError(f"Unsupported provider: {config['provider']}")


def run_prompt_test(prompt, models=None):
    if models is None:
        models = list(MODEL_CONFIGS.keys())

    results = {}
    for model_name in models:
        config = MODEL_CONFIGS[model_name]
        request = FORMATTERS[config["provider"]](prompt, config)

        start = time.time()
        try:
            response = call_llm(config, request)
            error = None
        except Exception as e:
            response = {"response": "", "tokens_used": {}, "finish_reason": None}
            error = f"{type(e).__name__}: {e}"
        wall_time = (time.time() - start) * 1000

        results[model_name] = {
            "response": response["response"],
            "tokens": response["tokens_used"],
            "latency_ms": round(wall_time, 1),
            "finish_reason": response["finish_reason"],
            "error": error,
            "request_payload": request,
        }

    return results
