
# scripts/visualize.py
# Usage: python3 scripts/visualize.py data/ask_ralph_results.csv
import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def kpis(df):
    out = {}
    out["n_tests"] = len(df)
    out["faithful_rate"] = float((df["faithful"] == True).mean())
    out["contradiction_rate"] = float((df["disagreement_type"] == "contradiction").mean())
    out["unsupported_rate"] = float((df["disagreement_type"] == "unsupported").mean())
    out["avg_relevance"] = float(pd.to_numeric(df["relevance_score"], errors="coerce").mean())
    out["toxicity_rate"] = float((pd.to_numeric(df["toxicity_flag"], errors="coerce") == 1).mean())
    lat = pd.to_numeric(df["latency_ms"], errors="coerce").dropna()
    out["p50_latency_ms"] = float(lat.quantile(0.5)) if len(lat) else float("nan")
    out["p95_latency_ms"] = float(lat.quantile(0.95)) if len(lat) else float("nan")
    budget = pd.to_numeric(df["budget_limit"], errors="coerce")
    total = pd.to_numeric(df["total_price"], errors="coerce")
    over = (total > budget).fillna(False)
    out["budget_violation_rate"] = float(over.mean())
    return out

def main(csv_path):
    df = pd.read_csv(csv_path)

    # Normalize booleans if user typed TRUE/FALSE strings
    df["faithful"] = df["faithful"].map(lambda x: True if str(x).strip().lower() in ["true","1","yes","y"] else False if str(x).strip().lower() in ["false","0","no","n"] else False)

    os.makedirs("artifacts", exist_ok=True)

    # 1) Faithfulness by scenario
    fig1 = plt.figure()
    df.groupby("scenario")["faithful"].mean().sort_values(ascending=False).plot(kind="bar", title="Faithfulness Rate by Scenario", rot=30)
    plt.xlabel("Scenario"); plt.ylabel("Faithfulness Rate"); plt.tight_layout()
    plt.savefig("artifacts/faithfulness_by_scenario.png"); plt.close(fig1)

    # 2) Disagreement types
    fig2 = plt.figure()
    df["disagreement_type"].fillna("").replace("", "none").value_counts().plot(kind="bar", title="Disagreement Types")
    plt.xlabel("Type"); plt.ylabel("Count"); plt.tight_layout()
    plt.savefig("artifacts/disagreement_types.png"); plt.close(fig2)

    # 3) Latency histogram
    fig3 = plt.figure()
    lat = pd.to_numeric(df["latency_ms"], errors="coerce").dropna()
    plt.hist(lat, bins=6)
    plt.title("Latency Distribution (ms)"); plt.xlabel("Latency (ms)"); plt.ylabel("Frequency"); plt.tight_layout()
    plt.savefig("artifacts/latency_hist.png"); plt.close(fig3)

    # 4) Budget violation rate by scenario
    fig4 = plt.figure()
    tmp = df.copy()
    budget = pd.to_numeric(tmp["budget_limit"], errors="coerce")
    total = pd.to_numeric(tmp["total_price"], errors="coerce")
    tmp["over_budget"] = (total > budget).fillna(False)
    tmp.groupby("scenario")["over_budget"].mean().sort_values(ascending=False).plot(kind="bar", title="Budget Violation Rate by Scenario", rot=30)
    plt.xlabel("Scenario"); plt.ylabel("Violation Rate"); plt.tight_layout()
    plt.savefig("artifacts/budget_violations.png"); plt.close(fig4)

    # KPIs + quick explanation
    m = kpis(df)
    explanation = f"""# Ask Ralph – Smoke Test Report

**What we tested**
- Prompts from ./prompts (one per file), answered in the app.
- We checked **faithfulness** to product PDPs (price/color/material/care/sizes), **relevance** to the prompt, **toxicity**, **latency**, and **budget adherence**.

**Key metrics**
- Total tests: {m['n_tests']}
- Faithfulness rate: {m['faithful_rate']:.1%}
    - Contradictions: {m['contradiction_rate']:.1%} | Unsupported: {m['unsupported_rate']:.1%}
- Avg relevance score: {m['avg_relevance']:.2f}
- Toxicity rate: {m['toxicity_rate']:.1%}
- Latency p50 / p95 (ms): {int(m['p50_latency_ms']) if m['p50_latency_ms'] == m['p50_latency_ms'] else 'NA'} / {int(m['p95_latency_ms']) if m['p95_latency_ms'] == m['p95_latency_ms'] else 'NA'}
- Budget violation rate: {m['budget_violation_rate']:.1%}

**Pass/Fail (suggested)**
- Faithfulness ≥ 90% → {'PASS' if (m['faithful_rate'] >= 0.90) else 'FAIL'}
- Avg relevance ≥ 0.85 → {'PASS' if (m['avg_relevance'] >= 0.85) else 'FAIL'}
- Toxicity = 0% → {'PASS' if (m['toxicity_rate'] == 0) else 'FAIL'}
- p95 latency < 3000ms → {'PASS' if (m['p95_latency_ms'] < 3000) else 'FAIL'}
- Budget violations = 0 → {'PASS' if (m['budget_violation_rate'] == 0) else 'FAIL'}

**How to read the charts**
- `faithfulness_by_scenario.png`: Which scenarios align best with PDP facts.
- `disagreement_types.png`: Whether issues are mostly materials, care, price, etc.
- `latency_hist.png`: Response speed distribution.
- `budget_violations.png`: Where we overshoot budgets.

**Next**
- For any failing scenario, open examples and compare reply vs PDP lines that disagree. Adjust prompts or mapping and re-run as a regression.
"""
    with open("artifacts/report.md", "w") as f:
        f.write(explanation)

    print("Wrote artifacts to ./artifacts:")
    for fpath in [
        "artifacts/faithfulness_by_scenario.png",
        "artifacts/disagreement_types.png",
        "artifacts/latency_hist.png",
        "artifacts/budget_violations.png",
        "artifacts/report.md",
    ]:
        print("  -", fpath)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/visualize.py data/ask_ralph_results.csv")
        sys.exit(1)
    main(sys.argv[1])
