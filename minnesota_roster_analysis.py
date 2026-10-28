from pathlib import Path
import pandas as pd

# STEP 1: Load our existing datasets
data_folder = Path(__file__).resolve().parent / "data"

players = pd.read_csv(
    data_folder / "player_box_2026.csv",
    dtype={"game_id": str, "team_id": str}
)

schedule = pd.read_csv(
    data_folder / "wnba_schedule_2026.csv",
    dtype={"game_id": str}
)

standings = pd.read_csv(
    data_folder / "wnba_2026_standings_calculated.csv"
)

# STEP 2: Select valid 2026 regular-season games
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

# STEP 3: Identify Minnesota's games
team_name = "Minnesota Lynx"

home = regular["home_display_name"] == team_name
away = regular["away_display_name"] == team_name

lynx_games = regular[home | away].copy()

print("\nMINNESOTA REGULAR-SEASON GAMES:")
print(len(lynx_games))

assert len(lynx_games) == 44

# STEP 4: Identify Minnesota's ESPN team ID
team_ids = (
    set(regular.loc[home, "home_id"].astype(str))
    | set(regular.loc[away, "away_id"].astype(str))
)

team_ids = {
    team_id.removesuffix(".0")
    for team_id in team_ids
}

print("\nMINNESOTA ESPN TEAM ID:")
print(team_ids)

assert len(team_ids) == 1

# STEP 5: Match Minnesota's player box scores
players["team_id"] = (
    players["team_id"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
)

lynx = players[
    players["game_id"].isin(lynx_games["game_id"])
    & players["team_id"].isin(team_ids)
].copy()

assert not lynx.empty

# STEP 6: Convert player statistics
stats = [
    "minutes",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "field_goals_attempted",
    "three_point_field_goals_made",
    "three_point_field_goals_attempted",
    "free_throws_attempted"
]

for col in stats:
    lynx[col] = pd.to_numeric(
        lynx[col], errors="coerce"
    )

# Exclude DNPs
played = lynx[
    lynx["minutes"].notna()
    & (lynx["minutes"] > 0)
].copy()

assert not played.duplicated(
    ["game_id", "athlete_display_name"]
).any()

if played[stats].isna().any().any():
    raise ValueError("Missing player statistics.")

# STEP 7: Aggregate the roster
roster = played.groupby(
    "athlete_display_name"
).agg(
    games=("game_id", "nunique"),
    minutes=("minutes", "sum"),
    points=("points", "sum"),
    rebounds=("rebounds", "sum"),
    assists=("assists", "sum"),
    steals=("steals", "sum"),
    blocks=("blocks", "sum"),
    turnovers=("turnovers", "sum"),
    fga=("field_goals_attempted", "sum"),
    three_pm=("three_point_field_goals_made", "sum"),
    three_pa=("three_point_field_goals_attempted", "sum"),
    fta=("free_throws_attempted", "sum")
).reset_index()

roster["mpg"] = roster["minutes"] / roster["games"]
roster["ppg"] = roster["points"] / roster["games"]
roster["rpg"] = roster["rebounds"] / roster["games"]
roster["apg"] = roster["assists"] / roster["games"]

roster["ts_pct"] = (
    100 * roster["points"]
    / (2 * (roster["fga"] + 0.44 * roster["fta"]))
)

roster["three_pct"] = (
    100 * roster["three_pm"]
    / roster["three_pa"].replace(0, float("nan"))
)

roster = roster.sort_values(
    "minutes", ascending=False
)

# STEP 8: Check Collier's appearances
collier = roster[
    roster["athlete_display_name"] == "Napheesa Collier"
]

assert len(collier) == 1
assert int(collier.iloc[0]["games"]) == 16

# STEP 9: Display the roster
columns = [
    "athlete_display_name",
    "games",
    "mpg",
    "ppg",
    "rpg",
    "apg",
    "ts_pct",
    "three_pct"
]

print("\nMINNESOTA 2026 PRIMARY CONTRIBUTORS")
print(
    roster[columns]
    .round(2)
    .to_string(index=False)
)

# STEP 10: Save our analysis
output = (
    data_folder / "minnesota_2026_roster_profile.csv"
)

roster.to_csv(output, index=False)

print("\nSaved:", output.name)
print("Minnesota roster analysis completed!")