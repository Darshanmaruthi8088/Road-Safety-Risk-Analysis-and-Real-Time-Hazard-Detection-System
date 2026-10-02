import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned datasets
df1 = pd.read_csv("../data/indian_roads_cleaned.csv")
df2 = pd.read_csv("../data/accident_prediction_india_cleaned.csv")

print("Dataset 1 shape:", df1.shape)
print("Dataset 2 shape:", df2.shape)

# ==========================================
# EDA STEP 1: ACCIDENTS BY YEAR
# ==========================================

year_counts = df2["Year"].value_counts().sort_index()

print("\n" + "=" * 50)
print("ACCIDENTS BY YEAR")
print("=" * 50)

print(year_counts)

print("\nPercentage distribution:")
print(
    (year_counts / len(df2) * 100).round(2)
)

plt.figure(figsize=(8, 5))

plt.bar(
    year_counts.index.astype(str),
    year_counts.values
)

plt.title("Road Accident Records by Year")
plt.xlabel("Year")
plt.ylabel("Number of Accident Records")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 2: ACCIDENTS BY STATE
# ==========================================

state_counts = (
    df2["State Name"]
    .value_counts()
    .sort_values(ascending=False)
)

print("\n" + "=" * 50)
print("ACCIDENTS BY STATE")
print("=" * 50)

print(state_counts)

plt.figure(figsize=(10, 8))

plt.barh(
    state_counts.index,
    state_counts.values
)

plt.title("Road Accident Records by State")
plt.xlabel("Number of Accident Records")
plt.ylabel("State")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 3: ACCIDENT SEVERITY
# ==========================================

severity_counts = (
    df2["Accident Severity"]
    .value_counts()
)

print("\n" + "=" * 50)
print("ACCIDENT SEVERITY")
print("=" * 50)

print(severity_counts)

print("\nPercentage distribution:")
print(
    (severity_counts / len(df2) * 100).round(2)
)

plt.figure(figsize=(7, 5))

plt.bar(
    severity_counts.index,
    severity_counts.values
)

plt.title("Accident Severity Distribution")
plt.xlabel("Accident Severity")
plt.ylabel("Number of Accident Records")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 4: CASUALTIES AND FATALITIES
# ==========================================

print("\n" + "=" * 50)
print("CASUALTIES AND FATALITIES")
print("=" * 50)

print("\nCasualties:")
print(df2["Number of Casualties"].describe())

print("\nFatalities:")
print(df2["Number of Fatalities"].describe())

print("\nTotal casualties:",
      df2["Number of Casualties"].sum())

print("Total fatalities:",
      df2["Number of Fatalities"].sum())

impact_data = [
    df2["Number of Casualties"].sum(),
    df2["Number of Fatalities"].sum()
]

labels = [
    "Casualties",
    "Fatalities"
]

plt.figure(figsize=(7, 5))

plt.bar(labels, impact_data)

plt.title("Total Casualties and Fatalities")
plt.xlabel("Impact Type")
plt.ylabel("Count")

plt.tight_layout()
plt.show()


# ==========================================
# EDA STEP 5: ACCIDENT CAUSES
# ==========================================

cause_counts = (
    df1["cause"]
    .value_counts()
    .sort_values(ascending=False)
)

print("\n" + "=" * 50)
print("ACCIDENT CAUSES")
print("=" * 50)

print(cause_counts)

print("\nPercentage distribution:")
print(
    (cause_counts / len(df1) * 100).round(2)
)

plt.figure(figsize=(9, 5))

plt.bar(
    cause_counts.index,
    cause_counts.values
)

plt.title("Accident Records by Cause")
plt.xlabel("Cause")
plt.ylabel("Number of Accident Records")

plt.xticks(rotation=30)

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 6: CAUSE VS ACCIDENT SEVERITY
# ==========================================

cause_severity = pd.crosstab(
    df1["cause"],
    df1["accident_severity"]
)

