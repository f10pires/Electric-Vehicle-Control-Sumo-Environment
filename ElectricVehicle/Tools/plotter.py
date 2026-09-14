import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

plt.style.use("seaborn-v0_8-whitegrid")

# ==========================================================
# PATH
# ==========================================================

root_dir = Path(__file__).resolve().parent.parent
pasta_results = root_dir / "sumo" / "results"
pasta_results.mkdir(parents=True, exist_ok=True)

print(f"Results folder: {pasta_results}")

# ==========================================================
# REMOVE OLD PNGS
# ==========================================================

for f in pasta_results.glob("*.png"):
    f.unlink(missing_ok=True)

# ==========================================================
# LOAD CSVs
# ==========================================================

arquivos_csv = sorted(pasta_results.glob("*.csv"))

if not arquivos_csv:
    print("No CSV files found.")

for csv_path in arquivos_csv:

    print(f"Reading {csv_path.name}")

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    required = [
        "== Timestamp ==",
        "== Velocity (km/h) ==",
        "== Battery level (%) =="
    ]

    if not all(c in df.columns for c in required):
        print(f"Skipping {csv_path.name}")
        continue

    # ======================================================
    # CONVERT TYPES
    # ======================================================

    df["== Timestamp =="] = pd.to_datetime(df["== Timestamp =="], errors="coerce")
    df["== Velocity (km/h) =="] = pd.to_numeric(df["== Velocity (km/h) =="], errors="coerce")
    df["== Battery level (%) =="] = pd.to_numeric(df["== Battery level (%) =="], errors="coerce")

    df = df.dropna(subset=required)

    if df.empty:
        print(f"{csv_path.name} empty after cleaning.")
        continue

    # ======================================================
    # RESAMPLE (ONLY NUMERIC COLUMNS)
    # ======================================================

    df = df.set_index("== Timestamp ==")

    df_resampled = df[[
        "== Velocity (km/h) ==",
        "== Battery level (%) =="
    ]].resample("1min").mean().dropna()

    # ======================================================
    # TIME IN HOURS
    # ======================================================

    df_resampled["time_h"] = (
        df_resampled.index - df_resampled.index[0]
    ).total_seconds() / 3600

    veh_id = csv_path.stem

    # ======================================================
    # PLOT
    # ======================================================

    fig, ax1 = plt.subplots(figsize=(12, 5), dpi=300)

    color_vel = "#0077b6"
    color_bat = "#2d6a4f"

    # SPEED
    l1 = ax1.plot(
        df_resampled["time_h"],
        df_resampled["== Velocity (km/h) =="],
        linewidth=2,
        color=color_vel,
        label="Speed "
    )

    ax1.set_ylabel("Speed (km/h)", color=color_vel, fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_vel)
    ax1.set_ylim(0, 120)

    ax1.yaxis.set_major_locator(ticker.MultipleLocator(20))

    # BATTERY
    ax2 = ax1.twinx()

    l2 = ax2.plot(
        df_resampled["time_h"],
        df_resampled["== Battery level (%) =="],
        linewidth=2,
        color=color_bat,
        label="Battery level"
    )

    ax2.set_ylabel("Battery Level (%)", color=color_bat, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color_bat)
    ax2.set_ylim(0, 100)

    ax2.yaxis.set_major_locator(ticker.MultipleLocator(20))

    # ======================================================
    # STYLE
    # ======================================================

    ax1.set_xlabel("Time (hours)", fontsize=12, fontweight="bold")

    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax1.grid(True, linestyle="-", alpha=0.5)

    # LEGEND
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right")

    plt.tight_layout()

    # SAVE
    out_path = pasta_results / f"{veh_id}.pdf"

    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"✓ Saved {out_path.name}")

print("\nDone.")