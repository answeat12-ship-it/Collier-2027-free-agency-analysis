from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Load league performance
efficiency = pd.read_csv(
    data_folder / "wnba_2026_efficiency_estimates.csv"
)

# STEP 2: Define our four destinations
teams = {
    "New York Liberty": "Liberty",
    "Toronto Tempo": "Tempo",
    "Golden State Valkyries": "Valkyries",
    "Minnesota Lynx": "Lynx"
}

# STEP 3: Load each team's cap scenario
cap_files = {
    "New York Liberty": "liberty_2027_cap_scenarios.csv",
    "Toronto Tempo": "toronto_2027_cap_scenarios.csv",
    "Golden State Valkyries": "golden_state_2027_cap_scenarios.csv",
    "Minnesota Lynx": "minnesota_2027_cap_scenarios.csv"
}

records = []

for destination, short_name in teams.items():

    # Find the corresponding performance record
    team = efficiency[
        efficiency["team_name"] == short_name
    ]

    assert len(team) == 1, destination
    team = team.iloc[0]

    # Load the financial model
    cap = pd.read_csv(
        data_folder / cap_files[destination]
    )

    cap = cap[
        cap["cap_assumption"] == 7910000
    ].copy()

    # Use standard-max signing for consistency
    if destination == "New York Liberty":
        cap = cap[
            (cap["scenario"] == "Add Collier")
            & (cap["collier_salary_tier"] == "Standard max")
        ]

    elif destination == "Minnesota Lynx":
        cap = cap[
            cap["salary_tier"] == "Standard max"
        ]

    assert len(cap) == 1, destination
    cap = cap.iloc[0]

    records.append({
        "destination": destination,
        "offensive_rating": team["offensive_rating"],
        "offense_rank": team["offense_rank"],
        "defensive_rating": team["defensive_rating"],
        "defense_rank": team["defense_rank"],
        "net_rating": team["net_rating"],
        "net_rank": team["net_rank"],
        "modeled_cap_remaining": cap["cap_remaining"],
        "financial_model_fits": bool(cap["cap_remaining"] >=0)
    })

# STEP 4: Create our comparison
comparison = pd.DataFrame(records)

comparison = comparison.sort_values(
    "net_rank"
)

print("\nCOLLIER 2027 DESTINATION COMPARISON")

print(
    comparison.round(2).to_string(index=False)
)

# STEP 5: Display Minnesota supermax separately
minnesota_cap = pd.read_csv(
    data_folder / "minnesota_2027_cap_scenarios.csv"
)

supermax = minnesota_cap[
    (minnesota_cap["cap_assumption"] == 7910000)
    & (
        minnesota_cap["salary_tier"]
        == "Potential supermax"
    )
]

assert len(supermax) == 1

print("\nMINNESOTA POTENTIAL SUPERMAX CASE")
print(
    supermax[
        [
            "collier_salary",
            "cap_remaining",
            "fits_model"
        ]
    ].to_string(index=False)
)

# STEP 6: Save
output = (
    data_folder / "collier_2027_destination_comparison.csv"
)

comparison.to_csv(output, index=False)

print("\nSaved:", output.name)
print("Four-team comparison completed!")

