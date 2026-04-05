"""
annotation_validator.py
========================
Validate annotated dataset for consistency, completeness, and quality.

Checks performed:
  1. Missing or empty labels
  2. Invalid label values (not in allowed set)
  3. Low confidence entries (flagged for review)
  4. Label distribution summary
  5. Overall annotation consistency score

Usage:
    python scripts/annotation_validator.py
    python scripts/annotation_validator.py --file annotation/annotated_dataset.csv
    python scripts/annotation_validator.py --file annotation/annotated_dataset.csv --threshold 0.80
"""

import csv
import argparse
from pathlib import Path
from collections import Counter


# ─────────────────────────────────────────────
# VALID LABELS
# ─────────────────────────────────────────────
VALID_SENTIMENTS = {"Positive", "Negative", "Neutral"}
VALID_INTENTS    = {"Complaint", "Inquiry", "Feedback", "Request", "Greeting"}
VALID_TOPICS     = {"Technology", "Finance", "Health", "Sports", "Entertainment"}
VALID_STATUSES   = {"annotated", "unlabeled", "review"}


# ─────────────────────────────────────────────
# LOAD DATASET
# ─────────────────────────────────────────────
def load_csv(filepath: str) -> list:
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


# ─────────────────────────────────────────────
# VALIDATION CHECKS
# ─────────────────────────────────────────────
def validate(rows: list, confidence_threshold: float = 0.75) -> dict:
    errors        = []
    warnings      = []
    flagged_rows  = []

    sentiment_counts = Counter()
    intent_counts    = Counter()
    topic_counts     = Counter()
    confidence_vals  = []
    total_annotated  = 0

    for i, row in enumerate(rows, start=2):  # row 1 = header
        row_id = row.get("id", f"ROW-{i}")
        status = row.get("annotation_status", "").strip()

        if status != "annotated":
            continue

        total_annotated += 1
        sentiment  = row.get("sentiment_label", "").strip()
        intent     = row.get("intent_label", "").strip()
        topic      = row.get("topic_label", "").strip()
        conf_str   = row.get("confidence_score", "").strip()

        # ── Missing labels ──
        if not sentiment:
            errors.append(f"[{row_id}] Missing sentiment_label")
        elif sentiment not in VALID_SENTIMENTS:
            errors.append(f"[{row_id}] Invalid sentiment_label: '{sentiment}' — must be one of {VALID_SENTIMENTS}")
        else:
            sentiment_counts[sentiment] += 1

        if not intent:
            errors.append(f"[{row_id}] Missing intent_label")
        elif intent not in VALID_INTENTS:
            errors.append(f"[{row_id}] Invalid intent_label: '{intent}' — must be one of {VALID_INTENTS}")
        else:
            intent_counts[intent] += 1

        if not topic:
            errors.append(f"[{row_id}] Missing topic_label")
        elif topic not in VALID_TOPICS:
            errors.append(f"[{row_id}] Invalid topic_label: '{topic}' — must be one of {VALID_TOPICS}")
        else:
            topic_counts[topic] += 1

        # ── Confidence ──
        try:
            conf = float(conf_str)
            confidence_vals.append(conf)
            if conf < confidence_threshold:
                flagged_rows.append({
                    "id": row_id,
                    "text": row.get("text", "")[:60],
                    "confidence_score": conf,
                    "sentiment": sentiment,
                })
                warnings.append(f"[{row_id}] Low confidence: {conf:.2f} — flagged for review")
        except (ValueError, TypeError):
            errors.append(f"[{row_id}] Invalid confidence_score: '{conf_str}'")

    avg_confidence = round(sum(confidence_vals) / len(confidence_vals), 3) if confidence_vals else 0.0

    # Consistency score = % of entries above threshold
    high_conf = sum(1 for c in confidence_vals if c >= confidence_threshold)
    consistency = round(high_conf / len(confidence_vals) * 100, 1) if confidence_vals else 0.0

    return {
        "total_rows":         len(rows),
        "total_annotated":    total_annotated,
        "errors":             errors,
        "warnings":           warnings,
        "flagged_rows":       flagged_rows,
        "sentiment_counts":   dict(sentiment_counts),
        "intent_counts":      dict(intent_counts),
        "topic_counts":       dict(topic_counts),
        "avg_confidence":     avg_confidence,
        "consistency_score":  consistency,
    }


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────
def print_report(report: dict, threshold: float):
    print("\n" + "="*60)
    print("  ANNOTATION VALIDATION REPORT")
    print("="*60)
    print(f"  Total rows in dataset : {report['total_rows']}")
    print(f"  Annotated entries     : {report['total_annotated']}")
    print(f"  Confidence threshold  : {threshold}")
    print(f"  Avg confidence score  : {report['avg_confidence']:.3f}")
    print(f"  Consistency score     : {report['consistency_score']}%")
    print("-"*60)

    print("\n📊 Label Distribution")
    print("  Sentiment :", report["sentiment_counts"])
    print("  Intent    :", report["intent_counts"])
    print("  Topic     :", report["topic_counts"])

    print(f"\n❌ Errors ({len(report['errors'])} found)")
    if report["errors"]:
        for e in report["errors"][:10]:
            print(f"   {e}")
        if len(report["errors"]) > 10:
            print(f"   ... and {len(report['errors']) - 10} more.")
    else:
        print("   None — all labels are valid ✅")

    print(f"\n⚠️  Low Confidence Entries ({len(report['flagged_rows'])} flagged)")
    if report["flagged_rows"]:
        for item in report["flagged_rows"][:5]:
            print(f"   [{item['id']}] conf={item['confidence_score']:.2f} | {item['text']}...")
        if len(report["flagged_rows"]) > 5:
            print(f"   ... and {len(report['flagged_rows']) - 5} more.")
    else:
        print("   None — all entries meet the confidence threshold ✅")

    print("\n" + "="*60)
    passed = len(report["errors"]) == 0
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"  Overall Validation: {status}")
    if report["consistency_score"] >= 90:
        print(f"  Consistency: ✅ GOOD ({report['consistency_score']}% ≥ 90%)")
    else:
        print(f"  Consistency: ⚠️  LOW ({report['consistency_score']}% < 90%) — review flagged rows")
    print("="*60)


# ─────────────────────────────────────────────
# SAVE FLAGGED ENTRIES
# ─────────────────────────────────────────────
def save_flagged(flagged_rows: list):
    if not flagged_rows:
        return
    output_path = "results/flagged_for_review.csv"
    Path("results").mkdir(exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "confidence_score", "sentiment"])
        writer.writeheader()
        writer.writerows(flagged_rows)
    print(f"\n📁 Flagged entries saved to: {output_path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Validate annotated dataset.")
    parser.add_argument("--file",      type=str,   default="annotation/annotated_dataset.csv",
                        help="Path to annotated CSV file")
    parser.add_argument("--threshold", type=float, default=0.75,
                        help="Minimum confidence score (default: 0.75)")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"[ERROR] File not found: {filepath}")
        return

    print(f"Loading dataset: {filepath} ...")
    rows   = load_csv(str(filepath))
    report = validate(rows, confidence_threshold=args.threshold)
    print_report(report, threshold=args.threshold)
    save_flagged(report["flagged_rows"])


if __name__ == "__main__":
    main()
