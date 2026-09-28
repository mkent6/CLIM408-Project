import pandas as pd
import xarray as xr
from pathlib import Path

# -----------------------------
# File paths
# -----------------------------

pyrocb_file = Path("pyrocb_conus.csv")
gridmet_dir = Path("gridmet_tmmx")
output_file = Path("pyrocb_conus_tmax.csv")


# -----------------------------
# Load pyroCb inventory
# -----------------------------

df = pd.read_csv(pyrocb_file)

# Convert datetime column
df["datetime"] = pd.to_datetime(
    df["datetime"],
    errors="coerce"
)

print(f"Loaded {len(df)} pyroCb events")
print(
    f"Date range: {df['datetime'].min()} "
    f"to {df['datetime'].max()}"
)
print(
    f"Missing event dates: "
    f"{df['datetime'].isna().sum()}"
)


# -----------------------------
# Create Tmax column
# -----------------------------

df["tmax_c"] = float("nan")


# -----------------------------
# Process each year
# -----------------------------

years = sorted(
    df["datetime"]
    .dropna()
    .dt.year
    .unique()
)

for year in years:

    nc_file = gridmet_dir / f"tmmx_{year}.nc"

    if not nc_file.exists():
        print(f"Missing gridMET file for {year}")
        continue

    # Get pyroCb events for this year
    mask = df["datetime"].dt.year == year
    indices = df.index[mask]

    print(
        f"Processing {year}: "
        f"{len(indices)} pyroCb events"
    )

    # Open one annual gridMET file
    with xr.open_dataset(nc_file) as ds:

        for idx in indices:

            lat = df.at[idx, "lat"]
            lon = df.at[idx, "lon"]
            event_datetime = df.at[idx, "datetime"]

            # Skip incomplete records
            if (
                pd.isna(lat)
                or pd.isna(lon)
                or pd.isna(event_datetime)
            ):
                continue

            try:

                # gridMET is daily, so remove event time
                event_day = pd.Timestamp(
                    event_datetime.date()
                )

                # Find nearest grid cell and correct day
                temp_k = (
                    ds["air_temperature"]
                    .sel(
                        day=event_day,
                        lat=float(lat),
                        lon=float(lon),
                        method="nearest"
                    )
                    .item()
                )

                # Convert Kelvin to Celsius
                temp_c = temp_k - 273.15

                df.at[idx, "tmax_c"] = temp_c

            except Exception as e:

                print(
                    f"Could not process row {idx}: {e}"
                )


# -----------------------------
# Save results
# -----------------------------

df.to_csv(
    output_file,
    index=False
)


# -----------------------------
# Summary
# -----------------------------

matched = df["tmax_c"].notna().sum()
missing = df["tmax_c"].isna().sum()

print()
print("Finished!")
print(f"Temperatures matched: {matched}")
print(f"Temperatures missing: {missing}")
print(f"Saved to: {output_file}")
