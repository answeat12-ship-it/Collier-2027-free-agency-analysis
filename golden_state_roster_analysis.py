
from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Load existing datasets
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

# STEP 2: Validate regular-season games
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

# STEP 3: Identify Golden State games
team_name = "Golden State Valkyries"

home = regular["home_display_name"] == team_name
away = regular["away_display_name"] == team_name

gs_games = regular[home | away].copy()

print("\nGOLDEN STATE REGULAR-SEASON GAMES:")
print(len(gs_games))

assert len(gs_games) == 44

# STEP 4: Identify ESPN team ID
gs_ids = (
    set(gs_games.loc[home, "home_id"].astype(str))
    | set(gs_games.loc[away, "away_id"].astype(str))
)

gs_ids = {
    team_id.removesuffix(".0")
    for team_id in gs_ids
}

print("\nGOLDEN STATE ESPN TEAM ID:")
print(gs_ids)

assert len(gs_ids) == 1

# STEP 5: Match player records
players["team_id"] = (
    players["team_id"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
)

gs_players = players[
    players["game_id"].isin(gs_games["game_id"])
    & players["team_id"].isin(gs_ids)
].copy()

if gs_players.empty:
    raise ValueError("No Golden State player records found.")

# STEP 6: Convert statistics
stats = [
    "minutes", "points", "rebounds",
    "assists", "steals", "blocks",
    "turnovers"
]

for col in stats:
    gs_players[col] = pd.to_numeric(
        gs_players[col], errors="coerce"
    )

# Remove did-not-play records
played = gs_players[
    gs_players["minutes"].notna()
    & (gs_players["minutes"] > 0)
].copy()

assert not played.duplicated(
    ["game_id", "athlete_display_name"]
).any()

if played[stats].isna().any().any():
    raise ValueError("Missing game statistics.")

# STEP 7: Calculate player contributions
roster = played.groupby(
    "athlete_display_name"
).agg(
    games=("game_id", "nunique"),
    total_minutes=("minutes", "sum"),
    points=("points", "sum"),
    rebounds=("rebounds", "sum"),
    assists=("assists", "sum"),
    steals=("steals", "sum"),
    blocks=("blocks", "sum"),
    turnovers=("turnovers", "sum")
).reset_index()

for name, column in {
    "mpg": "total_minutes",
    "ppg": "points",
    "rpg": "rebounds",
    "apg": "assists"
}.items():
    roster[name] = roster[column] / roster["games"]

roster = roster.sort_values(
    "total_minutes",
    ascending=False
)

# STEP 8: Display results
print("\nGOLDEN STATE 2026 PRIMARY CONTRIBUTORS")

print(
    roster[
        [
            "athlete_display_name",
            "games",
            "mpg",
            "ppg",
            "rpg",
            "apg"
        ]
    ].round(2).to_string(index=False)
)

# STEP 9: Save
output = (
    data_folder / "golden_state_2026_roster_profile.csv"
)

roster.to_csv(output, index=False)

print("\nGolden State roster analysis completed!")
print("Saved:", output.name)