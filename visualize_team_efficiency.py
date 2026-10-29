from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)

# Load our published destination comparison
df = pd.read_csv(
    DATA_DIR / "collier_2027_destination_comparison.csv"
)

# Verify required columns
required = {"destination", "net_rating"}

missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

# Order teams by estimated net rating
df = df.sort_values("net_rating")

# Simplify names for display
df["team"] = (
    df["destination"]
    .str.replace("Valkyries", "", regex=False)
    .str.replace("Lynx", "", regex=False)
    .str.replace("Liberty", "", regex=False)
    .str.replace("Tempo", "", regex=False)
)

# Create chart
fig, ax = plt.subplots(figsize=(11, 6))

bars = ax.barh(
    df["team"],
    df["net_rating"]
)

ax.axvline(0, linewidth=1)

ax.bar_label(
    bars,
    fmt="%+.2f",
    padding=5
)

ax.set_title(
    "2026 WNBA Estimated Net Rating\n"
    "Napheesa Collier's 2027 Destination Candidates"
)

ax.set_xlabel(
    "Estimated net rating"
    "(points per 100 possessions)"
)

ax.set_ylabel("")

ax.set_xlim(
    min(-13, df["net_rating"].min() - 2),
    max(13, df["net_rating"].max() + 2)
)

fig.text(
    0.5,
    0.02,
    "Source: 2026 regular-season team box scores | "
    "Estimated possession-based ratings",
    ha="center",
    fontsize=9
)

fig.tight_layout(rect=[0, 0.06, 1, 0.91])

# Save visualization
output_path = (
    OUTPUT_DIR / "2026_destination_net_rating.png"
)

fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("VISUALIZATION SAVED")
print(output_path)