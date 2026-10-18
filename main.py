import os

from dotenv import load_dotenv
from prompt_patterns import build_prompt
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.console import Console

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def main():
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": "You are a senior Python developer. Respond with code only, no explanations, inside a single ```python fenced code block.",
            },
            {
                "role": "user",
                "content": "Write a function that finds the longest palindromic substring.",
            },
        ],
    )

    Console().print(Markdown(response.choices[0].message.content or ""))


if __name__ == "__main__":
    main()
