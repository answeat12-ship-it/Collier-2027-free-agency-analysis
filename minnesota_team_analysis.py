from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent / "data"

# STEP 1: Load existing league-wide datasets
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

# STEP 2: Merge our validated team metrics
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

# ESPN uses the short team name.
minnesota = profile[
    profile["team_name"] == "Lynx"
].copy()

assert len(minnesota) == 1

# STEP 4: Display Minnesota's ranking profile
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

print("\nMINNESOTA LYNX 2026 TEAM PROFILE")

print(
    minnesota[rank_columns]
    .round(2)
    .to_string(index=False)
)

# STEP 5: Compare with league medians
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
    "minnesota": [
        minnesota.iloc[0][metric]
        for metric in metrics
    ],
    "league_median": [
        profile[metric].median()
        for metric in metrics
    ]
})

comparison["difference"] = (
    comparison["minnesota"]
    - comparison["league_median"]
)

print("\nMINNESOTA VS LEAGUE MEDIAN")
print(
    comparison.round(2).to_string(index=False)
)

# STEP 6: Save our results
minnesota.to_csv(
    data_folder / "minnesota_2026_team_profile.csv",
    index=False
)

comparison.to_csv(
    data_folder / "minnesota_2026_league_comparison.csv",
    index=False
)

print("\nMinnesota team analysis completed!")