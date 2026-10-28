from pathlib import Path
import ast
import pandas as pd
import re

# STEP 1: Load existing datasets
data_folder = Path(__file__).resolve().parent / "data"

schedule = pd.read_csv(
    data_folder / "wnba_schedule_2026.csv",
    dtype={"game_id": str}
)

liberty = pd.read_csv(
    data_folder / "ny_liberty_2026_games.csv",
    dtype={"game_id": str}
)

# STEP 2: Attach quarter scores to Liberty games
quarter_data = schedule[
    ["game_id", "home_linescores", "away_linescores"]
].copy()

games = liberty.merge(
    quarter_data,
    on="game_id",
    how="left",
    validate="one_to_one"
)

# STEP 3: Convert the stored text into Python data
def parse_quarters(value):
    if pd.isna(value):
        return {}

    # Insert missing commas between quarter dictionaries
    cleaned_value = re.sub(
        r"}\s*{",
        "}, {",
        value
    )

    try:
        periods = ast.literal_eval(cleaned_value)

    except (SyntaxError, ValueError) as error:
        print("\nQUARTER DATA PARSING ERROR")
        print("Error:", error)
        print("Original value:", repr(value))
        print("Cleaned value:", repr(cleaned_value))
        raise

    return {
        int(item["period"]): float(item["value"])
        for item in periods
    }



# STEP 4: Calculate game-control metrics
records = []

for _, game in games.iterrows():

    print(
        f"\nChecking game {game['game_id']}"
        f"against {game['opponent']}"
    )

    home_quarters = parse_quarters(game["home_linescores"])
    away_quarters = parse_quarters(game["away_linescores"])

    is_home = str(game["is_home"]).lower() == "true"

    ny_quarters = home_quarters if is_home else away_quarters
    opp_quarters = away_quarters if is_home else home_quarters

    # Check for missing quarter data
    if not all(
        q in ny_quarters and q in opp_quarters
        for q in range(1, 5)
    ):
        raise ValueError(
            f"Missing quarter scores for game {game['game_id']}"
        )

    # Verify quarter totals match the final score
    assert sum(ny_quarters.values()) == game["liberty_score"]
    assert sum(opp_quarters.values()) == game["opponent_score"]

    halftime_margin = sum(
        ny_quarters[q] - opp_quarters[q]
        for q in [1, 2]
    )

    margin_after_q3 = sum(
        ny_quarters[q] - opp_quarters[q]
        for q in [1, 2, 3]
    )

    q4_margin = ny_quarters[4] - opp_quarters[4]

    # Lost after entering Q4 with a lead
    blown_q4_lead = (
        margin_after_q3 > 0
        and game["result"] == "L"
    )

    records.append({
        "game_id": game["game_id"],
        "date": game["date"],
        "opponent": game["opponent"],
        "result": game["result"],
        "final_margin": game["point_margin"],
        "halftime_margin": halftime_margin,
        "margin_after_q3": margin_after_q3,
        "ny_q4_points": ny_quarters[4],
        "opponent_q4_points": opp_quarters[4],
        "q4_margin": q4_margin,
        "blown_q4_lead": blown_q4_lead
    })

# STEP 5: Create analysis DataFrame
game_control = pd.DataFrame(records)

# STEP 6: Analyze fourth-quarter performance
print("\nLIBERTY FOURTH-QUARTER ANALYSIS")

print(
    "Average Q4 scoring margin:",
    round(game_control["q4_margin"].mean(), 2)
)

print(
    "Games entering Q4 with a lead:",
    (game_control["margin_after_q3"] > 0).sum()
)

print(
    "Losses after leading through Q3:",
    game_control["blown_q4_lead"].sum()
)

# STEP 7: Display games with surrendered leads
blown_leads = game_control[
    game_control["blown_q4_lead"]
].copy()

print("\nLOSSES AFTER LEADING ENTERING Q4")
print(
    blown_leads[
        [
            "date",
            "opponent",
            "margin_after_q3",
            "q4_margin",
            "final_margin"
        ]
    ].to_string(index=False)
)

# STEP 8: Save our results
output = data_folder / "ny_liberty_2026_game_control.csv"

game_control.to_csv(output, index=False)

print("\nSaved:", output.name)
