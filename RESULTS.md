# Exercise 2: OpenAI vs Anthropic

The same 10 prompts from `test_suite.py` were sent to both providers through `testing_harness.call_llm`. Each test ran 3 times (`RUNS=3`).

- **Models:** `gpt-4o-mini` (OpenAI) and `claude-haiku-5-5` (Anthropic)
- **Date:** 2026-10-19
- **Raw data:** `results/run-20261019-145249.json` (3 runs) and `results/run-20261019-144823.json` (an earlier single run)

## Setup caveats

- **Temperature:** OpenAI gets each pattern's temperature (0.0–0.7). Claude Haiku 5.5 rejects a non-default temperature, so it runs at its default.
- **Thinking:** Claude Haiku 5.5 thinks before answering and gpt-4o-mini doesn't. Claude's thinking tokens are included in its completion tokens and its latency.
- **Length limits:** `max_words` comes from the test criteria. Only the Audience test (and the Boundary test's exact refusal sentence) actually puts a limit in the prompt. The Persona (200 words) and Meta-Prompt (400 words) limits are never shown to the model, so those checks measure verbosity rather than instruction following.
- **Scoring:** the checks are keyword and format heuristics from `prompt_comparison.score_response`. They don't judge whether an answer is correct.

## Results (mean of 3 runs)

| Test | Model | Score | Words | Keywords | Format | Length | Latency |
|---|---|---|---|---|---|---|---|
| Persona: Technical Writer | gpt-4o-mini | **1.000** | 182 | 1.00 | – | 3/3 ≤200 | 2.6 s |
| | claude-haiku-5-5 | 0.778 | 240 | 1.00 | – | 1/3 ≤200 | 3.5 s |
| Few-Shot: Sentiment (JSON) | gpt-4o-mini | 1.000 | 6 | 1.00 | valid JSON | – | 0.7 s |
| | claude-haiku-5-5 | 1.000 | 6 | 1.00 | valid JSON | – | 1.7 s |
| Chain-of-Thought: Math | gpt-4o-mini | 1.000 | 276 | 1.00 | – | ≤300 | 6.4 s |
| | claude-haiku-5-5 | 1.000 | 226 | 1.00 | – | ≤300 | 3.7 s |
| Template Fill: Resume | gpt-4o-mini | 1.000 | 18 | 1.00 | – | – | 0.9 s |
| | claude-haiku-5-5 | 1.000 | 21 | 1.00 | – | – | 0.9 s |
| Guardrail: Python Tutor | gpt-4o-mini | **1.000** | 86 | 1.00 | – | – | 1.6 s |
| | claude-haiku-5-5 | 0.944 | 214 | 0.89 | – | – | 2.7 s |
| Meta-Prompt: Ticket Classifier | gpt-4o-mini | **1.000** | 277 | 1.00 | – | 3/3 ≤400 | 4.8 s |
| | claude-haiku-5-5 | 0.667 | 963 | 1.00 | – | 0/3 ≤400 | 16.5 s |
| Decomposition: Event (numbered) | gpt-4o-mini | 1.000 | 366 | 1.00 | numbered | – | 7.1 s |
| | claude-haiku-5-5 | 1.000 | 784 | 1.00 | numbered | – | 17.8 s |
| Critique: Decorator | gpt-4o-mini | 1.000 | 225 | 1.00 | – | – | 3.5 s |
| | claude-haiku-5-5 | 1.000 | 258 | 1.00 | – | – | 3.2 s |
| Audience: Blockchain for kids | gpt-4o-mini | 1.000 | 81 | 1.00 | – | <100 | 1.5 s |
| | claude-haiku-5-5 | 1.000 | 87 | 1.00 | – | <100 | 2.7 s |
| Boundary: Cooking (refusal) | gpt-4o-mini | 1.000 | 7 | 1.00 | – | ≤20 | 0.7 s |
| | claude-haiku-5-5 | 1.000 | 7 | 1.00 | – | ≤20 | 0.7 s |

### Totals

| Model | Avg score | Wins | Ties | Avg words | Avg latency | Errors |
|---|---|---|---|---|---|---|
| gpt-4o-mini | **1.000** | 3 | 7 | 152 | 3.0 s | 0 |
| claude-haiku-5-5 | 0.939 | 0 | 7 | 281 | 5.3 s | 0 |

## Which model follows instructions more precisely?

**gpt-4o-mini scored higher on this suite, but on the instructions the prompts actually state, the two models are essentially tied.**

- **Explicit instructions: tie.**
  - Both produced bare, parseable JSON in the few-shot test, a numbered decomposition, the exact refusal sentence in 7 words, a kids' explanation under 100 words, and every required keyword.
  - The one exception: in the earlier single run, Claude's few-shot answer failed to parse as JSON. It passed in all 3 later runs.
- **Where gpt-4o-mini won:**
  - All three wins come from **length**. Claude Haiku 5.5 wrote about 1.8x as many words on average. It ran past the 200-word Persona budget in 2 of 3 runs and past the 400-word Meta-Prompt budget in every run (881–1019 words).
  - Neither budget appears in the prompt, so this shows that gpt-4o-mini defaults to shorter answers. It doesn't show that Claude ignored an instruction.
  - The single Guardrail miss was Claude suggesting `operator.itemgetter` instead of a `lambda`. That's a valid answer which the keyword check doesn't recognize.
- **Following the examples:**
  - In the few-shot test, gpt-4o-mini labelled "great pasta … though a bit pricey" as `"mixed"`, matching the style of the first example.
  - Claude Haiku 5.5 said `"positive"` in all 3 runs, dropping the price caveat.
  - The scorer doesn't check this, but it's a point for gpt-4o-mini on following the examples' intent.
- **Latency:**
  - gpt-4o-mini was faster on average (3.0 s vs 5.3 s). The gap comes almost entirely from Claude's long answers plus its thinking tokens: up to ~4,000 completion tokens on Decomposition, vs ~650 for gpt-4o-mini.
  - On short tasks the two are close (Boundary 0.7 s each, Template Fill 0.9 s each), and Claude was faster on the math problem (3.7 s vs 6.4 s).

**Conclusion:** for prompts with tight output constraints, gpt-4o-mini is the safer default here because it stays concise without being told to. Claude Haiku 5.5 complies just as well with explicit constraints but needs the length limit written into the prompt.

To make the comparison fairer, put the `max_words` budgets into the Persona and Meta-Prompt templates, or lower Claude's effort (`output_config={"effort": "low"}`), and rerun.
