import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import json

# =========================
# Configuration
# =========================

"""Load config at 'data/dumpsters.json'"""

with open('data/dumpsters.json', "r", encoding="utf-8") as f:
    dumpsters =  json.load(f)

input_file = os.path.join(
    "Tools",
    "Exels_results",
    "Dhaka_Commercial_Dhanmondi_Normal.xlsx"
)



# =========================
# Read Excel file
# =========================

df = pd.read_excel(input_file)


# =========================
# Process date
# =========================

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df["day"] = df["date"].dt.date


# =========================
# Process time_factor
# =========================

df["time_factor"] = df["time_factor"].astype(int)


# =========================
# Calculate current waste
# =========================

df["Kg"] = (
    df["bin_capacity"] *
    df["fill_level"] / 100
)


# =========================
# Create nested dictionary
# =========================

data = {}


for (day, time_factor, time_slot), group in df.groupby(
    ["day", "time_factor", "time_slot"]
):

    day = str(day)

    # Create date if it does not exist
    if day not in data:
        data[day] = {}

    # Create time_factor if it does not exist
    if time_factor not in data[day]:
        data[day][time_factor] = {}

    # Create time_slot if it does not exist
    if time_slot not in data[day][time_factor]:
        data[day][time_factor][time_slot] = {}

    # Add bins
    for _, row in group.iterrows():

        bin_id = row["bin_id"]

        data[day][time_factor][time_slot][bin_id] = {
            "Kg": row["Kg"] + row["overflow_kg"]
        }

fill_waste = 0
for date in data :
    for time in data[date]:
        for time_slot in data[date][time]:
           for bin in data[date][time][time_slot] :
               fill_waste += data[date][time][time_slot][bin]["Kg"]
           
           data[date][time][time_slot] = fill_waste
           fill_waste = 0

D1 = dumpsters["d1"]

for date in data:
    
    # Create the date if it does not exist
    if date not in D1["fill_days"]:
        D1["fill_days"][date] = {}

    for time_factor in data[date]:

        # Create the time factor if it does not exist
        if time_factor not in D1["fill_days"][date]:
            D1["fill_days"][date][time_factor] = {
                "fill_waste(Kg)": next(
                    iter(data[date][time_factor].values())
                ),
                "overflow_kg": 0
            }
 
        if D1["fill_days"][date][time_factor]["fill_waste(Kg)"]  > D1["bin_capacity"] :
            D1["fill_days"][date][time_factor]["overflow_kg"] =  D1["fill_days"][date][time_factor]["fill_waste(Kg)"] -  D1["bin_capacity"]
            D1["fill_days"][date][time_factor]["fill_waste(Kg)"] = D1["bin_capacity"]

# ============================================================
# Update dumpsters and save JSON
# ============================================================

dumpsters["d1"] = D1

with open("data/dumpsters.json", "w", encoding="utf-8") as f:
    json.dump(
        dumpsters,
        f,
        ensure_ascii=False,
        indent=4
    )



# =========================
# Select first four days
# =========================

first_four_days = list(D1["fill_days"].items())[:4]


# =========================
# Create figure
# =========================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 9)
)

axes = axes.flatten()


# =========================
# Plot each day
# =========================

for ax, (date, time_data) in zip(axes, first_four_days):

    # Sort time factors
    time_factors = sorted(time_data.keys())

    # Get waste values
    waste = [
        time_data[time_factor]["fill_waste(Kg)"]
        for time_factor in time_factors
    ]

    # Create bars
    ax.bar(
        time_factors,
        waste,
        width=0.7
    )

    # Title
    ax.set_title(
        date,
        fontsize=14
    )

    # Labels
    ax.set_xlabel(
        "Time of day",
        fontsize=11
    )

    ax.set_ylabel(
        "Waste (Kg)",
        fontsize=11
    )

    # =========================
    # Improved X-axis
    # =========================

    ax.set_xlim(-0.5, 23.5)

    ax.set_xticks(range(0, 24, 2))

    ax.set_xticklabels(
        [f"{hour:02d}:00" for hour in range(0, 24, 2)],
        rotation=45,
        ha="right",
        fontsize=10
    )

    # Grid
    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )


# =========================
# General title
# =========================

fig.suptitle(
    f"Waste evolution - Bin {D1['bin_id']}",
    fontsize=18
)


# =========================
# Layout
# =========================

plt.tight_layout()

plt.show()