"""
prompt_tester.py
================
Test prompt templates against an LLM API (Anthropic Claude / OpenAI compatible).

Usage:
    python scripts/prompt_tester.py --technique zero-shot --task sentiment_classification
    python scripts/prompt_tester.py --technique few-shot --task intent_detection
    python scripts/prompt_tester.py --technique chain-of-thought --task multi_step_reasoning
    python scripts/prompt_tester.py --all   # Run all prompts on sample inputs
"""

import json
import argparse
import os
import time
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")
MODEL   = "claude-3-haiku-20240307"   # lightweight model for testing

PROMPT_FILES = {
    "zero-shot":        "prompts/zero_shot_prompts.json",
    "few-shot":         "prompts/few_shot_prompts.json",
    "chain-of-thought": "prompts/chain_of_thought_prompts.json",
}

SAMPLE_INPUTS = {
    "sentiment_classification": [
        "This product is absolutely fantastic! Works perfectly.",
        "Completely broken on arrival. Terrible quality.",
        "The item arrived two days after the expected date.",
    ],
    "intent_detection": [
        "I want to cancel my subscription immediately.",
        "What are your business hours?",
        "Great support team, very responsive!",
    ],
    "text_summarization": [
        "Artificial intelligence is transforming industries worldwide by automating repetitive tasks, enabling data-driven decisions, and creating new opportunities for innovation in healthcare, finance, and education.",
    ],
    "multi_step_reasoning": [
        "If a train travels 120 km in 2 hours, and then 180 km in 3 hours, what is its average speed for the entire journey?",
    ],
    "fact_verification": [
        "The Great Wall of China is visible from space with the naked eye.",
        "Python was created by Guido van Rossum.",
    ],
}


# ─────────────────────────────────────────────
# LLM CALL (Anthropic)
# ─────────────────────────────────────────────
def call_llm(prompt_text: str) -> str:
    """Send a prompt to the Anthropic Claude API and return the response text."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt_text}],
        )
        return message.content[0].text.strip()
    except ImportError:
        print("[WARNING] anthropic package not installed. Run: pip install anthropic")
        return "[MOCK RESPONSE] LLM not connected — install anthropic package."
    except Exception as e:
        return f"[ERROR] {str(e)}"


# ─────────────────────────────────────────────
# LOAD PROMPTS
# ─────────────────────────────────────────────
def load_prompts(technique: str) -> list:
    filepath = PROMPT_FILES.get(technique)
    if not filepath or not Path(filepath).exists():
        print(f"[ERROR] Prompt file not found for technique: {technique}")
        return []
    with open(filepath, "r") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# RUN SINGLE TECHNIQUE + TASK
# ─────────────────────────────────────────────
def run_test(technique: str, task: str = None):
    prompts = load_prompts(technique)
    results = []

    for prompt_obj in prompts:
        if task and prompt_obj["task"] != task:
            continue

        current_task = prompt_obj["task"]
        sample_texts = SAMPLE_INPUTS.get(current_task, ["Sample input text for testing."])

        print(f"\n{'='*60}")
        print(f"Prompt ID : {prompt_obj['id']}")
        print(f"Task      : {current_task}")
        print(f"Technique : {technique}")
        print(f"{'='*60}")

        for i, sample in enumerate(sample_texts[:2]):  # test max 2 samples per prompt
            # Fill in the template
            filled_prompt = prompt_obj["prompt"].replace("{input_text}", sample)
            if "{context}" in filled_prompt:
                filled_prompt = filled_prompt.replace("{context}", sample)
            if "{question}" in filled_prompt:
                filled_prompt = filled_prompt.replace("{question}", "What is the main point?")

            print(f"\n[Sample {i+1}] Input: {sample[:80]}...")
            response = call_llm(filled_prompt)
            print(f"[Response]: {response}")

            results.append({
                "prompt_id": prompt_obj["id"],
                "task": current_task,
                "technique": technique,
                "input": sample,
                "response": response,
            })

            time.sleep(0.5)  # avoid rate limits

    return results


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Test LLM prompts from JSON templates.")
    parser.add_argument("--technique", choices=list(PROMPT_FILES.keys()), help="Prompting technique to test")
    parser.add_argument("--task", type=str, default=None, help="Specific task to test (optional)")
    parser.add_argument("--all", action="store_true", help="Run all prompt techniques")
    args = parser.parse_args()

    all_results = []

    if args.all:
        for tech in PROMPT_FILES:
            results = run_test(tech)
            all_results.extend(results)
    elif args.technique:
        all_results = run_test(args.technique, args.task)
    else:
        parser.print_help()
        return

    # Save results
    output_path = "results/prompt_test_outputs.json"
    Path("results").mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n\n✅ Results saved to {output_path}")


if __name__ == "__main__":
    main()
