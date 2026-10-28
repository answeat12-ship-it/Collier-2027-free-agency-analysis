from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# 2027 commitments from Her Hoop Stats
contracts = {
    "Marina Mabrey": 1200000,
    "Brittney Sykes": 1190000,
    "Julie Allemand": 425000,
    "Kiki Rice": 369260,
    "Aneesah Morrow": 364720,
    "Teonni Key": 288600
}

# Hypothetical cap levels, not finalized cap figures
cap_levels = [7000000, 7500000, 7910000]

minimum_roster = 12
minimum_salary = 280800
standard_max_rate = 0.17

records = []

for cap in cap_levels:

    # Collier signs as the seventh roster player
    player_count = len(contracts) + 1

    open_slots = minimum_roster - player_count
    depth_cost = open_slots * minimum_salary

    collier_salary = cap * standard_max_rate

    projected_total = (
        sum(contracts.values())
        + collier_salary
        + depth_cost
    )

    remaining = cap - projected_total

    records.append({
        "cap_assumption": cap,
        "committed_salary": sum(contracts.values()),
        "collier_standard_max": collier_salary,
        "open_roster_slots": open_slots,
        "minimum_depth_cost": depth_cost,
        "projected_total": projected_total,
        "cap_remaining": remaining,
        "fits_model": remaining >= 0
    })

results = pd.DataFrame(records)

print("\nTORONTO 2027 COLLIER CAP SCENARIOS")
print(results.to_string(index=False))

results.to_csv(
    data_folder / "toronto_2027_cap_scenarios.csv",
    index=False
)

print("\nToronto financial scenarios completed!")

