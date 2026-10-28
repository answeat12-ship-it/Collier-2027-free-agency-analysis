from pathlib import Path
import pandas as pd

# STEP 1: Locate our existing datasets
data_folder = Path(__file__).resolve().parent / "data"

efficiency = pd.read_csv(
    data_folder / "wnba_2026_efficiency_estimates.csv"
)

offense = pd.read_csv(
    data_folder / "wnba_2026_four_factors.csv"
)

defense = pd.read_csv(
    data_folder / "wnba_2026_defensive_four_factors.csv"
)

turnovers = pd.read_csv(
    data_folder / "wnba_2026_turnover_comparison.csv"
)

# STEP 2: Combine our league results
profile = efficiency.merge(
    offense[
        [
            "team_name",
            "efg_pct",
            "efg_pct_rank",
            "tov_pct",
            "tov_rank",
            "oreb_pct",
            "oreb_pct_rank"
        ]
    ],
    on="team_name",
    validate="one_to_one"
)

profile = profile.merge(
    defense[
        [
            "team_name",
            "opp_efg_pct",
            "opp_efg_pct_rank",
            "forced_tov_pct",
            "forced_tov_rank",
            "opp_oreb_pct",
            "opp_oreb_pct_rank"
        ]
    ],
    on="team_name",
    validate="one_to_one"
)

profile = profile.merge(
    turnovers[
        [
            "team_name",
            "tov_rate_margin",
            "margin_rank"
        ]
    ],
    on="team_name",
    validate="one_to_one"
)

# STEP 3: Validate all 15 franchises
assert len(profile) == 15
assert profile["team_name"].is_unique

# STEP 4: Select Toronto
toronto = profile[
    profile["team_name"] == "Tempo"
].copy()

assert len(toronto) == 1

# STEP 5: Display Toronto's evaluation
columns = [
    "team_name",
    "offensive_rating",
    "offense_rank",
    "defensive_rating",
    "defense_rank",
    "net_rating",
    "net_rank",
    "efg_pct",
    "efg_pct_rank",
    "tov_pct",
    "tov_rank",
    "opp_efg_pct",
    "opp_efg_pct_rank",
    "forced_tov_pct",
    "forced_tov_rank",
    "opp_oreb_pct",
    "opp_oreb_pct_rank",
    "tov_rate_margin",
    "margin_rank"
]

print("\nTORONTO TEMPO 2026 TEAM PROFILE")
print(
    toronto[columns]
    .round(2)
    .to_string(index=False)
)

# STEP 6: Compare Toronto with league medians
metrics = [
    "offensive_rating",
    "defensive_rating",
    "net_rating",
    "efg_pct",
    "tov_pct",
    "opp_efg_pct",
    "forced_tov_pct",
    "opp_oreb_pct"
]

comparison = pd.DataFrame({
    "metric": metrics,
    "toronto": [
        toronto.iloc[0][metric]
        for metric in metrics
    ],
    "league_median": [
        profile[metric].median()
        for metric in metrics
    ]
})

comparison["difference"] = (
    comparison["toronto"]
    - comparison["league_median"]
)

print("\nTORONTO VS LEAGUE MEDIAN")
print(
    comparison.round(2).to_string(index=False)
)

# STEP 7: Save our Toronto assessment
toronto.to_csv(
    data_folder / "toronto_2026_team_profile.csv",
    index=False
)

comparison.to_csv(
    data_folder / "toronto_2026_league_comparison.csv",
    index=False
)

print("\nToronto team analysis completed!")