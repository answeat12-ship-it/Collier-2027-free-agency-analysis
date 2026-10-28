from pathlib import Path
import pandas as pd

# STEP 1: Load our existing data
data_folder = Path(__file__).resolve().parent / "data"

schedule = pd.read_csv(
    data_folder / "wnba_schedule_2026.csv",
    dtype={"game_id": str}
)

standings = pd.read_csv(
    data_folder / "wnba_2026_standings_calculated.csv"
)

valid_teams = set(standings["team"])


# Step 2: Filter completed regular-season games
regular = schedule[
    (pd.to_numeric(schedule["season"], errors="coerce") == 2026)
    & (pd.to_numeric(schedule["season_type"], errors="coerce") == 2)
].copy()

for column in ["home_score", "away_score"]:
    regular[column] = pd.to_numeric(
        regular[column], errors="coerce"
    )

regular = regular[
    (regular["home_score"] > 0)
    & (regular["away_score"] > 0)
    & (regular["game_id"] != "401857321")
    & (regular["home_display_name"].isin(valid_teams))
    & (regular["away_display_name"].isin(valid_teams))
].copy()

# Validate game count and duplicate IDs
assert len(regular) == 330
assert regular["game_id"].is_unique

print("Validated league games:", len(regular))

# Step 3: Create one row per team per game
home_games = pd.DataFrame({
    "team": regular["home_display_name"],
    "opponent": regular["away_display_name"],
    "points_scored": regular["home_score"],
    "points_allowed": regular["away_score"]
})

away_games = pd.DataFrame({
    "team": regular["away_display_name"],
    "opponent": regular["home_display_name"],
    "points_scored": regular["away_score"],
    "points_allowed": regular["home_score"]
})

team_games = pd.concat(
    [home_games, away_games],
    ignore_index=True
)

# All 15 teams should have exactly 44 games
assert len(team_games) == 660
assert (team_games.groupby("team").size() == 44).all()

# STEP 4: Calculate team scoring and variability
comparison = team_games.groupby("team").agg(
    games=("points_scored", "count"),
    avg_scored=("points_scored", "mean"),
    avg_allowed=("points_allowed", "mean"),
    offensive_sd=("points_scored", "std"),
    defensive_sd=("points_allowed", "std")
).reset_index()

# STEP 5: Identify unusually low-scoring games
# Compare each performance to that team's own average
team_games = team_games.merge(
    comparison[["team", "avg_scored", "avg_allowed"]],
    on="team",
    how="left",
    validate="many_to_one"
)

team_games["offensive_drought"] = (
    team_games["points_scored"]
    <= team_games["avg_scored"] - 10
)

team_games["defensive_spike"] = (
    team_games["points_allowed"]
    >= team_games["avg_allowed"] + 10
)

# Count notable scoring swings
swings = team_games.groupby("team").agg(
    offensive_droughts=("offensive_drought", "sum"),
    defensive_spikes=("defensive_spike", "sum")
).reset_index()

comparison = comparison.merge(
    swings,
    on="team",
    validate="one_to_one"
)

# STEP 6: Rank teams
comparison["offense_rank"] = comparison[
    "avg_scored"
].rank(ascending=False, method="min").astype(int)

comparison["defense_rank"] = comparison[
    "avg_allowed"
].rank(ascending=True, method="min").astype(int)

comparison["offensive_volatility_rank"] = comparison[
    "offensive_sd"
].rank(ascending=False, method="min").astype(int)

comparison["defensive_volatility_rank"] = comparison[
    "defensive_sd"
].rank(ascending=False, method="min").astype(int)

# STEP 7: Display league comparison
comparison = comparison.sort_values("offense_rank")

print("\n2026 WNBA OFFENSE / DEFENSE COMPARISON")
print(
    comparison.round(2).to_string(index=False)
)

# STEP 8: Focus on New York
liberty = comparison[
    comparison["team"] == "New York Liberty"
].iloc[0]

print("\nNEW YORK LIBERTY CONSISTENCY PROFILE")
print(f"Points scored per game: {liberty['avg_scored']:.2f}")
print(f"Points allowed per game: {liberty['avg_allowed']:.2f}")
print(f"Offense rank: {liberty['offense_rank']}/15")
print(f"Defense rank: {liberty['defense_rank']}/15")

print(f"\nOffensive SD: {liberty['offensive_sd']:.2f}")
print(
    "Offensive volatility rank:",
    f"{liberty['offensive_volatility_rank']}/15"
)

print(f"Defensive SD: {liberty['defensive_sd']:.2f}")
print(
    "Defensive volatility rank:",
    f"{liberty['defensive_volatility_rank']}/15"
)

print(
    "\nGames scoring 10+ below team average:",
    liberty["offensive_droughts"]
)

print(
    "Games allowing 10+ above team average:",
    liberty["defensive_spikes"]
)

# STEP 9: Compare New York with league medians
print("\nLEAGUE COMPARISON")
print(
    "Median offensive SD:",
    round(comparison["offensive_sd"].median(), 2)
)

print(
    "Median defensive SD:",
    round(comparison["defensive_sd"].median(), 2)
)

# STEP 10: Save results
comparison.to_csv(
    data_folder / "wnba_2026_consistency_comparison.csv",
    index=False
)

print("\nConsistency analysis completed!")
