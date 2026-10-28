from pathlib import Path
import pandas as pd
import numpy as np


# Step 1: Load datasets
data_folder = Path(__file__).resolve().parent / "data"

schedule = pd.read_csv(
    data_folder / "wnba_schedule_2026.csv"
)

liberty = pd.read_csv(
    data_folder / "ny_liberty_2026_games.csv"
)

# Step 2: Clean league wide regular-season data
regular = schedule[
    (pd.to_numeric(schedule["season"], errors="coerce") == 2026)
    & (pd.to_numeric(schedule['season_type'], errors="coerce") == 2)
].copy()

regular["home_score"] = pd.to_numeric(
    regular["home_score"], errors="coerce"
)

regular["away_score"] = pd.to_numeric(
    regular["away_score"], errors="coerce"
)

regular = regular[
    (regular["home_score"] > 0)
    & (regular["away_score"] > 0)
].copy()

# Exclude Commissioner's Cup championship
regular = regular[
    regular["game_id"].astype(str) != "401857321"
].copy()

# Exclude All-Star and other non-franchise games
valid_teams = {
    "Atlanta Dream",
    "Chicago Sky",
    "Connecticut Sun",
    "Dallas Wings",
    "Golden State Valkyries",
    "Indiana Fever",
    "Las Vegas Aces",
    "Los Angeles Sparks",
    "Minnesota Lynx",
    "New York Liberty",
    "Phoenix Mercury",
    "Portland Fire",
    "Seattle Storm",
    "Toronto Tempo",
    "Washington Mystics"
}

# Both teams must be recognized WNBA franchises
valid_matchups = (
    regular["home_display_name"].isin(valid_teams)
    & regular["away_display_name"].isin(valid_teams)
)

excluded_games = regular.loc[~valid_matchups]

print("\nNON-FRANCHISE GAMES EXCLUDED:")
print(
    excluded_games[
        [
            "game_id",
            "home_display_name",
            "away_display_name"
        ]
    ].to_string(index=False)
)

regular = regular.loc[valid_matchups].copy()

# Validate the expected league schedule
assert len(regular) == 330, (
    f"Expected 330 games, found {len(regular)}"
)

print("\nLeague games analyzed:", len(regular))


# Step 3: Build a row for each team's game
home_games = pd.DataFrame({
    "team": regular["home_display_name"],
    "points_for": regular["home_score"],
    "points_against": regular["away_score"]
})

away_games = pd.DataFrame({
    "team": regular["away_display_name"],
    "points_for": regular["away_score"],
    "points_against": regular["home_score"]
})

team_games = pd.concat(
    [home_games, away_games],
    ignore_index=True
)

team_games["win"] = (
    team_games["points_for"] > team_games["points_against"]
).astype(int)

# Step 4: Calculate each team's season record
standings = team_games.groupby("team").agg(
    wins=("win", "sum"),
    games=("win", "count")
).reset_index()

standings["losses"] = (
    standings["games"] - standings["wins"]
)

standings["win_pct"] = (
    standings["wins"] / standings["games"]
)

standings = standings.sort_values(
    "win_pct", ascending=False
)

print("\n2026 WNBA STANDINGS")
print(standings.to_string(index=False))

# Step 5: Attach opponent strength to Liberty Games
opponent_records = standings[
    ["team", "win_pct"]
].rename(columns={
    "team": "opponent",
    "win_pct": "opponent_win_pct"
})

liberty = liberty.merge(
    opponent_records,
    on="opponent",
    how="left",
    validate="many_to_one"
)

if liberty["opponent_win_pct"].isna().any():
    raise ValueError("Some opponents have no matching record.")


# Step 6: Categorize opponents by final win percentage
liberty["opponent_group"] = np.where(
    liberty["opponent_win_pct"] >= 0.500,
    ".500 or above",
    "Below .500"
)

# Step 7: Compare Liberty performance by opponent group
liberty["win"] = (
    liberty["result"] == "W"
).astype(int)

comparison = liberty.groupby(
    "opponent_group"
).agg(
    games=("win", "count"),
    wins=("win", "sum"),
    avg_margin=("point_margin", "mean"),
    avg_points=("liberty_score", "mean")
).reset_index()

comparison["losses"] = (
    comparison["games"] - comparison["wins"]
)

print("\nLIBERTY PERFORMANCE BY OPPONENT STRENGTH")
print(comparison.to_string(index=False))


# Step 8: Identify losses against below .500 opponents
unexpected_losses = liberty[
    (liberty["opponent_group"] == "Below .500")
    & (liberty["result"] == "L")
]

print("\nLOSSES AGAINST BELOW .500 OPPONENTS")
print(
    unexpected_losses[
        ["date", "opponent", "point_margin"]
    ].to_string(index=False)
)


# Step 9: Save results
standings.to_csv(
    data_folder / "wnba_2026_standings_calculated.csv",
    index=False
)

liberty.to_csv(
    data_folder / "ny_liberty_2026_opponent_strength.csv",
    index=False
)

print("\nOpponent strength analysis completed!")
