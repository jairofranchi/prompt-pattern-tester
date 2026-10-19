import json
import os
from datetime import datetime

from prompt_comparison import compare_models
from prompt_patterns import build_prompt
from testing_harness import MODEL_CONFIGS, run_prompt_test

TEST_SUITE = [
    {
        "name": "Persona: Technical Writer",
        "pattern": "persona",
        "variables": {
            "role": "a senior technical writer at Stripe",
            "experience": "10 years of API documentation experience",
            "style": "precise, concise, and example-driven",
            "priority": "clarity over comprehensiveness",
            "task": "Explain what an API rate limit is and why it exists.",
        },
        "criteria": {
            "max_words": 200,
            "required_keywords": ["rate limit", "API", "requests"],
            "forbidden_phrases": ["in conclusion", "it is important to note"],
        },
    },
    {
        "name": "Few-Shot: Sentiment Analysis",
        "pattern": "few_shot",
        "variables": {
            "examples": (
                'Input: "The food was amazing but service was slow"\n'
                'Output: {"sentiment": "mixed", "food": "positive", "service": "negative"}\n\n'
                'Input: "Terrible experience, never coming back"\n'
                'Output: {"sentiment": "negative", "food": null, "service": "negative"}'
            ),
            "input": "Great ambiance and the pasta was perfect, though a bit pricey",
        },
        "criteria": {
            "expected_format": "json",
            "required_keywords": ["sentiment"],
        },
    },
    {
        "name": "Chain-of-Thought: Math Problem",
        "pattern": "chain_of_thought",
        "variables": {
            "problem": "A store offers 20% off all items. An item originally costs $85. There is also a $10 coupon. Which saves more: applying the discount first then the coupon, or the coupon first then the discount?",
        },
        "criteria": {
            "required_keywords": ["discount", "coupon", "$"],
            "max_words": 300,
        },
    },
    {
        "name": "Template Fill: Resume Extraction",
        "pattern": "template_fill",
        "variables": {
            "text": "John Smith is a software engineer at Google with 5 years of experience. He graduated from MIT with a BS in Computer Science in 2019. He specializes in distributed systems and Go programming.",
            "template_structure": "Name: [full name]\nCompany: [current employer]\nYears of Experience: [number]\nEducation: [degree, school, year]\nSpecialties: [comma-separated list]",
        },
        "criteria": {
            "required_keywords": ["John Smith", "Google", "MIT"],
        },
    },
    {
        "name": "Guardrail: Scoped Assistant",
        "pattern": "guardrail",
        "variables": {
            "role": "Python programming tutor",
            "domain": "Python programming",
            "additional_rules": "Do not write complete solutions. Guide the student with hints.",
            "question": "How do I sort a list of dictionaries by a specific key?",
        },
        "criteria": {
            "required_keywords": ["sorted", "key", "lambda"],
            "forbidden_phrases": ["here is the complete solution"],
        },
    },
    {
        "name": "Meta-Prompt: Support Ticket Classifier",
        "pattern": "meta_prompt",
        "variables": {
            "objective": "classify customer support tickets into billing, technical, or account categories",
            "metric": "classification accuracy",
            "model": "gpt-4o",
        },
        "criteria": {
            "max_words": 400,
            "required_keywords": ["billing", "technical", "account", "example"],
            "forbidden_phrases": ["as an ai language model"],
        },
    },
    {
        "name": "Decomposition: Event Planning",
        "pattern": "decomposition",
        "variables": {
            "problem": "Plan a 3-day conference for 200 attendees with a $50,000 budget, including venue, catering, speakers, and registration.",
        },
        "criteria": {
            "expected_format": "numbered_list",
            "required_keywords": ["sub-problem", "venue", "catering", "budget"],
        },
    },
    {
        "name": "Critique: Code Explanation",
        "pattern": "critique",
        "variables": {
            "task": "Explain what a Python decorator is in two or three sentences.",
        },
        "criteria": {
            "required_keywords": ["Step 1", "Step 2", "Step 3", "decorator"],
            "forbidden_phrases": ["i cannot"],
        },
    },
    {
        "name": "Audience Adaptation: Blockchain for Kids",
        "pattern": "audience_adapt",
        "variables": {
            "concept": "how a blockchain works",
            "audience": "10-year-old children",
            "length": "under 100 words",
            "include": "a simple everyday analogy",
            "exclude": "technical jargon like hashing or consensus",
        },
        "criteria": {
            "max_words": 100,
            "required_keywords": ["blockchain"],
            "forbidden_phrases": ["hashing", "consensus"],
        },
    },
    {
        "name": "Boundary: Cooking Assistant",
        "pattern": "boundary",
        "variables": {
            "scope": "cooking and recipe questions",
            "refusal_message": "I can only help with cooking questions.",
            "user_input": "Can you help me file my taxes?",
        },
        "criteria": {
            "max_words": 20,
            "required_keywords": ["I can only help with cooking questions."],
            "forbidden_phrases": ["deduction", "tax return"],
        },
    },
]


