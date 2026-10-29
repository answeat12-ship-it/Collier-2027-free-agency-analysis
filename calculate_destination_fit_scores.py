from pathlib import Path

import numpy as np
import pandas as pd

# STEP 1: Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# STEP 2: Load completed scouting evaluations
scouting = pd.read_csv(
    DATA_DIR / "collier_2027_fit_evaluations.csv"
)

weights_df = pd.read_csv(
    DATA_DIR / "collier_2027_scoring_weights.csv"
)

# STEP 3: Define our evaluation categories
categories = [
    "basketball_compatibility",
    "role_opportunity",
    "competitive_outlook",
    "financial_opportunity",
    "stability_continuity"
]

# Validate destinations
if len(scouting) != 4:
    raise ValueError("Expected four destinations.")

if scouting["destination"].duplicated().any():
    raise ValueError("Duplicate destinations found.")

# Validate scoring weights
if weights_df["category"].duplicated().any():
    raise ValueError("Duplicate scoring categories.")

weights = weights_df.set_index("category")["weight"]

if set(weights.index) != set(categories):
    raise ValueError("Scoring categories do not match.")

weights = pd.to_numeric(
    weights.reindex(categories),
    errors="raise"
)

if weights.isna().any():
    raise ValueError("Missing scoring weights.")

if (weights < 0).any():
    raise ValueError("Weights cannot be negative.")

if not np.isclose(weights.sum(), 1.0):
    raise ValueError("Scoring weights must total 100%.")

# STEP 4: Validate all 20 grades
grades = scouting[categories].apply(
    pd.to_numeric,
    errors="raise"
)

if grades.isna().any().any():
    raise ValueError(
        "Incomplete evaluations. "
        "All 20 grades must be present."
    )

if not grades.ge(1).all().all() or not grades.le(5).all().all():
    raise ValueError("Grades must fall between 1 and 5.")

# STEP 5: Calculate weighted contributions
results = scouting[["destination"]].copy()

for category in categories:
    results[f"{category}_contribution"] = (
        grades[category] * weights[category]
    )

contribution_columns = [
    f"{category}_contribution"
    for category in categories
]

# STEP 6: Calculate final weighted scores
results["weighted_fit_score"] = (
    results[contribution_columns].sum(axis=1)
)

# STEP 7: Rank by weighted score
results = results.sort_values(
    "weighted_fit_score",
    ascending=False
).reset_index(drop=True)

results["baseline_rank"] = (
    np.arange(1, len(results) + 1)
)

# STEP 8: Save results
output_path = (
    DATA_DIR / "collier_2027_weighted_fit_scores.csv"
)

results.to_csv(output_path, index=False)

# STEP 9: Display results
print("\n2027 COLLIER DESTINATION FIT SCORES")
print("=" * 55)

print(
    results[
        [
            "baseline_rank",
            "destination",
            "weighted_fit_score"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

print("\nCATEGORY WEIGHTS")
print(weights.to_string())

print("\nLEADER VS. SECOND PLACE")
gap = (
    results.loc[0, "weighted_fit_score"]
    - results.loc[1, "weighted_fit_score"]
)

print(f"Score difference: {gap:.3f}")

print("\nRESULTS SAVED")
print(output_path)

print(
    "\nInterpretation: These scores represent "
    "the agreed scouting framework, not "
    "a prediction of Collier's decision."
)