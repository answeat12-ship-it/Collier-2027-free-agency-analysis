from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Load our existing sources
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

# STEP 2: Reuse our validated league filter
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
]

assert len(regular) == 330

# STEP 3: Isolate Toronto games
home_toronto = regular["home_display_name"] == "Toronto Tempo"
away_toronto = regular["away_display_name"] == "Toronto Tempo"

toronto_games = regular[
    home_toronto | away_toronto
].copy()

print("\nTORONTO REGULAR-SEASON GAMES:")
print(len(toronto_games))

assert len(toronto_games) == 44

# STEP 4: Identify Toronto's ESPN team ID
toronto_ids = set(
    toronto_games.loc[
        home_toronto, "home_id"
    ].astype(str).str.replace(
        r"\.0$", "", regex=True
    )
) | set(
    toronto_games.loc[
        away_toronto, "away_id"
    ].astype(str).str.replace(
        r"\.0$", "", regex=True
    )
)

print("\nTORONTO ESPN TEAM IDS:")
print(toronto_ids)

assert len(toronto_ids) == 1

# STEP 5: Match Toronto player records
players["team_id"] = (
    players["team_id"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
)

toronto = players[
    players["game_id"].isin(toronto_games["game_id"])
    & players["team_id"].isin(toronto_ids)
].copy()

print("\nTORONTO PLAYER RECORDS:")
print(len(toronto))

if toronto.empty:
    print("\nTeam-related player columns:")
    print([
        col for col in players.columns
        if "team" in col.lower()
    ])
    raise ValueError(
        "Toronto team ID did not match player data."
    )

# STEP 6: Remove DNP records
stats = [
    "minutes",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers"
]

for col in stats:
    toronto[col] = pd.to_numeric(
        toronto[col], errors="coerce"
    )

played = toronto[
    toronto["minutes"].notna()
    & (toronto["minutes"] > 0)
].copy()

assert not played.duplicated(
    ["game_id", "athlete_display_name"]
).any()

# STEP 7: Aggregate player contributions
roster = played.groupby(
    "athlete_display_name"
).agg(
    games=("game_id", "nunique"),
    total_minutes=("minutes", "sum"),
    total_points=("points", "sum"),
    total_rebounds=("rebounds", "sum"),
    total_assists=("assists", "sum"),
    total_steals=("steals", "sum"),
    total_blocks=("blocks", "sum"),
    total_turnovers=("turnovers", "sum")
).reset_index()

roster["mpg"] = roster["total_minutes"] / roster["games"]
roster["ppg"] = roster["total_points"] / roster["games"]
roster["rpg"] = roster["total_rebounds"] / roster["games"]
roster["apg"] = roster["total_assists"] / roster["games"]

roster = roster.sort_values(
    "total_minutes",
    ascending=False
)

# STEP 8: Display the roster
print("\nTORONTO 2026 PRIMARY CONTRIBUTORS")

display_cols = [
    "athlete_display_name",
    "games",
    "mpg",
    "ppg",
    "rpg",
    "apg"
]

print(
    roster[display_cols]
    .round(2)
    .to_string(index=False)
)

# STEP 9: Save the results
roster.to_csv(
    data_folder / "toronto_2026_roster_profile.csv",
    index=False
)

print("\nToronto roster analysis completed!")