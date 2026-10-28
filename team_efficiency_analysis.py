from pathlib import Path
import pandas as pd
import numpy as np

# STEP 1: Load our datasets
data_folder = Path(__file__).resolve().parent / "data"

schedule = pd.read_csv(
    data_folder / "wnba_schedule_2026.csv",
    dtype={"game_id": str}
)

box = pd.read_csv(
    data_folder / "team_box_2026.csv",
    dtype={"game_id": str}
)

standings = pd.read_csv(
    data_folder / "wnba_2026_standings_calculated.csv"
)

# Step 2: Identify the 330 official regular-season games
# STEP 2: Identify the 330 official regular-season games
valid_teams = set(standings["team"])

regular = schedule[
    (pd.to_numeric(schedule["season"], errors="coerce") == 2026)
    & (pd.to_numeric(schedule["season_type"], errors="coerce") == 2)
    & (schedule["home_display_name"].isin(valid_teams))
    & (schedule["away_display_name"].isin(valid_teams))
    & (schedule["game_id"] != "401857321")
].copy()

for col in ["home_score", "away_score"]:
    regular[col] = pd.to_numeric(
        regular[col], errors="coerce"
    )

regular = regular[
    (regular["home_score"] > 0)
    & (regular["away_score"] > 0)
].copy()

assert len(regular) == 330
assert regular["game_id"].is_unique

# STEP 3: Match ESPN box scores to those games
games = box[
    box["game_id"].isin(regular["game_id"])
].copy()

print("\nLEAGUE BOX-SCORE COVERAGE")
print("Matched games:", games["game_id"].nunique())
print("Team rows:", len(games))

rows_per_game = games.groupby("game_id").size()

if (
    games["game_id"].nunique() != 330
    or len(games) != 660
    or not (rows_per_game == 2).all()
):
    raise ValueError(
        "League box-score coverage is incomplete. "
        "Inspect missing games before calculating ratings."
    )

# STEP 4: Convert required statistics to numbers
stats = [
    "field_goals_attempted",
    "free_throws_attempted",
    "offensive_rebounds",
    "total_turnovers"
]

for col in stats:
    games[col] = pd.to_numeric(
        games[col], errors="coerce"
    )

if games[stats].isna().any().any():
    print(games[stats].isna().sum())
    raise ValueError("Missing required box-score statistics.")

# STEP 5: Validate team scores against the schedule

# Connect ESPN team box scores with final game results
games = games.merge(
    regular[
        ["game_id", "home_score", "away_score"]
    ],
    on="game_id",
    how="left",
    validate="many_to_one"
)

# Use each team's actual box-score total
games["points"] = pd.to_numeric(
    games["team_score"],
    errors="coerce"
)

if games["points"].isna().any():
    raise ValueError("Some team scores are missing.")

# Compare both box-score totals with the final scores
score_check = games.groupby("game_id").agg(
    box_scores=("points", lambda x: sorted(x.tolist())),
    home_score=("home_score", "first"),
    away_score=("away_score", "first")
)

score_check["schedule_scores"] = score_check.apply(
    lambda row: sorted([
        row["home_score"],
        row["away_score"]
    ]),
    axis=1
)

mismatches = score_check[
    score_check["box_scores"]
    != score_check["schedule_scores"]
]

if not mismatches.empty:
    print("\nSCORE MISMATCHES:")
    print(mismatches.to_string())
    raise ValueError("Team scores do not match schedule.")

print("\nSCORE VALIDATION")
print("Games checked:", len(score_check))
print("Score mismatches:", len(mismatches))
print("\nAll team scores matched!")

# STEP 6: Inspect turnover column definitions
print("\nTURNOVER COLUMN CHECK")
turnover_cols = [
    "team_name",
    "turnovers",
    "team_turnovers",
    "total_turnovers"
]

print(games[turnover_cols].head(8).to_string(index=False))

# STEP 7: Estimate team possessions
games["poss_est"] = (
    games["field_goals_attempted"]
    - games["offensive_rebounds"]
    + games["total_turnovers"]
    + 0.44 * games["free_throws_attempted"]
)

if (games["poss_est"] <= 0).any():
    raise ValueError("Invalid possession estimate detected.")

# Average both teams' estimates for each game
games["game_poss_est"] = (
    games.groupby("game_id")["poss_est"]
    .transform("mean")
)

# Find opposing team's score
games["opponent_points"] = (
    games.groupby("game_id")["points"]
    .transform("sum")
    - games["points"]
)

