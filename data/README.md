Data Documentation

Overview

This directory contains derived statistical outputs and scouting evaluations for the Napheesa Collier 2027 WNBA Free Agency Analysis.

The project evaluates Minnesota, Golden State, Toronto, and New York using 2025–2026 player data, 2026 team performance, hypothetical 2027 salary-cap scenarios, and qualitative basketball scouting.

The repository is not yet fully reproducible from a fresh clone. Some source and intermediate datasets are intentionally excluded while their provenance and redistribution permissions are reviewed.

Published Analytical Datasets

File

Description

collier_2027_destination_comparison.csv

Four-team comparison of offensive efficiency, defensive efficiency, net rating, rankings, and modeled cap feasibility

collier_2027_fit_evaluations.csv

Scouting grades and written supporting evidence across five evaluation categories

collier_2027_scoring_weights.csv

Weights assigned to each scouting category

wnba_2026_efficiency_estimates.csv

Derived offensive, defensive, and net efficiency estimates for 15 WNBA teams

wnba_2026_four_factors.csv

Team Four Factors metrics and rankings

Source and Intermediate Data

The Python analyses use additional local files, including:

wnba_schedule_2026.csv — 2026 game schedule

team_box_2026.csv — team box-score data

player_box_2025.csv and player_box_2026.csv — player-level box-score data

wnba_2026_standings_calculated.csv — derived team standings

ny_liberty_2026_opponent_strength.csv — intermediate opponent-strength analysis

Team-specific 2027 salary-cap scenario CSVs

These inputs are not all included in the public repository.

The complete source URLs, extraction procedures, and applicable dataset licenses will be documented before declaring the pipeline fully reproducible.

Statistical Methodology

Team efficiency estimates use game-level box scores and estimated possessions. They should not automatically be treated as identical to official WNBA offensive and defensive ratings.

Additional analyses examine opponent strength, player availability, offensive and defensive Four Factors, roster composition, and team performance trends.

Salary-Cap Modeling

All 2027 salary-cap calculations are hypothetical scenarios, not confirmed contracts or finalized payrolls.

The models use researched contract commitments, assumed cap levels, salary-limit rules, and minimum-roster placeholders.

Actual available cap space may differ because of contract changes, roster decisions, salary rules, and final league figures.

Scouting Evaluations

Five categories contribute to the destination evaluation:

Category

Weight

Basketball Compatibility

25%

Role and Opportunity

25%

Competitive Outlook

20%

Financial Opportunity

15%

Stability and Continuity

15%

Each grade is accompanied by a qualitative scouting explanation.

The grades incorporate statistical evidence and basketball judgment. They are not objective measurements of Collier's personal preferences.

Current status: 19 of 20 scouting grades are complete. Golden State's Competitive Outlook grade remains pending.

Interpretation and Limitations

Statistical results describe historical performance, not guaranteed 2027 outcomes.

Team rosters and contract situations may change.

Injury-disrupted seasons introduce uncertainty into roster projections.

Player chemistry, coaching integration, and role expectations require qualitative assessment.

The final weighted evaluation reflects the project's assumptions and scoring framework, not Collier's stated free-agency preferences.

Reproducibility Status

This repository currently provides selected analysis scripts, derived outputs, dependency requirements, and methodological documentation.

A complete, ordered workflow for regenerating every dataset will be added as source files and intermediate dependencies are documented.

