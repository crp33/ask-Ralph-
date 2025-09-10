# Ask Ralph – Smoke Tests

## Quick start
1) Put your prompt files (one prompt per `.txt`) in `./prompts/`
2) Build/update the results CSV:
   ```bash
   python3 scripts/prepare_from_prompts.py prompts
   ```
3) Run your tests in the app. Fill the CSV columns:
   - `items_returned`, `faithful`, `disagreement_type`, `disagreement_entity`
   - `relevance_score` (0–1), `toxicity_flag` (0/1)
   - `latency_ms`, `total_price`, `budget_limit`, `notes`
4) Visualize and summarize:
   ```bash
   python3 scripts/visualize.py data/ask_ralph_results.csv
   ```
5) See charts + `artifacts/report.md`.

**Relevance scoring quick rubric**: average of 4 binary checks (occasion, budget, constraints, coherent outfit).




