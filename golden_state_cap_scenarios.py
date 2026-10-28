from pathlib import Path
import pandas as pd

# STEP 1: Locate our data folder
data_folder = Path(__file__).resolve().parent / "data"

# STEP 2: 2027 cap hits from Her Hoop Stats
contracts = {
    "Gabby Williams": 1249500,
    "Veronica Burton": 971250,
    "Kaila Charles": 615000,
    "Janelle Salaun": 520000,
    "Iliana Rupert": 472500,
    "Juste Jocyte": 395428,
    "Kiah Stokes": 386250
}

assert len(contracts) == 7
assert sum(contracts.values()) == 4609928

# STEP 3: Keep assumptions consistent
# with our other destination analyses
cap_levels = [7000000, 7500000, 7910000]

minimum_roster = 12
minimum_salary = 280800
standard_max_rate = 0.17

records = []

# STEP 4: Calculate the salary scenarios
for cap in cap_levels:

    existing_salary = sum(contracts.values())

    collier_salary = cap * standard_max_rate

    # Seven contracted players plus Collier
    player_count = len(contracts) + 1

    open_slots = minimum_roster - player_count

    minimum_depth_cost = (
        open_slots * minimum_salary
    )

    estimated_total = (
        existing_salary
        + collier_salary
        + minimum_depth_cost
    )

    cap_remaining = cap - estimated_total

    records.append({
        "cap_assumption": cap,
        "existing_commitments": existing_salary,
        "contracted_players": player_count,
        "collier_standard_max": collier_salary,
        "open_roster_slots": open_slots,
        "minimum_depth_cost": minimum_depth_cost,
        "estimated_total": estimated_total,
        "cap_remaining": cap_remaining,
        "fits_model": cap_remaining >= 0
    })

# STEP 5: Validate our results
results = pd.DataFrame(records)

assert len(results) == 3
assert results["contracted_players"].eq(8).all()
assert results["open_roster_slots"].eq(4).all()

# STEP 6: Print a readable comparison
display_cols = [
    "cap_assumption",
    "collier_standard_max",
    "minimum_depth_cost",
    "estimated_total",
    "cap_remaining",
    "fits_model"
]

print("\nGOLDEN STATE 2027 COLLIER CAP SCENARIOS")
print(results[display_cols].to_string(index=False))

# STEP 7: Display financial sensitivity
print("\nREMAINING CAP ROOM BY ASSUMPTION")

for _, row in results.iterrows():
    print(
        f"Cap ${row['cap_assumption']:,.0f}: "
        f"${row['cap_remaining']:,.0f} remaining"
    )

# STEP 8: Save
output = (
    data_folder / "golden_state_2027_cap_scenarios.csv"
)

results.to_csv(output, index=False)

print("\nSaved:", output.name)
print("Golden State cap analysis completed!")