print("\n" + "=" * 50)
print("CAUSE VS ACCIDENT SEVERITY")
print("=" * 50)

print(cause_severity)

cause_severity_percentage = (
    pd.crosstab(
        df1["cause"],
        df1["accident_severity"],
        normalize="index"
    ) * 100
)

print("\nPercentage distribution within each cause:")
print(cause_severity_percentage.round(2))

# ==========================================
# EDA STEP 7: ROAD TYPE VS ACCIDENT SEVERITY
# ==========================================

road_severity = pd.crosstab(
    df1["road_type"],
    df1["accident_severity"]
)

print("\n" + "=" * 50)
print("ROAD TYPE VS ACCIDENT SEVERITY")
print("=" * 50)

print(road_severity)

road_severity_percentage = (
    pd.crosstab(
        df1["road_type"],
        df1["accident_severity"],
        normalize="index"
    ) * 100
)

print("\nPercentage distribution within each road type:")
print(road_severity_percentage.round(2))

road_severity_percentage.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Accident Severity Distribution by Road Type")
plt.xlabel("Road Type")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 8: WEATHER VS ACCIDENT SEVERITY
# ==========================================

weather_severity = pd.crosstab(
    df1["weather"],
    df1["accident_severity"]
)

print("\n" + "=" * 50)
print("WEATHER VS ACCIDENT SEVERITY")
print("=" * 50)

print(weather_severity)

weather_severity_percentage = (
    pd.crosstab(
        df1["weather"],
        df1["accident_severity"],
        normalize="index"
    ) * 100
)

print("\nPercentage distribution within each weather condition:")
print(weather_severity_percentage.round(2))

weather_severity_percentage.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Accident Severity Distribution by Weather")
plt.xlabel("Weather Condition")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 9: TRAFFIC DENSITY VS ACCIDENT SEVERITY
# ==========================================

traffic_severity = pd.crosstab(
    df1["traffic_density"],
    df1["accident_severity"]
)

print("\n" + "=" * 50)
print("TRAFFIC DENSITY VS ACCIDENT SEVERITY")
print("=" * 50)

print(traffic_severity)

traffic_severity_percentage = (
    pd.crosstab(
        df1["traffic_density"],
        df1["accident_severity"],
        normalize="index"
    ) * 100
)

print("\nPercentage distribution within each traffic density:")
print(traffic_severity_percentage.round(2))

traffic_severity_percentage.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Accident Severity Distribution by Traffic Density")
plt.xlabel("Traffic Density")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 10: VISIBILITY VS ACCIDENT SEVERITY
# ==========================================

visibility_severity = pd.crosstab(
    df1["visibility"],
    df1["accident_severity"]
)

print("\n" + "=" * 50)
print("VISIBILITY VS ACCIDENT SEVERITY")
print("=" * 50)

print(visibility_severity)

visibility_severity_percentage = (
    pd.crosstab(
        df1["visibility"],
        df1["accident_severity"],
        normalize="index"
    ) * 100
)

print("\nPercentage distribution within each visibility level:")
print(visibility_severity_percentage.round(2))

visibility_severity_percentage.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Accident Severity Distribution by Visibility")
plt.xlabel("Visibility")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 11: TIME PERIOD VS ACCIDENT SEVERITY
# ==========================================

def time_period(hour):
    if 0 <= hour <= 5:
        return "Night"
    elif 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 17:
        return "Afternoon"
    else:
        return "Evening"

df1["time_period"] = df1["hour"].apply(time_period)

time_severity_percentage = (
    pd.crosstab(
        df1["time_period"],
        df1["accident_severity"],
        normalize="index"
    ) * 100
)

print("\n" + "=" * 50)
print("TIME PERIOD VS ACCIDENT SEVERITY")
print("=" * 50)

print(time_severity_percentage.round(2))

time_order = [
    "Morning",
    "Afternoon",
    "Evening",
    "Night"
]

