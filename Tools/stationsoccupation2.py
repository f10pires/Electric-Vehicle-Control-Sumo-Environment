import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Read occupancy log
# -------------------------------------------------
df = pd.read_csv("sumo/results/charging_log.csv")

# -------------------------------------------------
# Create stacked bar chart
# -------------------------------------------------
plt.figure(figsize=(12, 6))

plt.bar(df["Hour"], df["Charge_ParkA"], label="Charge_ParkA")
plt.bar(df["Hour"], df["Charge_ParkB"],
        bottom=df["Charge_ParkA"],
        label="Charge_ParkB")

plt.bar(df["Hour"], df["Charge_ParkC"],
        bottom=df["Charge_ParkA"] + df["Charge_ParkB"],
        label="Charge_ParkC")

plt.bar(df["Hour"], df["Charge_ParkD"],
        bottom=df["Charge_ParkA"] + df["Charge_ParkB"] + df["Charge_ParkC"],
        label="Charge_ParkD")

plt.bar(df["Hour"], df["Charge_ParkE"],
        bottom=df["Charge_ParkA"] + df["Charge_ParkB"] + df["Charge_ParkC"] + df["Charge_ParkD"],
        label="Charge_ParkE")

# -------------------------------------------------
# Figure formatting
# -------------------------------------------------
plt.title(
    "Average Charging Station Occupancy by Hour",
    fontsize=20,
    fontweight="bold"
)

plt.xlabel(
    "Hour of Day",
    fontsize=18,
    fontweight="bold"
)

plt.ylabel(
    "Average Number of Vehicles",
    fontsize=18,
    fontweight="bold"
)

# Increase tick label size
plt.xticks(
    range(24),
    [f"{i:02d}" for i in range(24)],
    fontsize=15
)

plt.yticks(fontsize=15)

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.legend(
    title="Charging Station",
    title_fontsize=16,
    fontsize=14,
    loc="upper right"
)

plt.tight_layout()

plt.savefig(
    "sumo/results/charging_station_occupancy.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()