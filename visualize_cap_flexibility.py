from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)

CAP = 7_910_000

# Load our published salary-cap scenarios
gs = pd.read_csv(
    DATA_DIR / "golden_state_2027_cap_scenarios.csv"
)

mn = pd.read_csv(
    DATA_DIR / "minnesota_2027_cap_scenarios.csv"
)

tor = pd.read_csv(
    DATA_DIR / "toronto_2027_cap_scenarios.csv"
)

ny = pd.read_csv(
    DATA_DIR / "liberty_2027_cap_scenarios.csv"
)


def select_one(df, mask, description):
    selected = df.loc[mask]

    if len(selected) != 1:
        raise ValueError(
            f"Expected one row for {description}; "
            f"found {len(selected)}."
        )

    return selected.iloc[0]


def normalized(series):
    return (
        series.astype("string")
        .str.strip()
        .str.casefold()
    )


# Golden State standard maximum
golden_state = select_one(
    gs,
    gs["cap_assumption"].eq(CAP),
    "Golden State"
)

# Minnesota standard maximum
minnesota_standard = select_one(
    mn,
    mn["cap_assumption"].eq(CAP)
    & normalized(mn["salary_tier"]).eq("standard max"),
    "Minnesota standard max"
)

# Minnesota potential supermax
minnesota_supermax = select_one(
    mn,
    mn["cap_assumption"].eq(CAP)
    & normalized(mn["salary_tier"]).eq("potential supermax"),
    "Minnesota potential supermax"
)

# Toronto standard maximum
toronto = select_one(
    tor,
    tor["cap_assumption"].eq(CAP),
    "Toronto"
)

# New York: direct addition with standard maximum
new_york = select_one(
    ny,
    ny["cap_assumption"].eq(CAP)
    & normalized(ny["scenario"]).eq("add collier")
    & normalized(ny["collier_salary_tier"]).eq("standard max"),
    "New York direct-add standard max"
)


# Build comparison from the source CSVs
comparison = pd.DataFrame({
    "destination": [
        "Golden State - Standard",
        "Minnesota - Standard",
        "Minnesota - Potential Supermax",
        "Toronto - Standard",
        "New York - Direct Addition"
    ],
    "cap_remaining": [
        golden_state["cap_remaining"],
        minnesota_standard["cap_remaining"],
        minnesota_supermax["cap_remaining"],
        toronto["cap_remaining"],
        new_york["cap_remaining"]
    ]
})

comparison = comparison.sort_values(
    "cap_remaining"
)

# Create chart
fig, ax = plt.subplots(figsize=(13, 7))

bars = ax.barh(
    comparison["destination"],
    comparison["cap_remaining"]
)

# Zero line distinguishes positive and negative balances
ax.axvline(
    0,
    linewidth=1.2,
    zorder=3
)

# Display clear dollar amounts next to each bar
for bar, value in zip(
    bars,
    comparison["cap_remaining"]
):
    y = bar.get_y() + bar.get_height() / 2

    if value >= 0:
        ax.text(
            value + 35000,
            y,
            f"${value:,.0f}",
            va="center",
            ha="left",
            fontsize=10
        )
    else:
        ax.text(
            value - 35000,
            y,
            f"-${abs(value):,.0f}",
            va="center",
            ha="right",
            fontsize=10
        )

# Axis limits leave room for value labels
ax.set_xlim(-300000, 1650000)

# Format ticks as dollars in millions
def money_millions(value, position):
    if value < 0:
        return f"-${abs(value) / 1_000_000:.1f}M"

    return f"${value / 1_000_000:.1f}M"


ax.xaxis.set_major_formatter(
    FuncFormatter(money_millions)
)

ax.set_xlabel(
    "Modeled Remaining Salary-Cap Space (USD)",
    fontsize=11
)
ax.set_ylabel("")

fig.suptitle(
    "2027 WNBA: Modeled Roster-Building Flexibility",
    fontsize=16,
    fontweight="bold",
    y=0.97
)

ax.set_title(
    "Napheesa Collier's Potential Destinations | "
    "Hypothetical $7.91M Cap",
    fontsize=11
)

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.2
)

ax.set_axisbelow(True)

# Modeling assumptions and limitations
fig.text(
    0.5,
    0.055,
    "Includes Collier's modeled salary and "
    "12-player minimum-roster cost placeholders.",
    ha="center",
    fontsize=9
)

fig.text(
    0.5,
    0.025,
    "Negative values indicate a scenario exceeding "
    "the assumed cap. Figures are not confirmed "
    "2027 cap availability.",
    ha="center",
    fontsize=9
)

fig.tight_layout(rect=[0, 0.10, 1, 0.92])

# Save visualization
output_path = (
    OUTPUT_DIR / "2027_cap_flexibility_comparison.png"
)

fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("\nCAP FLEXIBILITY VISUALIZATION SAVED")
print(output_path)

print("\nMODELED REMAINING CAP SPACE")
print(
    comparison.to_string(index=False)
)