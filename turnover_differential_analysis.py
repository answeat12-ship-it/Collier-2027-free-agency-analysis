
from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# Load our validated Four Factors results
offense = pd.read_csv(
    data_folder / "wnba_2026_four_factors.csv"
)

defense = pd.read_csv(
    data_folder / "wnba_2026_defensive_four_factors.csv"
)

# STEP 1: Select relevant turnover statistics
offense = offense[
    ["team_name", "tov_pct", "tov_rank"]
].copy()

defense = defense[
    ["team_name", "forced_tov_pct", "forced_tov_rank"]
].copy()

# STEP 2: Combine offense and defense
turnover_profile = offense.merge(
    defense,
    on="team_name",
    how="inner",
    validate="one_to_one"
)

assert len(turnover_profile) == 15

# STEP 3: Calculate the turnover-rate differential
# Positive is better: forcing more than committing
turnover_profile["tov_rate_margin"] = (
    turnover_profile["forced_tov_pct"]
    - turnover_profile["tov_pct"]
)

# STEP 4: Rank all WNBA teams
turnover_profile["margin_rank"] = (
    turnover_profile["tov_rate_margin"]
    .rank(ascending=False, method="min")
    .astype(int)
)

turnover_profile = turnover_profile.sort_values(
    "margin_rank"
)

print("\n2026 WNBA TURNOVER-RATE COMPARISON")
print(
    turnover_profile.round(2).to_string(index=False)
)

# STEP 5: Isolate the Liberty
liberty = turnover_profile[
    turnover_profile["team_name"] == "Liberty"
]

print("\nNEW YORK LIBERTY TURNOVER PROFILE")
print(liberty.round(2).to_string(index=False))

# STEP 6: Compare with the league median
print("\nLEAGUE MEDIAN DIFFERENTIAL:")
print(
    round(turnover_profile["tov_rate_margin"].median(), 2)
)

# STEP 7: Save our analysis
turnover_profile.to_csv(
    data_folder / "wnba_2026_turnover_comparison.csv",
    index=False
)

print("\nTurnover analysis completed!")
