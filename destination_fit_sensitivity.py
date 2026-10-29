from pathlib import Path

import numpy as np
import pandas as pd

# STEP 1: Locate our data
DATA_DIR = Path(__file__).resolve().parent / "data"

scouting = pd.read_csv(
    DATA_DIR / "collier_2027_fit_evaluations.csv"
)

weights_df = pd.read_csv(
    DATA_DIR / "collier_2027_scoring_weights.csv"
)

categories = [
    "basketball_compatibility",
    "role_opportunity",
    "competitive_outlook",
    "financial_opportunity",
    "stability_continuity",
]

# STEP 2: Validate grades
grades = scouting.set_index("destination")[categories]

if len(grades) != 4 or grades.index.has_duplicates:
    raise ValueError("Expected four unique destinations.")

grades = grades.apply(pd.to_numeric, errors="raise")

if grades.isna().any().any():
    raise ValueError("Some scouting grades are missing.")

if not grades.ge(1).all().all() or not grades.le(5).all().all():
    raise ValueError("Grades must be between 1 and 5.")

# STEP 3: Retrieve baseline weights from our CSV
baseline = (
    weights_df.set_index("category")["weight"]
    .reindex(categories)
)

if baseline.isna().any():
    raise ValueError("Baseline weights are incomplete.")

# STEP 4: Define illustrative alternative priorities
# Order:
# Basketball, Role, Competitive, Financial, Stability

scenarios = {
    "Baseline": baseline.to_numpy(dtype=float),

    "Basketball-first": [
        0.40, 0.25, 0.20, 0.075, 0.075
    ],

    "Role-first": [
        0.20, 0.40, 0.20, 0.10, 0.10
    ],

    "Competition-first": [
        0.25, 0.20, 0.35, 0.10, 0.10
    ],

    "Compensation-first": [
        0.20, 0.20, 0.15, 0.30, 0.15
    ],

    "Stability-first": [
        0.20, 0.20, 0.15, 0.10, 0.35
    ],
}

# STEP 5: Calculate results for every scenario
records = []
weight_records = []

for scenario_name, weight_values in scenarios.items():

    weights = np.asarray(weight_values, dtype=float)

    if not np.isclose(weights.sum(), 1.0):
        raise ValueError(
            f"Weights do not total 100%: {scenario_name}"
        )

    if (weights < 0).any():
        raise ValueError("Negative weight found.")

    weight_records.append({
        "scenario": scenario_name,
        **dict(zip(categories, weights))
    })

    scores = grades.to_numpy() @ weights

    for destination, score in zip(grades.index, scores):
        records.append({
            "scenario": scenario_name,
            "destination": destination,
            "weighted_score": float(score)
        })

results = pd.DataFrame(records)

# STEP 6: Rank destinations within each scenario
results["rank"] = (
    results.groupby("scenario")["weighted_score"]
    .rank(method="min", ascending=False)
    .astype(int)
)

# STEP 7: Save outputs
results_path = (
    DATA_DIR / "collier_2027_sensitivity_results.csv"
)

weights_path = (
    DATA_DIR / "collier_2027_sensitivity_weights.csv"
)

results.to_csv(results_path, index=False)

pd.DataFrame(weight_records).to_csv(
    weights_path, index=False
)

# STEP 8: Print scenario rankings
print("\nDESTINATION FIT SENSITIVITY ANALYSIS")
print("=" * 65)

for name in scenarios:

    subset = results[
        results["scenario"].eq(name)
    ].sort_values(
        ["weighted_score", "destination"],
        ascending=[False, True]
    )

    print(f"\n{name.upper()}")
    print(
        subset[
            ["destination", "weighted_score", "rank"]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}"
        )
    )

# STEP 9: Compare Minnesota and Golden State
comparison = results.pivot(
    index="scenario",
    columns="destination",
    values="weighted_score"
)

comparison["Minnesota_minus_Golden_State"] = (
    comparison["Minnesota Lynx"]
    - comparison["Golden State Valkyries"]
)

print("\nMINNESOTA VS. GOLDEN STATE")
print(
    comparison[
        ["Minnesota_minus_Golden_State"]
    ].to_string(float_format=lambda x: f"{x:+.3f}")
)

print("\nPositive = Minnesota leads")
print("Negative = Golden State leads")
print("\nOutputs saved:")
print(results_path)
print(weights_path)

print(
    "\nThese scenarios are illustrative. "
    "They do not represent Collier's stated priorities."
)