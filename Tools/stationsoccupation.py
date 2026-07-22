import pandas as pd
import matplotlib.pyplot as plt

# Read log
df = pd.read_csv("sumo/results/charging_log.csv")

plt.figure(figsize=(10, 5))

for column in df.columns[1:]:
    plt.plot(df["Hour"], df[column], linewidth=2, label=column)

plt.xlabel("Hour of Day")
plt.ylabel("Average Number of Vehicles")
plt.title("Average Charging Station Occupancy")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig("sumo/results/charging_occupancy.pdf", dpi=300)
plt.show()