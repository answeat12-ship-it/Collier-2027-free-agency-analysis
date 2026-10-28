from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Listed 2027 contracts from Her Hoop Stats
contracts = {
    "Kayla McBride": 1249500,
    "Courtney Williams": 1249500,
    "Natasha Howard": 735000,
    "Olivia Miles": 485590,
    "Nia Brodie": 367500,
    "Anastasiia Olairi Kosu": 305250
}

assert len(contracts) == 6
assert sum(contracts.values()) == 4392340

# STEP 2: Match our previous cap assumptions
cap_levels = [7000000, 7500000, 7910000]

minimum_roster = 12
minimum_salary = 280800

salary_tiers = {
    "Standard max": 0.17,
    "Potential supermax": 0.20
}

records = []

# STEP 3: Test Collier's return to Minnesota
for cap in cap_levels:

    for tier, rate in salary_tiers.items():

        collier_salary = cap * rate

        player_count = len(contracts) + 1

        open_slots = minimum_roster - player_count

        minimum_depth_cost = (
            open_slots * minimum_salary
        )

        estimated_total = (
            sum(contracts.values())
            + collier_salary
            + minimum_depth_cost
        )

        remaining = cap - estimated_total

        records.append({
            "cap_assumption": cap,
            "salary_tier": tier,
            "existing_commitments": sum(contracts.values()),
            "collier_salary": collier_salary,
            "open_roster_slots": open_slots,
            "minimum_depth_cost": minimum_depth_cost,
            "estimated_total": estimated_total,
            "cap_remaining": remaining,
            "fits_model": remaining >= 0
        })

# STEP 4: Validate results
results = pd.DataFrame(records)

assert len(results) == 6
assert results["open_roster_slots"].eq(5).all()

# STEP 5: Print salary scenarios
print("\nMINNESOTA 2027 COLLIER CAP SCENARIOS")

print(
    results[
        [
            "cap_assumption",
            "salary_tier",
            "collier_salary",
            "estimated_total",
            "cap_remaining",
            "fits_model"
        ]
    ].to_string(index=False)
)

# STEP 6: Compare the contract tiers
print("\nCOLLIER SALARY DIFFERENTIAL")

for cap in cap_levels:
    standard = cap * 0.17
    supermax = cap * 0.20

    print(
        f"Cap ${cap:,.0f}: "
        f"potential extra salary ${supermax-standard:,.0f}"
    )

# STEP 7: Save
output = (
    data_folder / "minnesota_2027_cap_scenarios.csv"
)

results.to_csv(output, index=False)

print("\nSaved:", output.name)
print("Minnesota cap analysis completed!")

