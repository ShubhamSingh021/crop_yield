from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "agriculture_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "historical_crop_data.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading agricultural dataset...")

df = pd.read_csv(SOURCE_FILE)

print(f"Source: {SOURCE_FILE}")
print(f"Rows: {len(df):,}")
print(f"Columns: {df.columns.tolist()}")


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = {
    "State",
    "District",
    "Crop",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:

    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# CLEAN VALUES
# ============================================================

support = df[
    [
        "State",
        "District",
        "Crop",
    ]
].copy()


support["State"] = (
    support["State"]
    .astype(str)
    .str.strip()
)

support["District"] = (
    support["District"]
    .astype(str)
    .str.strip()
)

support["Crop"] = (
    support["Crop"]
    .astype(str)
    .str.strip()
)


# Remove invalid rows

support = support[
    (support["State"] != "")
    & (support["District"] != "")
    & (support["Crop"] != "")
]


# ============================================================
# COUNT HISTORICAL RECORDS
# ============================================================

historical_support = (
    support
    .groupby(
        [
            "State",
            "District",
            "Crop",
        ]
    )
    .size()
    .reset_index(name="historical_records")
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# SAVE
# ============================================================

historical_support.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("\n" + "=" * 70)
print("HISTORICAL SUPPORT FILE CREATED")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(
    f"\nUnique State/District/Crop combinations: "
    f"{len(historical_support):,}"
)


# ============================================================
# TEST EXAMPLES
# ============================================================

print("\nExample records:")

print(
    historical_support.head(10).to_string(
        index=False
    )
)


# ============================================================
# TEST COCONUT + JAIPUR
# ============================================================

print("\n" + "=" * 70)
print("TEST: COCONUT + JAIPUR")
print("=" * 70)

test = historical_support[
    (
        historical_support["State"]
        .str.lower()
        .str.contains("rajasthan", na=False)
    )
    &
    (
        historical_support["District"]
        .str.lower()
        .str.contains("jaipur", na=False)
    )
    &
    (
        historical_support["Crop"]
        .str.lower()
        .str.contains("coconut", na=False)
    )
]

if len(test) > 0:

    print("\nHistorical support FOUND:")
    print(
        test.to_string(index=False)
    )

else:

    print(
        "\nNo historical Coconut + Jaipur "
        "combination found."
    )

print("\nDone.")