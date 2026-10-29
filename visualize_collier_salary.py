from pathlib import Path
from matplotlib.ticker import FuncFormatter

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)

CAP = 7_910_000

# Load the four existing financial models
golden_state = pd.read_csv(
    DATA_DIR / "golden_state_2027_cap_scenarios.csv"
)

minnesota = pd.read_csv(
    DATA_DIR / "minnesota_2027_cap_scenarios.csv"
)

toronto = pd.read_csv(
    DATA_DIR / "toronto_2027_cap_scenarios.csv"
)

new_york = pd.read_csv(
    DATA_DIR / "liberty_2027_cap_scenarios.csv"
)

# Select exactly one matching model scenario
def select_one(df, mask, description):
    selected = df.loc[mask]

    if len(selected) != 1:
        raise ValueError(
            f"Expected one row for {description}, "
            f"found {len(selected)}."
        )

    return selected.iloc[0]


gs = select_one(
    golden_state,
    golden_state["cap_assumption"].eq(CAP),
    "Golden State standard max"
)

mn_standard = select_one(
    minnesota,
    minnesota["cap_assumption"].eq(CAP)
    & minnesota["salary_tier"].eq("Standard max"),
    "Minnesota standard max"
)

mn_supermax = select_one(
    minnesota,
    minnesota["cap_assumption"].eq(CAP)
    & minnesota["salary_tier"].eq("Potential supermax"),
    "Minnesota potential supermax"
)

tor = select_one(
    toronto,
    toronto["cap_assumption"].eq(CAP),
    "Toronto standard max"
)

ny = select_one(
    new_york,
    new_york["cap_assumption"].eq(CAP)
    & new_york["scenario"].eq("Add Collier")
    & new_york["collier_salary_tier"].eq("Standard max"),
    "New York direct-add standard max"
)

# Salary opportunities, not confirmed offers
salaries = pd.DataFrame({
    "scenario": [
        "Golden State - Standard",
        "Minnesota - Standard",
        "Minnesota - Potential Supermax",
        "Toronto - Standard",
        "New York - Standard"
    ],
    "salary": [
        gs["collier_standard_max"],
        mn_standard["collier_salary"],
        mn_supermax["collier_salary"],
        tor["collier_standard_max"],
        ny["collier_salary"]
    ]
})

fig, ax = plt.subplots(figsize=(12, 6))

bars = ax.barh(
    salaries["scenario"],
    salaries["salary"]
)

ax.invert_yaxis()

ax.bar_label(
    bars,
    labels=[
        f"${value:,.0f}"
        for value in salaries["salary"]
    ],
    padding=5
)

ax.set_xlim(
    0,
    salaries["salary"].max() * 1.2
)

ax.xaxis.set_major_formatter(
    FuncFormatter(
        lambda value, position: f"${value / 1_000_000:.1f}M"
    )
)

ax.set_xlabel("Modeled Annual Salary (USD)")
ax.set_ylabel("")

fig.suptitle(
    "Napheesa Collier: 2027 Salary Opportunities",
    fontsize=16,
    fontweight="bold",
    y=0.97
)

ax.set_title(
    "Hypothetical $7.91M Salary-Cap Scenario",
    fontsize=11
)

fig.text(
    0.5,
    0.025,
    "Potential Minnesota supermax requires eligibility. "
    "New York's direct-add scenario exceeds modeled cap room. "
    "Figures are not confirmed offers.",
    ha="center",
    fontsize=8,
    wrap=True
)

fig.tight_layout(rect=[0, 0.09, 1, 0.91])

output_path = (
    OUTPUT_DIR / "2027_collier_salary_comparison.png"
)

fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("\nSALARY VISUALIZATION SAVED")
print(output_path)
print("\nMODELED SALARY OPPORTUNITIES")
print(salaries.to_string(index=False))