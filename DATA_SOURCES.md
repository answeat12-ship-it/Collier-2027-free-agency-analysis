# Data Sources & Reproducibility

## Overview

This project examines Napheesa Collier's potential
2027 WNBA free-agency destinations using historical
basketball statistics, financial scenarios, and
evidence-informed scouting evaluations.

## Original Data Provider

**Downloaded from:** SportsDataverse

**Underlying statistical source:** ESPN WNBA data

**Relevant resources:**
- https://github.com/sportsdataverse/wehoop
- https://github.com/sportsdataverse/wehoop-wnba-data

The original basketball datasets were downloaded
from SportsDataverse and saved locally as CSV files.

## Source Datasets

| Local Filename | Description |
|---|---|
| `wnba_schedule_2026.csv` | 2026 WNBA game schedule, team matchups, game IDs, results, and season information |
| `team_box_2026.csv` | Team-level box-score statistics for 2026 games |
| `player_box_2025.csv` | Individual player game statistics for the 2025 season |
| `player_box_2026.csv` | Individual player game statistics for the 2026 season |

These filenames represent the project's local
working copies.

## Derived Datasets

Examples include:

- `wnba_2026_standings_calculated.csv`
- `wnba_2026_efficiency_estimates.csv`
- `wnba_2026_four_factors.csv`
- `collier_2027_destination_comparison.csv`
- `collier_2027_fit_evaluations.csv`
- `collier_2027_weighted_fit_scores.csv`
- `collier_2027_sensitivity_results.csv`

These datasets were generated or assembled during
the project's analysis and evaluation process.

## Processing and Analysis

The analytical workflow includes:

1. Load the SportsDataverse basketball datasets.
2. Identify official regular-season games.
3. Validate game identifiers and team records.
4. Calculate team performance and efficiency metrics.
5. Examine player production and team roster fit.
6. Model hypothetical 2027 salary-cap scenarios.
7. Evaluate four possible Collier destinations.
8. Calculate weighted destination-fit scores.
9. Test alternative category-weighting scenarios.
10. Generate visualizations and scouting conclusions.

## Reproducibility

Selected derived datasets and analysis scripts are
available in this repository.

The original SportsDataverse source datasets are
currently excluded from version control.

To reproduce the complete upstream statistical
analysis, users must obtain corresponding source
data and place the required CSV files in the
project's `data/` directory.

Dataset availability, updates, column schemas,
and historical revisions may affect reproducibility.

The original downloaded dataset versions have not
yet been pinned with release identifiers or hashes.

## Analytical Limitations

- Historical statistics do not guarantee future results.
- Estimated possession-based ratings are not official
  league efficiency statistics.
- The 2027 salary-cap scenarios are hypothetical.
- Scouting grades include qualitative judgment.
- Alternative category weights may change rankings.
- The model does not predict Collier's personal decision.

## Attribution

Basketball source data: SportsDataverse / wehoop,
using ESPN-derived WNBA statistics.

Statistical modeling, scouting assessments,
financial scenarios, and visualizations:
project author.