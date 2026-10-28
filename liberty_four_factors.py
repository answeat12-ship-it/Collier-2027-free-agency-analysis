from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# Load previously validated ESPN box scores
box = pd.read_csv(
    data_folder / "ny_liberty_2026_espn_box.csv",
    dtype={"game_id": str}
)

# Verify complete coverage
assert len(box) == 88
assert box["game_id"].nunique() == 44
assert (box.groupby("game_id").size() == 2).all()

# Required ESPN columns
stats = [
    "field_goals_made",
    "field_goals_attempted",
    "three_point_field_goals_made",
    "free_throws_attempted",
    "offensive_rebounds",
    "defensive_rebounds",
    "total_turnovers"
]

for col in stats:
    box[col] = pd.to_numeric(
        box[col], errors="coerce"
    )

if box[stats].isna().any().any():
    raise ValueError("Missing Four Factors statistics.")

# Identify New York and opposing teams
box["group"] = box["team_name"].apply(
    lambda name: "Liberty" if name == "Liberty"
    else "Opponents"
)

# Get the opposing team's defensive rebounds
box["opponent_dreb"] = (
    box.groupby("game_id")["defensive_rebounds"]
    .transform("sum")
    - box["defensive_rebounds"]
)

# Aggregate statistics before calculating percentages
totals = box.groupby("group")[
    stats + ["opponent_dreb"]
].sum()

# Effective field-goal percentage
totals["efg_pct"] = (
    (
        totals["field_goals_made"]
        + 0.5 * totals["three_point_field_goals_made"]
    )
    / totals["field_goals_attempted"]
    * 100
)

# Turnover percentage
totals["tov_pct"] = (
    totals["total_turnovers"]
    / (
        totals["field_goals_attempted"]
        + 0.44 * totals["free_throws_attempted"]
        + totals["total_turnovers"]
    )
    * 100
)

# Offensive rebounding percentage
totals["oreb_pct"] = (
    totals["offensive_rebounds"]
    / (
        totals["offensive_rebounds"]
        + totals["opponent_dreb"]
    )
    * 100
)

# Free-throw attempt rate
totals["ft_rate"] = (
    totals["free_throws_attempted"]
    / totals["field_goals_attempted"]
)

# Display the results
result = totals[
    ["efg_pct", "tov_pct", "oreb_pct", "ft_rate"]
]

print("\nLIBERTY VS OPPONENTS: FOUR FACTORS")
print(result.round(3).to_string())

# Save results
result.to_csv(
    data_folder / "ny_liberty_2026_four_factors.csv"
)

print("\nFour Factors analysis completed!")