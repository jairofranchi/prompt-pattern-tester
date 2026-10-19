# prompt-pattern-tester

Prompt-engineering playground: reusable prompt patterns, a test harness that scores model responses against criteria, and a small app that calls the OpenAI API.

## Requirements

- Python 3.12+
- OpenAI and Anthropic API keys
- Dependencies in `requirements.txt`: `anthropic`, `openai`, `python-dotenv`, `rich`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set OPENAI_API_KEY and ANTHROPIC_API_KEY in .env
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

Sends every prompt pattern to `gpt-4o-mini` (OpenAI) and `claude-haiku-5-5` (Anthropic). For each response it measures length, format compliance, keyword coverage and latency, then prints per-test scores and a final model ranking. The raw responses are saved to `results/run-<timestamp>.json`.

The suite makes real API calls, so `.env` needs both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`. A full run costs a few cents. Set `RUNS=3` to repeat each test and average the latency. If one provider fails, its errors are recorded and the other provider still runs.

Findings are written up in [RESULTS.md](RESULTS.md).

## Project layout

| File | Purpose |
| --- | --- |
| `main.py` | App entry point (OpenAI or Anthropic call, picked with `MODEL`) |
| `prompt_patterns.py` | Prompt templates (persona, few-shot, ...) and builders |
| `testing_harness.py` | Request formatting and real OpenAI / Anthropic calls |
| `prompt_comparison.py` | Response scoring and model ranking |
| `test_suite.py` | Test cases and runner |
