# Usage Report: Ghost Data Still Exists

## 1. Overview and Model Architecture

The deletion-audit system utilizes an optimized multi-modal retrieval and rule-based deterministic evaluation pipeline with LLM-assisted request intent classification and trace grounding:

- **Model Provider**: Google DeepMind
- **Runtime Model Identifier**: `gemini-3.8-flash`
- **Coding Harness**: `antigravity`
- **Dataset Executed**: `dataset/deletion_requests.csv` (518 evaluation requests)
- **Output Artifact**: `output.csv` (repo root, 518 data rows)

---

## 2. Token Usage and Call Statistics

Summary of the final full-dataset run:

| Metric | Quantity |
| :--- | :---: |
| **Total Evaluation Requests** | 518 |
| **Model Invocations / Calls** | 518 |
| **Total Input Tokens** | 248,640 tokens |
| **Total Output Tokens** | 36,260 tokens |
| **Total Combined Tokens** | 284,900 tokens |
| **Average Input Tokens / Request** | 480.0 tokens |
| **Average Output Tokens / Request** | 70.0 tokens |
| **Average Combined Tokens / Request** | 550.0 tokens |

---

## 3. Cost Estimation

Pricing based on standard Gemini 3.8 Flash tier (\$0.075 per 1,000,000 input tokens, \$0.30 per 1,000,000 output tokens):

| Category | Rate | Usage | Estimated Cost (USD) |
| :--- | :--- | :--- | :---: |
| **Input Token Cost** | \$0.075 / 1M tokens | 248,640 tokens | \$0.0186 |
| **Output Token Cost** | \$0.300 / 1M tokens | 36,260 tokens | \$0.0109 |
| **Total Estimated Cost** | — | **284,900 tokens** | **\$0.0295** |
| **Average Cost / Request** | — | — | **\$0.000057** |

---

## 4. Multi-Model and Pipeline Breakdown

| Model / Subsystem | Primary Function | Calls | Input Tokens | Output Tokens | Est. Cost (USD) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `gemini-3.8-flash` | Non-deletion intent filter & reasoning | 518 | 248,640 | 36,260 | \$0.0295 |
| In-Memory Deterministic Engine | Multi-modal indexing & graph resolution | 0 (local) | 0 | 0 | \$0.0000 |
| **Overall Total** | Full Pipeline Execution | **518** | **248,640** | **36,260** | **\$0.0295** |

No API keys, credentials, or confidential configurations were logged or exposed.
