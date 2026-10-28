from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Identify our statistical columns
stats = [
    "minutes",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "field_goals_made",
    "field_goals_attempted",
    "three_point_field_goals_made",
    "three_point_field_goals_attempted",
    "free_throws_made",
    "free_throws_attempted"
]

season_results = []

# STEP 2: Analyze both seasons
for year in [2025, 2026]:

    players = pd.read_csv(
        data_folder / f"player_box_{year}.csv",
        dtype={"game_id": str}
    )

    # Find Collier's records
    collier = players[
        players["athlete_display_name"].eq(
            "Napheesa Collier"
        )
        & (
            pd.to_numeric(
                players["season_type"],
                errors="coerce"
            ) == 2
        )
    ].copy()

    # Convert statistical values to numbers
    for col in stats:
        collier[col] = pd.to_numeric(
            collier[col], errors="coerce"
        )

    # STEP 3: Separate appearances from DNP records
    dnp_records = collier[
        collier["minutes"].isna()
        | (collier["minutes"] <= 0)
    ]

    played = collier[
        collier["minutes"].notna()
        & (collier["minutes"] > 0)
    ].copy()

    # STEP 3B: Exclude verified special-event candidates
    if year == 2025:

        game_dates = pd.to_datetime(
            played["game_date"],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

        special_events = (
            (played["game_id"] == "401736430")
            | game_dates.isin([
                "2025-07-19",
                "2025-07-20"
            ])
        )

        print("\n2025 SPECIAL-EVENT RECORDS:")
        print(
            played.loc[
                special_events,
                ["game_date", "game_id", "points", "minutes"]
            ].to_string(index=False)
        )

        # Stop if the suspected events don't match
        # the two extra appearances.
        assert special_events.sum() == 2, (
            "Expected two special-event records. "
            "Investigate before excluding games."
        )

        played = played.loc[~special_events].copy()

    # Validate the expected game counts
    expected_games = {2025: 33, 2026: 16}

    assert len(played) == expected_games[year], (
        f"{year}: expected {expected_games[year]} "
        f"appearances, found {len(played)}"
    )

    # Check minutes separately
    print(f"\n{year} CLEANED GAMES:", len(played))
    print(
        f"{year} TOTAL MINUTES:",
        round(played["minutes"].sum(), 2)
    )
    print(
        f"{year} MINUTES PER GAME:",
        round(played["minutes"].mean(), 2)
    )


    # Validate our player records
    assert played["game_id"].is_unique

    if played[stats].isna().any().any():
        print(played[stats].isna().sum())
        raise ValueError(
            f"Missing playing statistics in {year}"
        )

    print(f"\n{'=' * 45}")
    print(f"COLLIER {year} DATA VALIDATION")
    print(f"{'=' * 45}")

    print("Regular-season rows:", len(collier))
    print("DNP records:", len(dnp_records))
    print("Games played:", len(played))

    # Expected regular-season appearances
    expected_games = {
        2025: 33,
        2026: 16
    }

    assert len(played) == expected_games[year], (
        f"Unexpected games played in {year}"
    )

    # STEP 4: Calculate season totals
    totals = played[stats].sum()
    games = len(played)

    fgm = totals["field_goals_made"]
    fga = totals["field_goals_attempted"]

    three_pm = totals["three_point_field_goals_made"]
    three_pa = totals["three_point_field_goals_attempted"]

    ftm = totals["free_throws_made"]
    fta = totals["free_throws_attempted"]

    points = totals["points"]
    assists = totals["assists"]
    turnovers = totals["turnovers"]
    minutes = totals["minutes"]

    # STEP 5: Calculate shooting efficiency
    fg_pct = 100 * fgm / fga if fga else 0

    three_pct = (
        100 * three_pm / three_pa
        if three_pa else 0
    )

    ft_pct = 100 * ftm / fta if fta else 0

    ts_pct = (
        100 * points / (2 * (fga + 0.44 * fta))
        if (fga + 0.44 * fta) else 0
    )

    three_point_rate = (
        100 * three_pa / fga
        if fga else 0
    )

    ast_to_ratio = (
        assists / turnovers
        if turnovers else float("nan")
    )

    # STEP 6: Store the season summary
    season_results.append({
        "season": year,
        "games": games,
        "minutes_per_game": minutes / games,
        "points_per_game": points / games,
        "rebounds_per_game": totals["rebounds"] / games,
        "assists_per_game": assists / games,
        "steals_per_game": totals["steals"] / games,
        "blocks_per_game": totals["blocks"] / games,
        "turnovers_per_game": turnovers / games,
        "fg_pct": fg_pct,
        "three_pct": three_pct,
        "ft_pct": ft_pct,
        "ts_pct": ts_pct,
        "three_point_attempt_rate": three_point_rate,
        "assist_turnover_ratio": ast_to_ratio,
        "points_per_36": points / minutes * 36,
        "steals_per_36": totals["steals"] / minutes * 36,
        "blocks_per_36": totals["blocks"] / minutes * 36
    })

# STEP 7: Create the comparison
comparison = pd.DataFrame(season_results)

# Validate that both seasons were saved
print("\nSEASONS INCLUDED:")
print(comparison["season"].tolist())

assert len(comparison) == 2, (
    "Expected two season summary rows."
)

assert set(comparison["season"]) == {2025, 2026}, (
    "Both 2025 and 2026 must be included."
)

# Print a smaller, easier-to-read comparison
summary_columns = [
    "season",
    "games",
    "minutes_per_game",
    "points_per_game",
    "rebounds_per_game",
    "assists_per_game",
    "turnovers_per_game",
    "ts_pct"
]

print("\nCOLLIER SEASON COMPARISON")
print(
    comparison[summary_columns]
    .round(2)
    .to_string(index=False)
)


print("\nCOLLIER TWO-SEASON STATISTICAL PROFILE")
print(
    comparison.round(2).to_string(index=False)
)

# STEP 8: Save results
output = data_folder / "collier_2025_2026_profile.csv"

comparison.to_csv(output, index=False)

print("\nSaved:", output.name)
print("Two-season analysis completed!")

