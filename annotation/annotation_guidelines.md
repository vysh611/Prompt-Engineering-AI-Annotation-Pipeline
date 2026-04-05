# 📋 Annotation Guidelines

## Overview

This document defines the rules and standards for annotating the text dataset used in this project. All annotators must follow these guidelines to maintain consistency and achieve high inter-annotator agreement.

**Target Consistency Score: ≥ 93%**

---

## 1. Sentiment Labeling

### Labels
| Label | Definition |
|---|---|
| **Positive** | The text expresses satisfaction, happiness, praise, or approval |
| **Negative** | The text expresses dissatisfaction, frustration, criticism, or disappointment |
| **Neutral** | The text is factual, objective, or shows no clear emotional tone |

### Rules
- Base the label on the **overall tone**, not a single word.
- If the text contains both positive and negative content, label it based on the **dominant tone**.
- Sarcasm should be labeled based on the **intended meaning**, not the literal words.
  - Example: *"Oh great, another delayed delivery!"* → **Negative**
- Questions that are neutral in tone (e.g., *"When will my order arrive?"*) → **Neutral**

### Examples
| Text | Label | Reason |
|---|---|---|
| "Absolutely loved the product!" | Positive | Clear praise |
| "Stopped working after a day." | Negative | Clear complaint |
| "Order was delivered on Tuesday." | Neutral | Factual statement |
| "Yeah sure, best product ever." (sarcastic) | Negative | Sarcastic tone |
| "The size is smaller than expected but it works." | Neutral | Mixed but balanced |

---

## 2. Intent Labeling

### Labels
| Label | Definition |
|---|---|
| **Complaint** | User is expressing a problem, dissatisfaction, or frustration |
| **Inquiry** | User is asking a question or seeking information |
| **Feedback** | User is providing an opinion, review, or suggestion |
| **Request** | User wants an action to be taken (cancel, refund, change) |
| **Greeting** | User is opening a conversation or being polite |

### Rules
- A message can have **one primary intent** — choose the most dominant one.
- If the message asks a question AND complains, label based on the **main purpose**.
  - Example: *"Why is my order always late?!"* → **Complaint** (frustration-driven, not seeking info)
  - Example: *"What is your return policy?"* → **Inquiry**

---

## 3. Topic Labeling

### Labels
`Technology` | `Finance` | `Health` | `Sports` | `Entertainment`

### Rules
- Choose the topic that the text **primarily discusses**.
- If the text spans multiple topics, pick the one with the **most emphasis**.
- If the topic is ambiguous or not clearly in any category, mark it as `Unlabeled` for review.

---

## 4. Confidence Score

Each annotation must include a **confidence score** between 0.0 and 1.0:

| Score | Meaning |
|---|---|
| 0.90 – 1.00 | High confidence — clear and unambiguous |
| 0.75 – 0.89 | Moderate confidence — some ambiguity but label is justifiable |
| Below 0.75 | Low confidence — flag for second annotator review |

---

## 5. Quality Assurance

- All entries with confidence < 0.75 must be reviewed by a second annotator.
- A random 10% sample of annotated entries will be cross-validated.
- Disagreements between annotators should be resolved by majority vote or escalated to the project lead.
- Run `scripts/annotation_validator.py` after each batch to check consistency.

---

## 6. What to Avoid

- ❌ Do not label based on your personal opinion — follow the definitions strictly.
- ❌ Do not skip entries — mark uncertain ones with low confidence and flag them.
- ❌ Do not change previously agreed-upon labels without logging the reason.
- ❌ Do not use external context not present in the text itself.

---

## 7. Annotation Workflow

```
Raw Data → Annotator Labels → Confidence Score → Validator Script → QA Review → Final Dataset
```

1. Open `annotation/raw_dataset.csv`
2. For each row, assign `sentiment_label`, `intent_label`, `topic_label`
3. Assign a `confidence_score`
4. Change `annotation_status` from `unlabeled` to `annotated`
5. Save as `annotated_dataset.csv`
6. Run `python scripts/annotation_validator.py` to check your batch

---

*Last updated: 2026 | Project: Prompt Engineering & AI Annotation Pipeline*
