from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# STEP 1: Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)

# STEP 2: Load sensitivity results
results = pd.read_csv(
    DATA_DIR / "collier_2027_sensitivity_results.csv"
)

scenario_order = [
    "Baseline",
    "Basketball-first",
    "Role-first",
    "Competition-first",
    "Compensation-first",
    "Stability-first",
]

# STEP 3: Validate and reshape the results
if results.duplicated(
    ["scenario", "destination"]
).any():
    raise ValueError(
        "Duplicate scenario-destination combinations."
    )

comparison = results.pivot(
    index="scenario",
    columns="destination",
    values="weighted_score"
)

required_teams = [
    "Minnesota Lynx",
    "Golden State Valkyries"
]

for team in required_teams:
    if team not in comparison.columns:
        raise ValueError(f"Missing team: {team}")

comparison = comparison.reindex(scenario_order)

if comparison[required_teams].isna().any().any():
    raise ValueError("Missing required scenario scores.")

# STEP 4: Calculate the point difference
comparison["margin"] = (
    comparison["Minnesota Lynx"]
    - comparison["Golden State Valkyries"]
)

comparison["leader"] = comparison["margin"].apply(
    lambda value:
    "Minnesota" if value > 0
    else "Golden State" if value < 0
    else "Tie"
)

print("\nSENSITIVITY COMPARISON")
print(
    comparison[
        ["margin", "leader"]
    ].to_string()
)

# STEP 5: Create visualization
fig, ax = plt.subplots(figsize=(12, 7))

colors = [
    "C0" if value >= 0 else "C1"
    for value in comparison["margin"]
]

bars = ax.barh(
    comparison.index,
    comparison["margin"],
    color=colors
)

ax.invert_yaxis()

# Zero separates the two teams' advantages
ax.axvline(
    0,
    color="black",
    linewidth=1.2
)

# STEP 6: Label each result
for bar, value in zip(
    bars,
    comparison["margin"]
):
    y = bar.get_y() + bar.get_height() / 2

    if value >= 0:
        ax.text(
            value + 0.012,
            y,
            f"+{value:.3f}",
            va="center",
            ha="left",
            fontsize=10
        )
    else:
        ax.text(
            value - 0.012,
            y,
            f"{value:.3f}",
            va="center",
            ha="right",
            fontsize=10
        )

ax.set_xlim(-0.13, 0.45)

ax.set_xlabel(
    "Minnesota Score Minus Golden State Score",
    fontsize=11
)

ax.set_ylabel("")

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.2
)

ax.set_axisbelow(True)

fig.suptitle(
    "2027 Collier Destination Fit: Sensitivity Analysis",
    fontsize=16,
    fontweight="bold",
    y=0.98
)

ax.set_title(
    "How Changes in Scouting Priorities Affect "
    "Minnesota vs. Golden State",
    fontsize=11,
    pad=15
)

fig.text(
    0.5,
    0.07,
    "Positive values favor Minnesota | "
    "Negative values favor Golden State",
    ha="center",
    fontsize=10
)

fig.text(
    0.5,
    0.035,
    "Illustrative weighting scenarios; "
    "not Collier's stated priorities or "
    "probabilities of signing.",
    ha="center",
    fontsize=9
)

fig.tight_layout(rect=[0, 0.11, 1, 0.91])

# STEP 7: Save the image
output_path = (
    OUTPUT_DIR / "2027_fit_sensitivity_comparison.png"
)

fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("\nSENSITIVITY VISUALIZATION SAVED")
print(output_path)