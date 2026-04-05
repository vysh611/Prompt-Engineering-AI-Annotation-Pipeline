# 🤖 Prompt Engineering & AI Annotation Pipeline

A hands-on project demonstrating structured **prompt engineering techniques** for Large Language Models (LLMs) and a complete **text annotation pipeline** for NLP classification tasks.

---

## 📌 Project Overview

This project covers two key areas of Generative AI development:

1. **Prompt Engineering** — Designing, testing, and evaluating prompts using Zero-Shot, Few-Shot, and Chain-of-Thought (CoT) strategies to guide LLM outputs for tasks like classification, summarization, and Q&A.
2. **Data Annotation Pipeline** — Curating, labeling, and validating a text dataset for NLP model training with consistency checks and quality assurance.

---

## 🗂️ Project Structure

```
prompt-engineering-annotation-pipeline/
│
├── prompts/
│   ├── zero_shot_prompts.json         # Zero-shot prompt templates
│   ├── few_shot_prompts.json          # Few-shot prompt templates
│   └── chain_of_thought_prompts.json  # Chain-of-Thought prompt templates
│
├── annotation/
│   ├── raw_dataset.csv                # Raw unlabeled text data
│   ├── annotated_dataset.csv          # Labeled dataset (2000+ entries)
│   └── annotation_guidelines.md      # Labeling rules and instructions
│
├── scripts/
│   ├── prompt_tester.py               # Test prompts against an LLM API
│   ├── evaluate_prompts.py            # Score and compare prompt outputs
│   └── annotation_validator.py        # Check annotation consistency
│
├── results/
│   └── prompt_evaluation_results.csv  # Output scores for each prompt
│
└── README.md
```

---

## 🧠 Prompt Engineering Techniques Used

| Technique | Description | Use Case |
|---|---|---|
| Zero-Shot | No examples given; relies on instruction clarity | Sentiment classification |
| Few-Shot | 2–5 examples provided in the prompt | Intent detection |
| Chain-of-Thought | Step-by-step reasoning guided via prompt | Multi-step Q&A |

---

## 📊 Annotation Pipeline

- **Dataset Size:** 2,000+ text entries
- **Labels:** Positive, Negative, Neutral (Sentiment) / Intent categories
- **Annotation Consistency:** 93%+ inter-annotator agreement
- **Tools:** Python (Pandas), CSV-based workflow
- **Guidelines:** See `annotation/annotation_guidelines.md`

---

## 📈 Key Results

- Designed and tested **50+ structured prompts** across 3 techniques
- Achieved **~40% improvement** in response relevance through iterative prompt refinement
- Curated a **2,000+ entry labeled dataset** with 93% annotation consistency
- Documented reusable prompt templates for classification, summarization, and Q&A

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Libraries:** Pandas, NumPy, OpenAI / Anthropic API (compatible)
- **Data Format:** JSON (prompts), CSV (datasets)

---

## 👩‍💻 Author

**Gandla Vyshnavi**  
Data Science | GEN AI | Prompt Engineering  
📧 gvyshnavi611@gmail.com | [LinkedIn](www.linkedin.com/in/gandla-vyshnavi) | [Portfolio](https://portfolio-lyart-five-39.vercel.app/)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
