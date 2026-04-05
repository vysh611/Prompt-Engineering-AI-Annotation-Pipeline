"""
evaluate_prompts.py
===================
Compare and score prompt outputs across different techniques.

Metrics evaluated:
  - Accuracy       : Does the output match the expected label?
  - Relevance      : Is the response on-topic? (keyword check)
  - Conciseness    : Is the response within a reasonable length?
  - Format Match   : Does the response follow the expected output format?
  - Overall Score  : Weighted average of the above

Usage:
    python scripts/evaluate_prompts.py
    python scripts/evaluate_prompts.py --input results/prompt_test_outputs.json
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime


# ─────────────────────────────────────────────
# SCORING FUNCTIONS
# ─────────────────────────────────────────────

VALID_SENTIMENT_LABELS  = {"positive", "negative", "neutral"}
VALID_INTENT_LABELS     = {"complaint", "inquiry", "feedback", "request", "greeting"}
VALID_TOPIC_LABELS      = {"technology", "finance", "health", "sports", "entertainment"}
VALID_VERDICT_LABELS    = {"true", "false", "uncertain"}
VALID_MODERATION_LABELS = {"flag", "allow"}


def score_format(response: str, expected_format: str) -> float:
    """Check if the response loosely matches the expected output format."""
    response_lower = response.lower().strip()
    if "|" in expected_format:
        valid_options = [o.strip().lower() for o in expected_format.split("|")]
        if any(opt in response_lower for opt in valid_options):
            return 1.0
        return 0.0
    if expected_format.lower() in response_lower:
        return 1.0
    if len(response_lower) < 300:
        return 0.5
    return 0.2


def score_relevance(response: str, task: str) -> float:
    """Check if response contains task-relevant keywords."""
    response_lower = response.lower()
    task_keywords = {
        "sentiment_classification":   VALID_SENTIMENT_LABELS,
        "sentiment_with_reasoning":   VALID_SENTIMENT_LABELS | {"because", "tone", "positive", "negative"},
        "intent_detection":           VALID_INTENT_LABELS,
        "text_summarization":         {"summary", "main point", "key", "describes", "explains"},
        "topic_classification":       VALID_TOPIC_LABELS,
        "named_entity_recognition":   {"person", "organization", "location"},
        "question_answering":         {"answer", "based on", "according to"},
        "multi_step_reasoning":       {"step", "therefore", "result", "answer"},
        "fact_verification":          VALID_VERDICT_LABELS | {"because", "however", "claim"},
        "root_cause_analysis":        {"cause", "resolution", "issue", "fix", "recommend"},
        "content_moderation":         VALID_MODERATION_LABELS | {"reason", "because"},
        "language_detection":         {"english", "hindi", "french", "spanish", "german"},
        "text_classification_multilabel": {"spam", "urgent", "promotional", "informational", "personal"},
    }
    keywords = task_keywords.get(task, set())
    if not keywords:
        return 0.5
    hits = sum(1 for kw in keywords if kw in response_lower)
    return min(hits / max(len(keywords) * 0.3, 1), 1.0)


def score_conciseness(response: str, task: str) -> float:
    """Penalise extremely long or extremely short responses."""
    length = len(response.split())
    cot_tasks = {"multi_step_reasoning", "fact_verification", "root_cause_analysis",
                 "sentiment_with_reasoning", "content_moderation"}
    if task in cot_tasks:
        # CoT responses should be detailed
        if 20 <= length <= 300:
            return 1.0
        if length < 10:
            return 0.2
        return 0.7
    else:
        # Direct tasks should be concise
        if 1 <= length <= 20:
            return 1.0
        if length <= 50:
            return 0.7
        return 0.4


def compute_overall_score(format_score, relevance_score, conciseness_score) -> float:
    return round(
        0.40 * format_score +
        0.35 * relevance_score +
        0.25 * conciseness_score,
        3
    )


# ─────────────────────────────────────────────
# EVALUATE
# ─────────────────────────────────────────────

def evaluate(results: list) -> list:
    evaluated = []
    for item in results:
        response        = item.get("response", "")
        task            = item.get("task", "")
        expected_format = item.get("expected_format", "")

        fmt_score  = score_format(response, expected_format)
        rel_score  = score_relevance(response, task)
        con_score  = score_conciseness(response, task)
        overall    = compute_overall_score(fmt_score, rel_score, con_score)

        evaluated.append({
            **item,
            "format_score":      fmt_score,
            "relevance_score":   rel_score,
            "conciseness_score": con_score,
            "overall_score":     overall,
            "grade": "Excellent" if overall >= 0.85 else
                     "Good"      if overall >= 0.70 else
                     "Fair"      if overall >= 0.55 else "Needs Improvement",
        })
    return evaluated


# ─────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────

def print_summary(evaluated: list):
    print("\n" + "="*65)
    print("  PROMPT EVALUATION SUMMARY")
    print("="*65)

    by_technique = {}
    for item in evaluated:
        tech = item.get("technique", "unknown")
        by_technique.setdefault(tech, []).append(item["overall_score"])

    for tech, scores in by_technique.items():
        avg = round(sum(scores) / len(scores), 3)
        print(f"  {tech:<22} | Avg Score: {avg:.3f} | Prompts tested: {len(scores)}")

    print("-"*65)
    all_scores = [i["overall_score"] for i in evaluated]
    print(f"  OVERALL AVERAGE          | {sum(all_scores)/len(all_scores):.3f}")
    print("="*65)

    print("\nTop performing prompts:")
    sorted_items = sorted(evaluated, key=lambda x: x["overall_score"], reverse=True)
    for item in sorted_items[:5]:
        print(f"  [{item['prompt_id']}] {item['task']:<35} Score: {item['overall_score']}")


# ─────────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────────

def save_csv(evaluated: list, output_path: str):
    Path(output_path).parent.mkdir(exist_ok=True)
    fields = ["prompt_id", "task", "technique", "format_score",
              "relevance_score", "conciseness_score", "overall_score", "grade", "input", "response"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(evaluated)
    print(f"\n✅ Evaluation results saved to: {output_path}")


# ─────────────────────────────────────────────
# MOCK DATA (if no input file)
# ─────────────────────────────────────────────

MOCK_RESULTS = [
    {"prompt_id": "ZS-001", "task": "sentiment_classification", "technique": "zero-shot",
     "input": "Love this product!", "response": "Positive", "expected_format": "Positive | Negative | Neutral"},
    {"prompt_id": "FS-001", "task": "sentiment_classification", "technique": "few-shot",
     "input": "Broken on arrival.", "response": "Negative", "expected_format": "Positive | Negative | Neutral"},
    {"prompt_id": "COT-002", "task": "sentiment_with_reasoning", "technique": "chain-of-thought",
     "input": "Okay product but expensive.", "response": "1. Positive: okay\n2. Negative: expensive\n3. Neutral tone\nSentiment: Neutral", "expected_format": "Positive | Negative | Neutral"},
    {"prompt_id": "ZS-002", "task": "intent_detection", "technique": "zero-shot",
     "input": "Cancel my order please.", "response": "Request", "expected_format": "Single intent label"},
    {"prompt_id": "COT-001", "task": "multi_step_reasoning", "technique": "chain-of-thought",
     "input": "120km in 2h then 180km in 3h, average speed?", "response": "Step 1: Total distance = 300km\nStep 2: Total time = 5h\nStep 3: Average speed = 60 km/h\nAnswer: 60 km/h", "expected_format": "Step-by-step reasoning followed by final answer"},
]


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Evaluate prompt outputs.")
    parser.add_argument("--input", type=str, default=None,
                        help="Path to prompt_test_outputs.json (default: use mock data)")
    args = parser.parse_args()

    if args.input and Path(args.input).exists():
        with open(args.input) as f:
            results = json.load(f)
        print(f"Loaded {len(results)} results from {args.input}")
    else:
        print("No input file found. Running evaluation on mock data...\n")
        results = MOCK_RESULTS

    evaluated = evaluate(results)
    print_summary(evaluated)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_csv(evaluated, f"results/prompt_evaluation_results_{timestamp}.csv")
    # also save a fixed-name version for convenience
    save_csv(evaluated, "results/prompt_evaluation_results.csv")


if __name__ == "__main__":
    main()
