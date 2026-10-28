from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Define our assessment criteria
weights = {
    "basketball_compatibility": 0.25,
    "role_opportunity": 0.25,
    "competitive_outlook": 0.20,
    "financial_opportunity": 0.15,
    "stability_continuity": 0.15
}

assert abs(sum(weights.values()) - 1.0) < 1e-9

# STEP 2: Load our completed comparison
comparison = pd.read_csv(
    data_folder / "collier_2027_destination_comparison.csv"
)

assert len(comparison) == 4

# STEP 3: Prepare separate scouting evaluations
scouting = comparison[["destination"]].copy()

# No grades until we review the evidence together.
for category in weights:
    scouting[category] = pd.NA
    scouting[f"{category}_evidence"] = ""

# STEP 4: Preserve the scoring weights
weight_table = pd.DataFrame([
    {"category": category, "weight": weight}
    for category, weight in weights.items()
])

# STEP 5: Save without overwriting existing work
scouting_path = (
    data_folder / "collier_2027_fit_evaluations.csv"
)

weights_path = (
    data_folder / "collier_2027_scoring_weights.csv"
)

if not scouting_path.exists():
    scouting.to_csv(scouting_path, index=False)
    print("Created:", scouting_path.name)
else:
    print("Preserved existing:", scouting_path.name)

if not weights_path.exists():
    weight_table.to_csv(weights_path, index=False)
    print("Created:", weights_path.name)
else:
    print("Preserved existing:", weights_path.name)

print("\nDESTINATION EVALUATION TEMPLATE")
print(scouting.to_string(index=False))
print("\nScoring template ready!")