time_severity_percentage = (
    time_severity_percentage
    .reindex(time_order)
)

time_severity_percentage.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Accident Severity Distribution by Time Period")
plt.xlabel("Time Period")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 12: ACCIDENTS BY HOUR
# ==========================================

hour_counts = (
    df1["hour"]
    .value_counts()
    .sort_index()
)

print("\n" + "=" * 50)
print("ACCIDENT RECORDS BY HOUR")
print("=" * 50)

print(hour_counts)

plt.figure(figsize=(11, 5))

plt.plot(
    hour_counts.index,
    hour_counts.values,
    marker="o"
)

plt.title("Accident Records by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Accident Records")
plt.xticks(range(24))

plt.grid(True)

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 13: PEAK HOUR VS ACCIDENT SEVERITY
# ==========================================

peak_severity = pd.crosstab(
    df1["is_peak_hour"],
    df1["accident_severity"],
    normalize="index"
) * 100

print("\n" + "=" * 50)
print("PEAK HOUR VS ACCIDENT SEVERITY")
print("=" * 50)

print(peak_severity.round(2))

peak_severity.plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Accident Severity Distribution: Peak vs Non-Peak Hours")
plt.xlabel("Peak Hour (0 = No, 1 = Yes)")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 14: VEHICLES INVOLVED VS ACCIDENT SEVERITY
# ==========================================

vehicle_severity = pd.crosstab(
    df1["vehicles_involved"],
    df1["accident_severity"],
    normalize="index"
) * 100

print("\n" + "=" * 50)
print("VEHICLES INVOLVED VS ACCIDENT SEVERITY")
print("=" * 50)

print(vehicle_severity.round(2))

vehicle_severity.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Accident Severity Distribution by Vehicles Involved")
plt.xlabel("Number of Vehicles Involved")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=0)
plt.legend(title="Severity")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 15: NUMERICAL CORRELATION
# ==========================================

numeric_columns = [
    "lanes",
    "temperature",
    "vehicles_involved",
    "casualties",
    "risk_score",
    "hour"
]

correlation_matrix = df1[numeric_columns].corr()

print("\n" + "=" * 50)
print("NUMERICAL CORRELATION MATRIX")
print("=" * 50)

print(correlation_matrix.round(2))

plt.figure(figsize=(9, 7))

plt.imshow(
    correlation_matrix,
    aspect="auto"
)

plt.colorbar(label="Correlation")

plt.xticks(
    range(len(numeric_columns)),
    numeric_columns,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(numeric_columns)),
    numeric_columns
)

plt.title("Correlation Matrix of Numerical Features")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 16: RISK SCORE DISTRIBUTION
# ==========================================

print("\n" + "=" * 50)
print("RISK SCORE DISTRIBUTION")
print("=" * 50)

print(df1["risk_score"].describe())

print("\nRisk score values:")
print(df1["risk_score"].value_counts().sort_index())

plt.figure(figsize=(9, 5))

plt.hist(
    df1["risk_score"],
    bins=20
)

plt.title("Distribution of Risk Scores")
plt.xlabel("Risk Score")
plt.ylabel("Number of Accident Records")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 17: RISK SCORE BY ACCIDENT FACTORS
# ==========================================

risk_by_cause = df1.groupby("cause")["risk_score"].agg(
    ["mean", "min", "max"]
)

risk_by_road = df1.groupby("road_type")["risk_score"].agg(
    ["mean", "min", "max"]
)

risk_by_weather = df1.groupby("weather")["risk_score"].agg(
    ["mean", "min", "max"]
)

print("\n" + "=" * 50)
print("RISK SCORE BY CAUSE")
print("=" * 50)
print(risk_by_cause.round(3))

print("\n" + "=" * 50)
print("RISK SCORE BY ROAD TYPE")
print("=" * 50)
print(risk_by_road.round(3))

print("\n" + "=" * 50)
print("RISK SCORE BY WEATHER")
print("=" * 50)
print(risk_by_weather.round(3))

