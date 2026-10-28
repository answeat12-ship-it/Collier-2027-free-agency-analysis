from pathlib import Path
import pandas as pd

# STEP 1: Load our existing results
data_folder = Path(__file__).resolve().parent / "data"

liberty = pd.read_csv(
    data_folder / "ny_liberty_2026_game_efficiency.csv",
    dtype={"game_id": str}
)

league = pd.read_csv(
    data_folder / "wnba_2026_efficiency_estimates.csv"
)

# STEP 2: Match opponent names between datasets
# Example: "Golden State Valkyries" -> "Valkyries"
# All 2026 WNBA franchise names have unique final words.
liberty["opponent_short"] = (
    liberty["opponent"].str.split().str[-1]
)

opponent_baselines = league[
    ["team_name", "offensive_rating", "defensive_rating"]
].rename(columns={
    "team_name": "opponent_short",
    "offensive_rating": "opponent_off_rating",
    "defensive_rating": "opponent_def_rating"
})

liberty = liberty.merge(
    opponent_baselines,
    on="opponent_short",
    how="left",
    validate="many_to_one"
)

# STEP 3: Validate matches
assert len(liberty) == 44
assert liberty["game_id"].is_unique

if liberty[
    ["opponent_off_rating", "opponent_def_rating"]
].isna().any().any():
    raise ValueError("Some opponent ratings are missing.")

# STEP 4: Calculate game-level expected efficiencies
liberty["ny_off_rating"] = (
    100 * liberty["points"] / liberty["game_poss_est"]
)

liberty["ny_def_rating"] = (
    100 * liberty["opponent_points"]
    / liberty["game_poss_est"]
)

# Positive = New York scored more efficiently than
# that opponent typically allowed.
liberty["offense_vs_expected"] = (
    liberty["ny_off_rating"]
    - liberty["opponent_def_rating"]
)

# Positive = New York allowed fewer points than
# that opponent typically scored.
liberty["defense_vs_expected"] = (
    liberty["opponent_off_rating"]
    - liberty["ny_def_rating"]
)

# STEP 5: Summarize results using possession weights
def summarize(group):
    possessions = group["game_poss_est"].sum()

    offense = (
        group["offense_vs_expected"]
        * group["game_poss_est"]
    ).sum() / possessions

    defense = (
        group["defense_vs_expected"]
        * group["game_poss_est"]
    ).sum() / possessions

    return pd.Series({
        "games": len(group),
        "offense_vs_expected": offense,
        "defense_vs_expected": defense,
        "combined_advantage": offense + defense
    })

print("\nOVERALL PERFORMANCE VS OPPONENT BASELINES")
print(summarize(liberty).round(2).to_string())

print("\nBY OPPONENT STRENGTH")
strength = liberty.groupby(
    "opponent_group"
).apply(
    summarize,
    include_groups=False
)

print(strength.round(2).to_string())

# STEP 6: Save the analysis
liberty.to_csv(
    data_folder / "ny_liberty_2026_adjusted_game_efficiency.csv",
    index=False
)

strength.to_csv(
    data_folder / "ny_liberty_2026_adjusted_strength_summary.csv"
)

print("\nMatchup-context analysis completed!")