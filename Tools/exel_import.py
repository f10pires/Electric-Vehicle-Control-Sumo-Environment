import pandas as pd
import os

# =========================
# Configuration
# =========================

# Relative folder containing the Excel files
excel_folder = os.path.join("Tools", "Exels_results")

# Input Excel file
input_file = os.path.join(
    excel_folder,
    "data.xlsx"
)


# =========================
# Read Excel file
# =========================

df = pd.read_excel(input_file)


# =========================
# Base filter
# =========================

base_filter = (
    (df["city"] == "Dhaka") &
    (df["area_type"] == "Commercial") &
    (df["neighborhood"] == "Dhanmondi")
)


# =========================
# Normal event
# =========================

df_normal = df[
    base_filter &
    (df["event"] == "Normal")
]

normal_file = os.path.join(
    excel_folder,
    "Dhaka_Commercial_Dhanmondi_Normal.xlsx"
)

df_normal.to_excel(normal_file, index=False)


# =========================
# Weekend event
# =========================

df_weekend = df[
    base_filter &
    (df["event"] == "Weekend")
]

weekend_file = os.path.join(
    excel_folder,
    "Dhaka_Commercial_Dhanmondi_Weekend.xlsx"
)

df_weekend.to_excel(weekend_file, index=False)


# =========================
# Results
# =========================

print(f"Normal records: {len(df_normal)}")
print(f"Weekend records: {len(df_weekend)}")

print("\nFiles saved to:")
print(f"- {normal_file}")
print(f"- {weekend_file}")