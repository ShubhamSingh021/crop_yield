from pathlib import Path
import pandas as pd

# Go to the PROJECT ROOT
# This script is currently inside backend,
# so parent = smart-crop-ai
PROJECT_DIR = Path(__file__).parent.parent

print(f"\nSearching project: {PROJECT_DIR}\n")
print("Searching for CSV files that may contain crop data...\n")

found = False

for csv_file in PROJECT_DIR.rglob("*.csv"):

    # Skip known generated/support files
    if csv_file.name.lower() in [
        "climate_lookup.csv",
        "historical_crop_data.csv",
    ]:
        continue

    try:
        df = pd.read_csv(csv_file, nrows=5)

        columns = [str(col) for col in df.columns]

        normalized = [
            col.strip()
            .lower()
            .replace("_", "")
            .replace(" ", "")
            for col in columns
        ]

        has_state = any("state" in col for col in normalized)
        has_district = any("district" in col for col in normalized)
        has_crop = any("crop" in col for col in normalized)

        if has_state and has_district and has_crop:

            found = True

            print("=" * 70)
            print("POSSIBLE CROP DATASET FOUND")
            print("=" * 70)

            print(f"\nFile:\n{csv_file}")

            print("\nColumns:")
            for column in columns:
                print(f"  - {column}")

            print()

    except Exception as e:
        print(f"Could not read: {csv_file.name}")

if not found:
    print("=" * 70)
    print("NO CROP DATASET FOUND")
    print("=" * 70)
    print(
        "\nNo CSV containing State + District + Crop "
        "was found anywhere inside smart-crop-ai."
    )

print("\nSearch finished.")