risk_by_cause["mean"].sort_values().plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Average Risk Score by Accident Cause")
plt.xlabel("Cause")
plt.ylabel("Average Risk Score")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 18: RISK SCORE VS WEATHER
# ==========================================

print("\n" + "=" * 50)
print("RISK SCORE VS WEATHER")
print("=" * 50)

risk_weather = (
    df1.groupby("weather")["risk_score"]
    .describe()
)

print(risk_weather.round(3))

plt.figure(figsize=(8, 5))

df1.boxplot(
    column="risk_score",
    by="weather"
)

plt.title("Risk Score Distribution by Weather")
plt.suptitle("")
plt.xlabel("Weather")
plt.ylabel("Risk Score")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 19: GEOGRAPHIC DISTRIBUTION
# ==========================================

print("\n" + "=" * 50)
print("GEOGRAPHIC DISTRIBUTION")
print("=" * 50)

print("\nLatitude statistics:")
print(df1["latitude"].describe())

print("\nLongitude statistics:")
print(df1["longitude"].describe())

print("\nInvalid coordinates:")

invalid_coordinates = (
    (df1["latitude"] < 6) |
    (df1["latitude"] > 38) |
    (df1["longitude"] < 68) |
    (df1["longitude"] > 98)
)

print("Invalid coordinate records:",
      invalid_coordinates.sum())

plt.figure(figsize=(9, 7))

plt.scatter(
    df1["longitude"],
    df1["latitude"],
    alpha=0.3,
    s=10
)

plt.title("Geographical Distribution of Accident Records")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 20: ACCIDENT HOTSPOTS BY CITY
# ==========================================

city_counts = (
    df1["city"]
    .value_counts()
    .sort_values(ascending=False)
)

print("\n" + "=" * 50)
print("ACCIDENT RECORDS BY CITY")
print("=" * 50)

print(city_counts)

print("\nTop 10 cities:")
print(city_counts.head(10))

top_cities = city_counts.head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    top_cities.index[::-1],
    top_cities.values[::-1]
)

plt.title("Top 10 Cities by Accident Records")
plt.xlabel("Number of Accident Records")
plt.ylabel("City")

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 21: GEOGRAPHIC HOTSPOT ANALYSIS
# ==========================================

df1["lat_grid"] = df1["latitude"].round(1)
df1["lon_grid"] = df1["longitude"].round(1)

hotspots = (
    df1.groupby(["lat_grid", "lon_grid"])
    .size()
    .reset_index(name="accident_count")
    .sort_values("accident_count", ascending=False)
)

print("\n" + "=" * 50)
print("TOP GEOGRAPHIC ACCIDENT HOTSPOTS")
print("=" * 50)

print(hotspots.head(15))

top_hotspots = hotspots.head(15)

plt.figure(figsize=(10, 7))

plt.scatter(
    top_hotspots["lon_grid"],
    top_hotspots["lat_grid"],
    s=top_hotspots["accident_count"] / 2,
    alpha=0.7
)

for _, row in top_hotspots.iterrows():
    plt.text(
        row["lon_grid"],
        row["lat_grid"],
        str(row["accident_count"]),
        fontsize=8
    )

plt.title("Top Geographic Accident Hotspots")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)

plt.tight_layout()
plt.show()

# ==========================================
# EDA STEP 22: CITY VS ACCIDENT SEVERITY
# ==========================================

city_severity = pd.crosstab(
    df1["city"],
    df1["accident_severity"],
    normalize="index"
) * 100

print("\n" + "=" * 50)
print("CITY VS ACCIDENT SEVERITY (%)")
print("=" * 50)

print(city_severity.round(2))

city_severity.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Accident Severity Distribution by City")
plt.xlabel("City")
plt.ylabel("Percentage of Accident Records")
plt.xticks(rotation=45)
plt.legend(title="Severity")
plt.tight_layout()
plt.show()