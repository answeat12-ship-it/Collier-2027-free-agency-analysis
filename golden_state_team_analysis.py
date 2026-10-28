from pathlib import Path
import pandas as pd

# STEP 1: Load our validated league datasets
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

# STEP 2: Combine the key team metrics
profile = efficiency.merge(
    offense[
        [
            "team_name",
            "efg_pct",
            "efg_pct_rank",
            "tov_pct",
            "tov_rank",
            "oreb_pct",
            "oreb_pct_rank",
            "ft_rate",
            "ft_rate_rank"
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
            "opp_oreb_pct_rank",
            "opp_ft_rate",
            "opp_ft_rate_rank"
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

# STEP 3: Validate the league
assert len(profile) == 15
assert profile["team_name"].is_unique

# The ESPN box-score dataset uses the short name.
golden_state = profile[
    profile["team_name"] == "Valkyries"
].copy()

assert len(golden_state) == 1

# STEP 4: Print Golden State's rankings
rank_columns = [
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
    "tov_rate_margin",
    "margin_rank"
]

print("\nGOLDEN STATE VALKYRIES 2026 PROFILE")
print(
    golden_state[rank_columns]
    .round(2)
    .to_string(index=False)
)

# STEP 5: Compare Golden State to league medians
metrics = [
    "offensive_rating",
    "defensive_rating",
    "net_rating",
    "efg_pct",
    "tov_pct",
    "oreb_pct",
    "ft_rate",
    "opp_efg_pct",
    "forced_tov_pct",
    "opp_oreb_pct",
    "opp_ft_rate"
]

comparison = pd.DataFrame({
    "metric": metrics,
    "golden_state": [
        golden_state.iloc[0][metric]
        for metric in metrics
    ],
    "league_median": [
        profile[metric].median()
        for metric in metrics
    ]
})

comparison["difference"] = (
    comparison["golden_state"]
    - comparison["league_median"]
)

print("\nGOLDEN STATE VS LEAGUE MEDIAN")
print(
    comparison.round(2).to_string(index=False)
)

# STEP 6: Save the profiles
golden_state.to_csv(
    data_folder / "golden_state_2026_team_profile.csv",
    index=False
)

comparison.to_csv(
    data_folder / "golden_state_2026_league_comparison.csv",
    index=False
)

print("\nGolden State team analysis completed!")