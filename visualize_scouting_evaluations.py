from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# STEP 1: Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)

# STEP 2: Load our existing scouting grades
scouting = pd.read_csv(
    DATA_DIR / "collier_2027_fit_evaluations.csv"
)

weights_df = pd.read_csv(
    DATA_DIR / "collier_2027_scoring_weights.csv"
)

weights = dict(zip(
    weights_df["category"],
    weights_df["weight"]
))

# STEP 3: Define category order and labels
categories = [
    ("basketball_compatibility", "Basketball Fit"),
    ("role_opportunity", "Role & Opportunity"),
    ("competitive_outlook", "Competitive Outlook"),
    ("financial_opportunity", "Financial Opportunity"),
    ("stability_continuity", "Stability & Continuity")
]

teams = [
    "Golden State Valkyries",
    "Minnesota Lynx",
    "New York Liberty",
    "Toronto Tempo"
]

short_names = {
    "Golden State Valkyries": "Golden State",
    "Minnesota Lynx": "Minnesota",
    "New York Liberty": "New York",
    "Toronto Tempo": "Toronto"
}

# STEP 4: Validate the underlying data
required = {"destination"} | {
    column for column, _ in categories
}

missing_columns = required - set(scouting.columns)

if missing_columns:
    raise ValueError(
        f"Missing scouting columns: {missing_columns}"
    )

if scouting["destination"].duplicated().any():
    raise ValueError("Duplicate destinations found.")

if set(scouting["destination"]) != set(teams):
    raise ValueError("Unexpected destination names.")

if not all(column in weights for column, _ in categories):
    raise ValueError("Scoring weights are incomplete.")

if not np.isclose(sum(weights.values()), 1.0):
    raise ValueError("Scoring weights must total 1.0.")

scouting = (
    scouting.set_index("destination")
    .loc[teams]
    .reset_index()
)

for column, _ in categories:
    scouting[column] = pd.to_numeric(
        scouting[column],
        errors="raise"
    )

    values = scouting[column].dropna()

    if not values.between(1, 5).all():
        raise ValueError(
            f"Grades outside 1–5 range: {column}"
        )

# STEP 5: Build the grouped bar chart
fig, ax = plt.subplots(figsize=(14, 8))

team_positions = np.arange(len(teams))
bar_height = 0.15

for index, (column, label) in enumerate(categories):

    offset = (index - 2) * bar_height

    positions = team_positions + offset
    values = scouting[column]

    # Exclude missing evaluations from plotted bars
    valid = values.notna()

    bars = ax.barh(
        positions[valid],
        values[valid],
        height=bar_height * 0.9,
        color=f"C{index}",
        label=f"{label} ({weights[column]:.0%})"
    )

    # Label completed grades
    for bar, value in zip(bars, values[valid]):
        ax.text(
            value + 0.06,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
            fontsize=9
        )

    # Clearly label any missing evaluation
    for position in positions[~valid]:
        ax.text(
            0.12,
            position,
            "Pending",
            va="center",
            fontsize=9,
            fontstyle="italic",
            color="gray"
        )

# STEP 6: Configure the chart
ax.set_yticks(team_positions)

ax.set_yticklabels(
    [short_names[team] for team in teams],
    fontsize=11
)

ax.invert_yaxis()

ax.set_xlim(0, 5.65)
ax.set_xticks([0, 1, 2, 3, 4, 5])

ax.set_xlabel(
    "Scouting Evaluation (1–5 Scale)",
    fontsize=11
)

ax.set_ylabel("")

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.2
)

ax.set_axisbelow(True)

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.08),
    ncol=3,
    fontsize=9
)

fig.suptitle(
    "Napheesa Collier: 2027 Destination Fit Evaluations",
    fontsize=16,
    fontweight="bold",
    y=0.98
)

ax.set_title(
    "Evidence-Informed Scouting Assessments",
    fontsize=11,
    pad=16
)

fig.text(
    0.5,
    0.015,
    "All 20 scouting evaluations completed. "
    "Category weights reflect the assessment framework. "
    "Grades are evidence-informed judgments, not predictions.",
    ha="center",
    fontsize=9
)

fig.tight_layout(rect=[0, 0.07, 1, 0.92])

# STEP 7: Save the chart
output_path = (
    OUTPUT_DIR / "2027_destination_fit_evaluations.png"
)

fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("\nSCOUTING VISUALIZATION SAVED")
print(output_path)

print("\nCURRENT DESTINATION GRADES")
print(
    scouting[
        ["destination"] +
        [column for column, _ in categories]
    ].to_string(index=False)
)

print("\nEvaluations completed:")
print(
    scouting[
        [column for column, _ in categories]
    ].notna().sum().sum(),
    "of 20"
)