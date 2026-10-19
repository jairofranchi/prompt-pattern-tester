import os
from functools import cache

import anthropic

from dotenv import load_dotenv
from prompt_patterns import build_prompt
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

MODEL = os.getenv("MODEL", "anthropic/claude-sonnet-5-5")


@cache
def openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@cache
def anthropic_client():
    return anthropic.Anthropic()


def call_model(model_name, prompt):
    if model_name.startswith("anthropic/"):
        # Current Claude models reject temperature, so it isn't sent.
        response = anthropic_client().beta.messages.create(
            model=model_name.removeprefix("anthropic/"),
            max_tokens=prompt.get("max_tokens", 16000),
            system=prompt["system"],
            messages=[{"role": "user", "content": prompt["user"]}],
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(f"Claude refused the request: {response.stop_details}")
        return "".join(block.text for block in response.content if block.type == "text")

    response = openai_client().chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        temperature=prompt.get("temperature", 0.7),
    )
    return response.choices[0].message.content


def main():
    prompt = build_prompt(
        "persona",
        {
            "role": "a senior Python developer",
            "experience": "10 years of algorithms experience",
            "style": "terse and code-only",
            "priority": "correctness and readability",
            "task": "Write a function that finds the longest palindromic substring.",
        },
        system_override="You are a senior Python developer. Respond with code only, no explanations, inside a single ```python fenced code block.",
    )

    response = call_model(MODEL, prompt)

    Console().print(Markdown(response or ""))


if __name__ == "__main__":
    main()