RUNS = int(os.getenv("RUNS", "1"))


def summarize_runs(runs):
    """Average score, words, and latency over the runs of one model on one test."""
    ok = [r for r in runs if not r["error"]]
    if not ok:
        return {"error": runs[-1]["error"]}
    last = ok[-1]["scores"]
    return {
        "composite_score": round(sum(r["scores"]["composite_score"] for r in ok) / len(ok), 3),
        "word_count": round(sum(r["scores"]["word_count"] for r in ok) / len(ok)),
        "keyword_coverage": last.get("keyword_coverage"),
        "format_valid": last.get("format_valid"),
        "length_compliant": last.get("length_compliant"),
        "latency_ms": round(sum(r["latency_ms"] for r in ok) / len(ok), 1),
        "error": None,
    }


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def run_test_suite():
    print("=" * 70)
    print(f"  PROMPT ENGINEERING TEST SUITE ({RUNS} run(s) per test)")
    print("=" * 70)

    all_results = []

    for test in TEST_SUITE:
        print(f"\n{'=' * 60}")
        print(f"  Test: {test['name']}")
        print(f"  Pattern: {test['pattern']}")
        print(f"{'=' * 60}")

        prompt = build_prompt(test["pattern"], test["variables"])
        print(f"\n  System: {prompt['system'][:80]}...")
        print(f"  User prompt: {prompt['user'][:120]}...")
        print(f"  Temperature: {prompt['temperature']}")

        runs_by_model = {}
        for _ in range(RUNS):
            comparison, _ranked = compare_models(run_prompt_test(prompt), test["criteria"])
            for model_name, data in comparison.items():
                runs_by_model.setdefault(model_name, []).append(data)

        summaries = {name: summarize_runs(runs) for name, runs in runs_by_model.items()}
        ranked = sorted(
            summaries.items(),
            key=lambda x: x[1].get("composite_score", -1),
            reverse=True,
        )

        print(f"\n  {'Model':<20} {'Score':>6} {'Words':>6} {'Keywords':>9} {'Format':>7} {'Length':>7} {'Latency':>10}")
        print(f"  {'-' * 70}")
        for model_name, s in ranked:
            if s["error"]:
                print(f"  {model_name:<20} ERROR: {s['error'][:60]}")
                continue
            print(
                f"  {model_name:<20} {s['composite_score']:>6.3f} {s['word_count']:>6} "
                f"{fmt(s['keyword_coverage']):>9} {fmt(s['format_valid']):>7} "
                f"{fmt(s['length_compliant']):>7} {s['latency_ms']:>8}ms"
            )

        all_results.append({
            "test": test["name"],
            "pattern": test["pattern"],
            "criteria": test["criteria"],
            "summaries": summaries,
            "runs": runs_by_model,
            "rankings": [(name, s.get("composite_score")) for name, s in ranked if not s["error"]],
        })

    print(f"\n\n{'=' * 70}")
    print("  SUMMARY: MODEL RANKINGS ACROSS ALL TESTS")
    print(f"{'=' * 70}")

    model_wins = {}
    for result in all_results:
        scores = [score for _, score in result["rankings"]]
        # A tie gives no win to either model.
        if scores and scores.count(scores[0]) == 1:
            winner = result["rankings"][0][0]
            model_wins[winner] = model_wins.get(winner, 0) + 1

    print(f"\n  {'Model':<20} {'Avg score':>10} {'Wins':>5} {'Avg words':>10} {'Avg latency':>12} {'Errors':>7}")
    print(f"  {'-' * 70}")
    for model_name in MODEL_CONFIGS:
        ok = [r["summaries"][model_name] for r in all_results if not r["summaries"].get(model_name, {}).get("error", True)]
        errors = len(all_results) - len(ok)
        if not ok:
            print(f"  {model_name:<20} no successful calls ({errors} errors)")
            continue
        avg_score = sum(s["composite_score"] for s in ok) / len(ok)
        avg_words = sum(s["word_count"] for s in ok) / len(ok)
        avg_latency = sum(s["latency_ms"] for s in ok) / len(ok)
        print(
            f"  {model_name:<20} {avg_score:>10.3f} {model_wins.get(model_name, 0):>5} "
            f"{avg_words:>10.0f} {avg_latency:>10.0f}ms {errors:>7}"
        )

    os.makedirs("results", exist_ok=True)
    path = os.path.join("results", f"run-{datetime.now():%Y%m%d-%H%M%S}.json")
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  Raw results saved to {path}")

    return all_results

if __name__ == "__main__":
    run_test_suite()
