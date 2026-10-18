# prompt-pattern-tester

Prompt-engineering playground: reusable prompt patterns, a test harness that scores model responses against criteria, and a small app that calls the OpenAI API.

## Requirements

- Python 3.12+
- An OpenAI API key (only needed to run the app, not the tests)
- Dependencies in `requirements.txt`: `openai`, `python-dotenv`, `rich`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set OPENAI_API_KEY in .env
```

## Run the app

```bash
python main.py
```

Sends a sample coding prompt to the OpenAI API and prints the rendered response. Requires `OPENAI_API_KEY` in `.env`.

## Run the tests

```bash
python test_suite.py
```

Runs every prompt pattern through the test harness, scores the responses, and prints per-test scores and a final model ranking. LLM calls are simulated, so no API key or network access is needed.

## Project layout

| File | Purpose |
| --- | --- |
| `main.py` | App entry point (OpenAI call) |
| `prompt_patterns.py` | Prompt templates (persona, few-shot, ...) and builders |
| `testing_harness.py` | Request formatting and simulated model calls |
| `prompt_comparison.py` | Response scoring and model ranking |
| `test_suite.py` | Test cases and runner |
