from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)

# Load our calculated 2026 team efficiency estimates
df = pd.read_csv(
    DATA_DIR / "collier_2027_destination_comparison.csv"
)

required = {
    "destination",
    "offensive_rating",
    "defensive_rating"
}

missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

if len(df) != 4 or df["destination"].duplicated().any():
    raise ValueError("Expected four unique destinations.")

# Shortened names for the chart
names = {
    "Golden State Valkyries": "Golden State",
    "Minnesota Lynx": "Minnesota",
    "New York Liberty": "New York",
    "Toronto Tempo": "Toronto"
}

fig, ax = plt.subplots(figsize=(11, 7))

# Plot each team
for _, row in df.iterrows():
    team = names.get(
        row["destination"],
        row["destination"]
    )

    offense = row["offensive_rating"]
    defense = row["defensive_rating"]

    ax.scatter(
        offense,
        defense,
        s=180,
        zorder=3
    )

    ax.annotate(
        team,
        (offense, defense),
        xytext=(9, -12),
        textcoords="offset points",
        fontsize=11,
        fontweight="bold"
    )

# Defensive rating: lower is better.
# Reverse the vertical axis so better defenses appear higher.
ax.set_ylim(116, 92)
ax.set_xlim(101, 114)

ax.set_xlabel(
    "Estimated Offensive Rating "
    "(Higher Is Better)",
    fontsize=11
)

ax.set_ylabel(
    "Estimated Defensive Rating "
    "(Lower Is Better)",
    fontsize=11
)

fig.suptitle(
    "2026 WNBA: Offensive vs. Defensive Efficiency",
    fontsize=16,
    fontweight="bold",
    y=0.97
)

ax.set_title(
    "Napheesa Collier's 2027 Destination Candidates",
    fontsize=11
)

ax.grid(
    alpha=0.25,
    linestyle="--"
)

# Context note
fig.text(
    0.5,
    0.025,
    "Source: 2026 regular-season team box scores | "
    "Estimated points per 100 possessions",
    ha="center",
    fontsize=9
)

fig.tight_layout(rect=[0, 0.06, 1, 0.93])

output_path = (
    OUTPUT_DIR / "2026_offense_defense_comparison.png"
)

fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("\nOFFENSE VS. DEFENSE VISUALIZATION SAVED")
print(output_path)