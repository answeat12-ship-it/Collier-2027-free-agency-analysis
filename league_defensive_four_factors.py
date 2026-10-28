from pathlib import Path
import pandas as pd

# STEP 1: Load our existing datasets
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

# STEP 2: Identify official regular-season games
valid_teams = set(standings["team"])

regular = schedule[
    (pd.to_numeric(schedule["season"], errors="coerce") == 2026)
    & (pd.to_numeric(schedule["season_type"], errors="coerce") == 2)
    & schedule["home_display_name"].isin(valid_teams)
    & schedule["away_display_name"].isin(valid_teams)
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

# STEP 3: Match the team box scores
games = box[
    box["game_id"].isin(regular["game_id"])
].copy()

assert len(games) == 660
assert games["game_id"].nunique() == 330
assert (games.groupby("game_id").size() == 2).all()

# STEP 4: Convert statistical columns
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
    games[col] = pd.to_numeric(
        games[col], errors="coerce"
    )

if games[stats].isna().any().any():
    raise ValueError("Missing required statistics.")

if (games[stats] < 0).any().any():
    raise ValueError("Negative box-score statistics found.")

# STEP 5: Attach the opponent's stats to each row
# Every game contains exactly two teams.
for col in stats:
    games[f"opp_{col}"] = (
        games.groupby("game_id")[col].transform("sum")
        - games[col]
    )

# STEP 6: Aggregate defensive statistics by team
defensive = games.groupby("team_name").agg(
    games_played=("game_id", "nunique"),
    opp_fgm=("opp_field_goals_made", "sum"),
    opp_fga=("opp_field_goals_attempted", "sum"),
    opp_3pm=("opp_three_point_field_goals_made", "sum"),
    opp_fta=("opp_free_throws_attempted", "sum"),
    opp_oreb=("opp_offensive_rebounds", "sum"),
    team_dreb=("defensive_rebounds", "sum"),
    forced_tov=("opp_total_turnovers", "sum")
).reset_index()

# Validate league coverage
assert len(defensive) == 15
assert (defensive["games_played"] == 44).all()

# Prevent division by zero
assert (defensive["opp_fga"] > 0).all()
assert (
    defensive["opp_oreb"] + defensive["team_dreb"] > 0
).all()

# STEP 7: Calculate Defensive Four Factors

# Opponent Effective Field Goal Percentage
defensive["opp_efg_pct"] = (
    (
        defensive["opp_fgm"]
        + 0.5 * defensive["opp_3pm"]
    )
    / defensive["opp_fga"] * 100
)

# Opponent Turnover Rate (turnovers forced)
defensive["forced_tov_pct"] = (
    defensive["forced_tov"]
    / (
        defensive["opp_fga"]
        + 0.44 * defensive["opp_fta"]
        + defensive["forced_tov"]
    ) * 100
)

# Opponent Offensive Rebounding Percentage
defensive["opp_oreb_pct"] = (
    defensive["opp_oreb"]
    / (
        defensive["opp_oreb"]
        + defensive["team_dreb"]
    ) * 100
)

# Opponent Free Throw Attempt Rate
defensive["opp_ft_rate"] = (
    defensive["opp_fta"]
    / defensive["opp_fga"]
)

# STEP 8: Rank all 15 teams

# Lower is better for these categories
for metric in [
    "opp_efg_pct",
    "opp_oreb_pct",
    "opp_ft_rate"
]:
    defensive[f"{metric}_rank"] = (
        defensive[metric]
        .rank(ascending=True, method="min")
        .astype(int)
    )

# Higher forced turnover rate is better
defensive["forced_tov_rank"] = (
    defensive["forced_tov_pct"]
    .rank(ascending=False, method="min")
    .astype(int)
)

# STEP 9: Display league rankings
display_cols = [
    "team_name",
    "opp_efg_pct",
    "opp_efg_pct_rank",
    "forced_tov_pct",
    "forced_tov_rank",
    "opp_oreb_pct",
    "opp_oreb_pct_rank",
    "opp_ft_rate",
    "opp_ft_rate_rank"
]

defensive = defensive.sort_values(
    "opp_efg_pct_rank"
)

print("\n2026 WNBA DEFENSIVE FOUR FACTORS")
print(
    defensive[display_cols]
    .round(3)
    .to_string(index=False)
)

# STEP 10: Isolate the Liberty
liberty = defensive[
    defensive["team_name"] == "Liberty"
]

if len(liberty) != 1:
    raise ValueError("Expected one Liberty team record.")

print("\nNEW YORK LIBERTY DEFENSIVE PROFILE")
print(
    liberty[display_cols]
    .round(3)
    .to_string(index=False)
)

# STEP 11: League medians
print("\nLEAGUE MEDIANS")
for metric in [
    "opp_efg_pct",
    "forced_tov_pct",
    "opp_oreb_pct",
    "opp_ft_rate"
]:
    print(
        f"{metric}: "
        f"{defensive[metric].median():.3f}"
    )

# STEP 12: Save our results
output = (
    data_folder / "wnba_2026_defensive_four_factors.csv"
)

defensive.to_csv(output, index=False)

print("\nDefensive Four Factors analysis completed!")
print("Saved:", output.name)
