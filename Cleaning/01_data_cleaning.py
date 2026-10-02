import pandas as pd
import numpy as np

df = pd.read_csv("indian_roads_dataset.csv")

print("Original shape:", df.shape)
print(df.head())

#2
print("\nMissing values:")
print(df.isnull().sum())

# STEP 3: Handle missing festival values

df["festival"] = df["festival"].fillna("No Festival")

print("\nMissing values after handling festival:")
print(df.isnull().sum())

print("\nFestival distribution:")
print(df["festival"].value_counts())


# STEP 4: Check for duplicate rows

print("\nDuplicate rows:")
print(df.duplicated().sum())

# STEP 5: Check data types

print("\nData types:")
print(df.dtypes)

# STEP 6: Convert date and time

df["date"] = pd.to_datetime(df["date"], errors="coerce")

df["time"] = pd.to_datetime(
    df["time"],
    format="%H:%M",
    errors="coerce"
).dt.time

print("\nData types after conversion:")
print(df.dtypes)

# STEP 7: Check invalid dates and times

print("\nInvalid dates:")
print(df["date"].isna().sum())

print("\nInvalid times:")
print(df["time"].isna().sum())


# STEP 8: Validate latitude and longitude

print("\nLatitude range:")
print(df["latitude"].min(), df["latitude"].max())

print("\nLongitude range:")
print(df["longitude"].min(), df["longitude"].max())

invalid_coordinates = df[
    ~df["latitude"].between(6, 38) |
    ~df["longitude"].between(68, 98)
]

print("\nInvalid coordinates:")
print(len(invalid_coordinates))


# STEP 9: Validate accident-related numerical values

print("\nVehicles involved:")
print(df["vehicles_involved"].describe())

print("\nCasualties:")
print(df["casualties"].describe())

print("\nLanes:")
print(df["lanes"].describe())

print("\nRisk score:")
print(df["risk_score"].describe())

print("\nNegative values:")

print("Vehicles involved:",
      (df["vehicles_involved"] < 0).sum())

print("Casualties:",
      (df["casualties"] < 0).sum())

print("Lanes:",
      (df["lanes"] < 0).sum())

print("Risk score:",
      (df["risk_score"] < 0).sum())

# STEP 10: Check categorical values

categorical_columns = [
    "city",
    "state",
    "day_of_week",
    "road_type",
    "weather",
    "visibility",
    "traffic_density",
    "cause",
    "accident_severity",
    "festival"
]

for col in categorical_columns:
    print("\n" + "=" * 40)
    print(col)
    print(df[col].value_counts())

# STEP 11: Check city-state relationship

print("\nCity-State combinations:")
print(
    df[["city", "state"]]
    .drop_duplicates()
    .sort_values(["state", "city"])
    .to_string(index=False)
)

print("\nNumber of records for each city-state combination:")
print(
    df.groupby(["state", "city"])
      .size()
      .sort_values(ascending=False)
)

# STEP 12: Check accident IDs

print("\nAccident ID information:")
print("Unique IDs:", df["accident_id"].nunique())
print("Total rows:", len(df))

print("\nDuplicate accident IDs:")
print(df["accident_id"].duplicated().sum())

# STEP 13: Validate binary columns

binary_columns = [
    "is_weekend",
    "traffic_signal",
    "is_peak_hour"
]

for col in binary_columns:
    print("\n", col)
    print(df[col].value_counts())

# STEP 14: Validate hour column

print("\nHour range:")
print("Minimum hour:", df["hour"].min())
print("Maximum hour:", df["hour"].max())

invalid_hours = df[
    ~df["hour"].between(0, 23)
]

print("\nInvalid hours:", len(invalid_hours))

print("\nHour distribution:")
print(df["hour"].value_counts().sort_index())


# STEP 15: Check time consistency

# Extract hour from time
time_hour = pd.to_datetime(
    df["time"].astype(str),
    format="%H:%M:%S",
    errors="coerce"
).dt.hour

print("\nTime vs Hour mismatches:")
print((time_hour != df["hour"]).sum())

# Check whether is_weekend matches the actual date

calculated_weekend = (
    df["date"].dt.dayofweek >= 5
).astype(int)

print("\nWeekend mismatches:")
print((calculated_weekend != df["is_weekend"]).sum())

# STEP 16: Save cleaned dataset

df.to_csv(
    "indian_roads_cleaned.csv",
    index=False
)

print("\nCleaned dataset saved successfully!")
print("Final shape:", df.shape)