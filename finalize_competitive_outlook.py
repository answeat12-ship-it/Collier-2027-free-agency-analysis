
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
FILE = DATA_DIR / "collier_2027_fit_evaluations.csv"

scouting = pd.read_csv(FILE)

team = "Golden State Valkyries"
mask = scouting["destination"].eq(team)

if mask.sum() != 1:
    raise ValueError(
        f"Expected one Golden State row, found {mask.sum()}"
    )

if pd.notna(scouting.loc[mask, "competitive_outlook"]).any():
    raise ValueError(
        "Golden State already has a competitive outlook "
        "grade. Review before overwriting."
    )

evidence = (
    "2026 championship-level competitiveness and "
    "league-leading estimated defensive efficiency "
    "support a strong 2027 competitive outlook. "
    "Natalie Nakase's coaching structure is a strength. "
    "The Finals outcome alone does not determine this grade. "
    "Expansion-draft changes, roster continuity, and "
    "future rotation decisions remain uncertainties."
)

scouting["competitive_outlook_evidence"] = (
    scouting["competitive_outlook_evidence"].astype("string")
)

scouting.loc[mask, "competitive_outlook"] = 4.5
scouting.loc[mask, "competitive_outlook_evidence"] = evidence

categories = [
    "basketball_compatibility",
    "role_opportunity",
    "competitive_outlook",
    "financial_opportunity",
    "stability_continuity",
]

completed = scouting[categories].notna().sum().sum()

if completed != 20:
    raise ValueError(
        f"Expected 20 completed evaluations; found {completed}"
    )

scouting.to_csv(FILE, index=False)

print("\nFINAL SCOUTING GRADES SAVED")
print(
    scouting[
        ["destination"] + categories
    ].to_string(index=False)
)

print(f"\nEvaluations completed: {completed} of 20")
