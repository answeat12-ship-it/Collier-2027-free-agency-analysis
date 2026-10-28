from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# Reported 2027 cap hits: Her Hoop Stats
contracts = {
    "Sabrina Ionescu": 1249500,
    "Breanna Stewart": 1249500,
    "Jonquel Jones": 1249500,
    "Satou Sabally": 855750,
    "Leonie Fiebich": 331666,
    "Marine Fauthoux": 288600
}

# CBA minimum roster and salary assumptions
minimum_roster = 12
minimum_salary = 280800

# Illustrative cap levels, NOT official projections
cap_levels = [7000000, 7500000, 7910000]

scenarios = {
    "No Collier": {
        "remove": [],
        "add_collier": False
    },
    "Add Collier": {
        "remove": [],
        "add_collier": True
    },
    "Replace Sabally": {
        "remove": ["Satou Sabally"],
        "add_collier": True
    },
    "Replace Jones": {
        "remove": ["Jonquel Jones"],
        "add_collier": True
    }
}

records = []

for cap in cap_levels:
    for scenario_name, scenario in scenarios.items():

        retained = {
            name: salary
            for name, salary in contracts.items()
            if name not in scenario["remove"]
        }

        existing_salary = sum(retained.values())

        # Test standard maximum and supermaximum
        tiers = (
            {"None": 0}
            if not scenario["add_collier"]
            else {
                "Standard max": 0.17,
                "Supermax": 0.20
            }
        )

        for tier_name, rate in tiers.items():

            collier_salary = cap * rate

            player_count = (
                len(retained)
                + int(scenario["add_collier"])
            )

            minimum_slots = max(
                0, minimum_roster - player_count
            )

            minimum_cost = (
                minimum_slots * minimum_salary
            )

            estimated_total = (
                existing_salary
                + collier_salary
                + minimum_cost
            )

            cap_remaining = cap - estimated_total

            records.append({
                "cap_assumption": cap,
                "scenario": scenario_name,
                "collier_salary_tier": tier_name,
                "contracted_players": player_count,
                "minimum_slots": minimum_slots,
                "collier_salary": collier_salary,
                "minimum_roster_cost": minimum_cost,
                "estimated_total": estimated_total,
                "cap_remaining": cap_remaining,
                "fits_cap_floor_model": (
                    cap_remaining >= 0
                )
            })

results = pd.DataFrame(records)

print("\n2027 LIBERTY SALARY CAP SCENARIOS")
print(results.to_string(index=False))

# Focus on the highest possible cap assumption
upper_limit = results[
    results["cap_assumption"] == 7910000
]

print("\nAT THE $7.91M CAP CEILING")
print(
    upper_limit[
        [
            "scenario",
            "collier_salary_tier",
            "estimated_total",
            "cap_remaining",
            "fits_cap_floor_model"
        ]
    ].to_string(index=False)
)

output = (
    data_folder / "liberty_2027_cap_scenarios.csv"
)

results.to_csv(output, index=False)

print("\nSaved:", output.name)

# STEP 24: Maximum theoretical Collier offer
# while retaining all six listed players

cap_ceiling = 7_910_000

current_commitments = sum(contracts.values())

# Six current players + Collier = seven.
# Five more players needed for a 12-player roster.
remaining_slots = minimum_roster - len(contracts) - 1

minimum_depth_cost = (
    remaining_slots * minimum_salary
)

collier_budget = (
    cap_ceiling
    - current_commitments
    - minimum_depth_cost
)

standard_max = cap_ceiling * 0.17

print("\nCOLLIER DIRECT-SIGNING BUDGET")
print(f"2027 cap ceiling: ${cap_ceiling:,.0f}")
print(f"Existing commitments: ${current_commitments:,.0f}")
print(f"Minimum depth cost: ${minimum_depth_cost:,.0f}")
print(f"Available for Collier: ${collier_budget:,.0f}")
print(f"Standard maximum: ${standard_max:,.0f}")

print(
    "Shortfall against standard max:",
    f"${standard_max - collier_budget:,.0f}"
)

