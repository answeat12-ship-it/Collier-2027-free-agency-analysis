from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Load our datasets
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

# STEP 2: Identify validated regular-season games
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
]

assert len(regular) == 330
assert regular["game_id"].is_unique

# STEP 3: Filter ESPN box scores
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

assert not games[stats].isna().any().any()

# STEP 5: Find opponent defensive rebounds
games["opponent_dreb"] = (
    games.groupby("game_id")["defensive_rebounds"]
    .transform("sum")
    - games["defensive_rebounds"]
)

# STEP 6: Aggregate team statistics
league = games.groupby("team_name").agg(
    fgm=("field_goals_made", "sum"),
    fga=("field_goals_attempted", "sum"),
    three_pm=("three_point_field_goals_made", "sum"),
    fta=("free_throws_attempted", "sum"),
    oreb=("offensive_rebounds", "sum"),
    opponent_dreb=("opponent_dreb", "sum"),
    tov=("total_turnovers", "sum"),
    games=("game_id", "nunique")
).reset_index()

assert len(league) == 15
assert (league["games"] == 44).all()

# STEP 7: Calculate Four Factors
league["efg_pct"] = (
    (league["fgm"] + 0.5 * league["three_pm"])
    / league["fga"] * 100
)

league["tov_pct"] = (
    league["tov"]
    / (league["fga"] + 0.44 * league["fta"] + league["tov"])
    * 100
)

league["oreb_pct"] = (
    league["oreb"]
    / (league["oreb"] + league["opponent_dreb"])
    * 100
)

league["ft_rate"] = league["fta"] / league["fga"]

# STEP 8: Rank the league
# Lower turnovers are better
league["tov_rank"] = (
    league["tov_pct"]
    .rank(ascending=True, method="min")
    .astype(int)
)

# Higher values are generally better
for metric in ["efg_pct", "oreb_pct", "ft_rate"]:
    league[metric + "_rank"] = (
        league[metric]
        .rank(ascending=False, method="min")
        .astype(int)
    )

# STEP 9: Display team comparison
league = league.sort_values("tov_rank")

display_cols = [
    "team_name",
    "efg_pct",
    "efg_pct_rank",
    "tov_pct",
    "tov_rank",
    "oreb_pct",
    "oreb_pct_rank",
    "ft_rate",
    "ft_rate_rank"
]

print("\n2026 WNBA FOUR FACTORS RANKINGS")
print(
    league[display_cols]
    .round(3)
    .to_string(index=False)
)

print("\nNEW YORK LIBERTY FOUR FACTORS")
ny = league[league["team_name"] == "Liberty"]

print(
    ny[display_cols]
    .round(3)
    .to_string(index=False)
)

print("\nLEAGUE MEDIAN TURNOVER RATE:")
print(round(league["tov_pct"].median(), 2))

# STEP 10: Save
league.to_csv(
    data_folder / "wnba_2026_four_factors.csv",
    index=False
)

print("\nLeague Four Factors analysis completed!")
