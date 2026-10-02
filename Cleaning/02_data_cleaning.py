import pandas as pd
import numpy as np

df2 = pd.read_csv("accident_prediction_india.csv")

print("Original shape:", df2.shape)
print(df2.head())

# STEP 2: Check missing values

print("\nMissing values:")
print(df2.isnull().sum())

# STEP 3: Handle missing categorical values

df2["Traffic Control Presence"] = (
    df2["Traffic Control Presence"].fillna("Unknown")
)

df2["Driver License Status"] = (
    df2["Driver License Status"].fillna("Unknown")
)

print("\nMissing values after handling:")
print(df2.isnull().sum())

# STEP 4: Check duplicate rows

print("\nDuplicate rows:")
print(df2.duplicated().sum())


# STEP 5: Check data types

print("\nData types:")
print(df2.dtypes)

# STEP 6: Clean text columns

text_columns = df2.select_dtypes(include="str").columns

for col in text_columns:
    df2[col] = df2[col].str.strip()

print("\nText columns cleaned successfully.")

print("\nEmpty string counts:")

for col in text_columns:
    print(col, (df2[col] == "").sum())

# STEP 7: Validate year

print("\nYear range:")
print("Minimum year:", df2["Year"].min())
print("Maximum year:", df2["Year"].max())

print("\nYear distribution:")
print(df2["Year"].value_counts().sort_index())

# STEP 8: Validate numerical accident data

numeric_columns = [
    "Number of Vehicles Involved",
    "Number of Casualties",
    "Number of Fatalities",
    "Speed Limit (km/h)",
    "Driver Age"
]

for col in numeric_columns:
    print("\n" + "=" * 50)
    print(col)
    print(df2[col].describe())

print("\nNegative values:")

for col in numeric_columns:
    print(
        col,
        ":",
        (df2[col] < 0).sum()
    )

# STEP 9: Check logical consistency

print("\n" + "=" * 50)
print("LOGICAL CONSISTENCY CHECK")

# Fatalities should not exceed casualties
print(
    "Fatalities greater than casualties:",
    (df2["Number of Fatalities"] > df2["Number of Casualties"]).sum()
)

# Driver age should be within expected range
print(
    "Driver age below 18:",
    (df2["Driver Age"] < 18).sum()
)

print(
    "Driver age above 70:",
    (df2["Driver Age"] > 70).sum()
)

# Speed limit should be positive
print(
    "Invalid speed limits:",
    (df2["Speed Limit (km/h)"] <= 0).sum()
)

# Vehicles involved should be at least 1
print(
    "Invalid vehicle counts:",
    (df2["Number of Vehicles Involved"] < 1).sum()
)

# STEP 10: Inspect inconsistent records

problematic_rows = df2[
    df2["Number of Fatalities"] > df2["Number of Casualties"]
]

print("Number of problematic records:", len(problematic_rows))

print("\nSample problematic records:")
print(
    problematic_rows[
        [
            "State Name",
            "City Name",
            "Year",
            "Accident Severity",
            "Number of Vehicles Involved",
            "Number of Casualties",
            "Number of Fatalities"
        ]
    ].head(20)
)

# STEP 11: Flag logically inconsistent records

df2["logical_inconsistency"] = (
    df2["Number of Fatalities"] > df2["Number of Casualties"]
)

print("\n" + "=" * 50)
print("DATA QUALITY FLAG")

print(
    df2["logical_inconsistency"].value_counts()
)

print(
    "\nInconsistent records:",
    df2["logical_inconsistency"].sum()
)

print(
    "Valid records:",
    (~df2["logical_inconsistency"]).sum()
)

# STEP 12: Check categorical values

categorical_columns = [
    "State Name",
    "City Name",
    "Month",
    "Day of Week",
    "Time of Day",
    "Accident Severity",
    "Vehicle Type Involved",
    "Weather Conditions",
    "Road Type",
    "Road Condition",
    "Lighting Conditions",
    "Traffic Control Presence",
    "Driver Gender",
    "Driver License Status",
    "Alcohol Involvement"
]

for col in categorical_columns:
    print("\n" + "=" * 50)
    print(col)
    print("Unique values:", df2[col].nunique())
    print(df2[col].value_counts())

# STEP 13: Validate Time of Day

print("\n" + "=" * 50)
print("TIME OF DAY VALIDATION")

# Convert Time of Day into datetime format
time_check = pd.to_datetime(
    df2["Time of Day"],
    format="%H:%M",
    errors="coerce"
)

print("Invalid time values:", time_check.isna().sum())

print("\nSample converted times:")
print(time_check.head(20))

print("\nTime range:")
print("Minimum:", time_check.min())
print("Maximum:", time_check.max())

# STEP 14: Check severity consistency

print("\n" + "=" * 50)
print("SEVERITY CONSISTENCY")

print("\nAccident Severity vs Fatalities:")
print(
    pd.crosstab(
        df2["Accident Severity"],
        df2["Number of Fatalities"]
    )
)

print("\nAccident Severity vs Casualties:")
print(
    pd.crosstab(
        df2["Accident Severity"],
        df2["Number of Casualties"]
    )
)

# STEP 15: Validate Year and Month

valid_months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

print("\n" + "=" * 50)
print("YEAR AND MONTH VALIDATION")

print(
    "Invalid years:",
    ((df2["Year"] < 2018) | (df2["Year"] > 2023)).sum()
)

print(
    "Invalid months:",
    (~df2["Month"].isin(valid_months)).sum()
)

print("\nYear range:")
print(df2["Year"].min(), "to", df2["Year"].max())

print("\nMonths present:")
print(df2["Month"].unique())

# STEP 16: Check State-City consistency

print("\n" + "=" * 50)
print("STATE-CITY CONSISTENCY")

known_city = df2[df2["City Name"] != "Unknown"]

print("Records with known city:", len(known_city))

print("\nCities by State:")
print(
    known_city.groupby("State Name")["City Name"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nSample State-City combinations:")
print(
    known_city[["State Name", "City Name"]]
    .drop_duplicates()
    .sort_values(["State Name", "City Name"])
    .head(50)
)

# STEP 17: Final duplicate and uniqueness check

print("\n" + "=" * 50)
print("FINAL DUPLICATE CHECK")

print("Total records:", len(df2))

print(
    "Duplicate complete rows:",
    df2.duplicated().sum()
)

# Check whether the dataset has an accident ID column
print(
    "\nColumn names containing 'ID':",
    [col for col in df2.columns if "id" in col.lower()]
)

# STEP 18: Save final cleaned dataset

output_file = "accident_prediction_india_cleaned.csv"

df2.to_csv(output_file, index=False)

print("\n" + "=" * 50)
print("FINAL DATASET SAVED")

print("File:", output_file)
print("Rows:", len(df2))
print("Columns:", len(df2.columns))

print("\nFinal columns:")
print(df2.columns.tolist())