# STEP 8: Aggregate league totals
efficiency = games.groupby("team_name").agg(
    games_played=("game_id", "nunique"),
    points_scored=("points", "sum"),
    points_allowed=("opponent_points", "sum"),
    total_possessions=("game_poss_est", "sum")
).reset_index()

efficiency["offensive_rating"] = (
    100 * efficiency["points_scored"]
    / efficiency["total_possessions"]
)

efficiency["defensive_rating"] = (
    100 * efficiency["points_allowed"]
    / efficiency["total_possessions"]
)

efficiency["net_rating"] = (
    efficiency["offensive_rating"]
    - efficiency["defensive_rating"]
)

# STEP 9: Rank all teams
efficiency["offense_rank"] = (
    efficiency["offensive_rating"]
    .rank(ascending=False, method="min")
    .astype(int)
)

efficiency["defense_rank"] = (
    efficiency["defensive_rating"]
    .rank(ascending=True, method="min")
    .astype(int)
)

efficiency["net_rank"] = (
    efficiency["net_rating"]
    .rank(ascending=False, method="min")
    .astype(int)
)

assert len(efficiency) == 15
assert (efficiency["games_played"] == 44).all()

# STEP 10: Review results
efficiency = efficiency.sort_values("net_rank")

display_cols = [
    "team_name",
    "offensive_rating",
    "defensive_rating",
    "net_rating",
    "offense_rank",
    "defense_rank",
    "net_rank"
]

print("\n2026 WNBA ESTIMATED EFFICIENCY")
print(
    efficiency[display_cols]
    .round(2)
    .to_string(index=False)
)

liberty = efficiency[
    efficiency["team_name"] == "Liberty"
].iloc[0]

print("\nNEW YORK LIBERTY EFFICIENCY")
print(f"Offensive rating: {liberty['offensive_rating']:.2f}")
print(f"Defensive rating: {liberty['defensive_rating']:.2f}")
print(f"Net rating: {liberty['net_rating']:+.2f}")
print(f"Offensive rank: {liberty['offense_rank']}/15")
print(f"Defensive rank: {liberty['defense_rank']}/15")
print(f"Net rating rank: {liberty['net_rank']}/15")

# STEP 11: Liberty efficiency by opponent strength

# Retrieve New York's per-game box-score records
liberty_game_stats = games[
    games["team_name"] == "Liberty"
].copy()

# Load our previously calculated opponent groups
opponent_data = pd.read_csv(
    data_folder / "ny_liberty_2026_opponent_strength.csv",
    dtype={"game_id": str}
)

# Attach opponent strength and game result
liberty_game_stats = liberty_game_stats.merge(
    opponent_data[
        ["game_id", "opponent", "opponent_group", "result"]
    ],
    on="game_id",
    how="left",
    validate="one_to_one"
)

# Validate the matching records
assert len(liberty_game_stats) == 44
assert liberty_game_stats["opponent_group"].notna().all()

# Calculate efficiency for each opponent category
def summarize_efficiency(df):
    possessions = df["game_poss_est"].sum()

    return pd.Series({
        "games": len(df),
        "offensive_rating": (
            100 * df["points"].sum() / possessions
        ),
        "defensive_rating": (
            100 * df["opponent_points"].sum() / possessions
        ),
        "net_rating": (
            100 * (
                df["points"].sum()
                - df["opponent_points"].sum()
            ) / possessions
        )
    })

strength_results = (
    liberty_game_stats
    .groupby("opponent_group")
    .apply(summarize_efficiency, include_groups=False)
    .reset_index()
)

print("\nLIBERTY EFFICIENCY BY OPPONENT STRENGTH")
print(strength_results.round(2).to_string(index=False))

# Compare efficiency in wins and losses
result_results = (
    liberty_game_stats
    .groupby("result")
    .apply(summarize_efficiency, include_groups=False)
    .reset_index()
)

print("\nLIBERTY EFFICIENCY BY GAME RESULT")
print(result_results.round(2).to_string(index=False))

# Save for our scouting report
liberty_game_stats.to_csv(
    data_folder / "ny_liberty_2026_game_efficiency.csv",
    index=False
)

print("\nLiberty game-level efficiency saved!")



# STEP 12: Save results
efficiency.to_csv(
    data_folder / "wnba_2026_efficiency_estimates.csv",
    index=False
)

print("\nEfficiency analysis completed!")


