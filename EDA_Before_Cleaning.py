"""Exploratory graphs for the original accident datasets, before cleaning.

Run from any directory with:
    python EDA_Before_Cleaning.py

The script reads the two original CSV files from the project's Data folder.
It does not modify the datasets or any existing EDA/cleaning files.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
roads = pd.read_csv(PROJECT_DIR / "Data" / "indian_roads_dataset.csv")
prediction = pd.read_csv(PROJECT_DIR / "Data" / "accident_prediction_india.csv")


def show_plot(fig):
    """Format and display one graph."""
    fig.tight_layout()
    plt.show()


def severity_percentages(data, group_column):
    """Calculate severity percentages for rows with the two required values."""
    chart_data = data[[group_column, "accident_severity"]].dropna().copy()
    chart_data["accident_severity"] = (
        chart_data["accident_severity"].astype(str).str.strip().str.lower()
    )
    result = pd.crosstab(
        chart_data[group_column],
        chart_data["accident_severity"],
        normalize="index",
    ) * 100
    return result.reindex(columns=["minor", "major", "fatal"], fill_value=0)


def plot_severity_percentages(table, title, xlabel, rotation=0):
    """Draw a 100% stacked chart of severity by category."""
    colors = {"minor": "#70ad47", "major": "#ed9b40", "fatal": "#c94747"}
    columns = [column for column in ["minor", "major", "fatal"] if column in table]
    ax = table[columns].plot(
        kind="bar",
        stacked=True,
        figsize=(10, 5),
        color=[colors[column] for column in columns],
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Percentage of records")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=rotation)
    ax.legend(title="Severity")
    show_plot(ax.figure)


def plot_counts(series, title, xlabel, ylabel, horizontal=False, top=None):
    """Draw category counts, optionally showing the most frequent values."""
    counts = series.dropna().value_counts()
    if top is not None:
        counts = counts.head(top)

    if horizontal:
        fig, ax = plt.subplots(figsize=(10, max(5, len(counts) * 0.32)))
        counts.sort_values().plot(kind="barh", ax=ax, color="#3273a8")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    else:
        fig, ax = plt.subplots(figsize=(9, 5))
        counts.plot(kind="bar", ax=ax, color="#3273a8")
        ax.set_xlabel(ylabel)
        ax.set_ylabel(xlabel)
        ax.tick_params(axis="x", rotation=25)

    ax.set_title(title)
    show_plot(fig)


print("BEFORE-CLEANING DATASET OVERVIEW")
print("Indian roads dataset:", roads.shape)
print("Accident prediction dataset:", prediction.shape)
print("\nMissing values in indian_roads_dataset.csv:")
print(roads.isna().sum()[roads.isna().sum() > 0])
print("\nMissing values in accident_prediction_india.csv:")
print(prediction.isna().sum()[prediction.isna().sum() > 0])
print("\nDuplicate rows in indian_roads_dataset.csv:", roads.duplicated().sum())
print("Duplicate rows in accident_prediction_india.csv:", prediction.duplicated().sum())


# GRAPH 1: Missing values in each original dataset.
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, data, title in [
    (axes[0], roads, "Indian roads dataset"),
    (axes[1], prediction, "Accident prediction dataset"),
]:
    missing = data.isna().sum()
    missing = missing[missing > 0].sort_values()
    if missing.empty:
        ax.text(0.5, 0.5, "No missing values", ha="center", va="center")
        ax.set_yticks([])
    else:
        missing.plot(kind="barh", ax=ax, color="#c65b52")
        ax.set_xlabel("Missing cells")
        ax.set_yticklabels(missing.index)
        for position, count in enumerate(missing.values):
            ax.text(count, position, f"  {count:,} ({count / len(data):.1%})", va="center")
    ax.set_title(title)
    ax.set_ylabel("Column")
fig.suptitle("Missing values in the original, uncleaned data")
show_plot(fig)


# GRAPHS 2–5: Overview of the original accident prediction dataset.
year_counts = prediction["Year"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8, 5))
year_counts.plot(kind="bar", ax=ax, color="#3273a8")
ax.set_title("Road Accident Records by Year — Before Cleaning")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Accident Records")
ax.tick_params(axis="x", rotation=0)
show_plot(fig)

plot_counts(
    prediction["State Name"],
    "Road Accident Records by State — Before Cleaning",
    "Number of Accident Records",
    "State",
    horizontal=True,
)

severity_counts = prediction["Accident Severity"].dropna().value_counts()
fig, ax = plt.subplots(figsize=(7, 5))
severity_counts.plot(kind="bar", ax=ax, color=["#70ad47", "#ed9b40", "#c94747"])
ax.set_title("Accident Severity — Before Cleaning")
ax.set_xlabel("Accident Severity")
ax.set_ylabel("Number of Accident Records")
ax.tick_params(axis="x", rotation=0)
show_plot(fig)

impact_data = pd.Series({
    "Casualties": prediction["Number of Casualties"].sum(),
    "Fatalities": prediction["Number of Fatalities"].sum(),
})
fig, ax = plt.subplots(figsize=(7, 5))
impact_data.plot(kind="bar", ax=ax, color=["#3273a8", "#c94747"])
ax.set_title("Total Casualties and Fatalities — Before Cleaning")
ax.set_xlabel("Impact Type")
ax.set_ylabel("Total Count")
ax.tick_params(axis="x", rotation=0)
show_plot(fig)


# GRAPHS 6–12: Causes, conditions, and accident timing in the raw roads data.
plot_counts(
    roads["cause"],
    "Accident Records by Cause — Before Cleaning",
    "Number of Accident Records",
    "Cause",
    horizontal=True,
)

plot_severity_percentages(
    severity_percentages(roads, "cause"),
    "Accident Severity Distribution by Cause",
    "Cause",
    rotation=20,
)
plot_severity_percentages(
    severity_percentages(roads, "road_type"),
    "Accident Severity Distribution by Road Type",
    "Road Type",
)
plot_severity_percentages(
    severity_percentages(roads, "weather"),
    "Accident Severity Distribution by Weather",
    "Weather Condition",
)
plot_severity_percentages(
    severity_percentages(roads, "traffic_density"),
    "Accident Severity Distribution by Traffic Density",
    "Traffic Density",
)
plot_severity_percentages(
    severity_percentages(roads, "visibility"),
    "Accident Severity Distribution by Visibility",
    "Visibility",
)

hour = pd.to_numeric(roads["hour"], errors="coerce")
time_period = pd.Series(index=roads.index, dtype="object")
time_period.loc[hour.between(0, 5)] = "Night"
time_period.loc[hour.between(6, 11)] = "Morning"
time_period.loc[hour.between(12, 17)] = "Afternoon"
time_period.loc[hour.between(18, 23)] = "Evening"
period_data = roads[["accident_severity"]].copy()
period_data["time_period"] = time_period
period_order = ["Morning", "Afternoon", "Evening", "Night"]
period_severity = severity_percentages(period_data, "time_period")
period_severity = period_severity.reindex(period_order)
plot_severity_percentages(
    period_severity,
    "Accident Severity Distribution by Time Period",
    "Time Period",
)

hour_counts = hour.dropna().astype(int).value_counts().reindex(range(24), fill_value=0)
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(hour_counts.index, hour_counts.values, marker="o", color="#3273a8")
ax.set_title("Accident Records by Hour — Before Cleaning")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Number of Accident Records")
ax.set_xticks(range(24))
ax.grid(True, alpha=0.3)
show_plot(fig)


# GRAPHS 13–19: Peak hours, numerical relationships, and risk scores.
peak_data = roads[["is_peak_hour", "accident_severity"]].copy()
peak_data["peak_period"] = peak_data["is_peak_hour"].map({0: "Off Peak", 1: "Peak"})
peak_severity = severity_percentages(peak_data, "peak_period")
peak_severity = peak_severity.reindex(["Off Peak", "Peak"])
plot_severity_percentages(
    peak_severity,
    "Accident Severity: Peak vs Non-Peak Hours",
    "Peak Hour (0 = No, 1 = Yes)",
)

vehicle_order = sorted(roads["vehicles_involved"].dropna().unique())
vehicle_severity = severity_percentages(roads, "vehicles_involved")
vehicle_severity = vehicle_severity.reindex(vehicle_order)
plot_severity_percentages(
    vehicle_severity,
    "Accident Severity Distribution by Vehicles Involved",
    "Vehicles Involved",
)

numeric_columns = [
    "lanes",
    "temperature",
    "vehicles_involved",
    "casualties",
    "risk_score",
    "hour",
]
correlation_matrix = roads[numeric_columns].corr()
fig, ax = plt.subplots(figsize=(9, 7))
image = ax.imshow(correlation_matrix, cmap="coolwarm", vmin=-1, vmax=1)
fig.colorbar(image, ax=ax, label="Correlation")
ax.set_xticks(range(len(numeric_columns)), numeric_columns, rotation=45, ha="right")
ax.set_yticks(range(len(numeric_columns)), numeric_columns)
for row in range(len(numeric_columns)):
    for column in range(len(numeric_columns)):
        ax.text(column, row, f"{correlation_matrix.iloc[row, column]:.2f}", ha="center", va="center")
ax.set_title("Correlation Matrix of Numerical Features")
show_plot(fig)

print("\nRisk-score summary before cleaning:")
print(roads["risk_score"].describe())
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(roads["risk_score"].dropna(), bins=20, color="#3273a8", edgecolor="white")
ax.set_title("Risk Score Distribution — Before Cleaning")
ax.set_xlabel("Risk Score")
ax.set_ylabel("Number of Accident Records")
show_plot(fig)

risk_by_cause = roads.groupby("cause")["risk_score"].mean().sort_values()
fig, ax = plt.subplots(figsize=(9, 5))
risk_by_cause.plot(kind="bar", ax=ax, color="#3273a8")
ax.set_title("Average Risk Score by Accident Cause")
ax.set_xlabel("Cause")
ax.set_ylabel("Average Risk Score")
ax.tick_params(axis="x", rotation=25)
show_plot(fig)

weather_risk = roads[["weather", "risk_score"]].dropna()
fig, ax = plt.subplots(figsize=(9, 5))
weather_risk.boxplot(column="risk_score", by="weather", ax=ax)
ax.set_title("Risk Score Distribution by Weather")
fig.suptitle("")
ax.set_xlabel("Weather")
ax.set_ylabel("Risk Score")
ax.tick_params(axis="x", rotation=15)
show_plot(fig)


# GRAPHS 20–23: Geographic distribution and hotspots.
coordinates = roads[["longitude", "latitude"]].dropna()
fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(
    coordinates["longitude"],
    coordinates["latitude"],
    alpha=0.3,
    s=10,
    color="#3273a8",
)
ax.set_title("Geographical Distribution of Accident Records")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
show_plot(fig)

city_counts = roads["city"].dropna().value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
city_counts.sort_values().plot(kind="barh", ax=ax, color="#3273a8")
ax.set_title("Top 10 Cities by Accident Records")
ax.set_xlabel("Number of Accident Records")
ax.set_ylabel("City")
show_plot(fig)

hotspot_data = roads[["latitude", "longitude"]].dropna().copy()
hotspot_data["lat_grid"] = hotspot_data["latitude"].round(1)
hotspot_data["lon_grid"] = hotspot_data["longitude"].round(1)
hotspots = (
    hotspot_data.groupby(["lat_grid", "lon_grid"])
    .size()
    .reset_index(name="accident_count")
    .sort_values("accident_count", ascending=False)
    .head(15)
)
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(
    hotspots["lon_grid"],
    hotspots["lat_grid"],
    s=hotspots["accident_count"] / 2,
    alpha=0.7,
    color="#c65b52",
)
for _, row in hotspots.iterrows():
    ax.text(row["lon_grid"], row["lat_grid"], str(row["accident_count"]), fontsize=8)
ax.set_title("Top Geographic Accident Hotspots")
ax.set_xlabel("Longitude (rounded to 0.1 degree)")
ax.set_ylabel("Latitude (rounded to 0.1 degree)")
ax.grid(True, alpha=0.3)
show_plot(fig)

city_severity = severity_percentages(roads, "city")
city_order = roads["city"].dropna().value_counts().head(10).index
city_severity = city_severity.reindex(city_order)
plot_severity_percentages(
    city_severity,
    "Accident Severity Distribution by City",
    "City",
    rotation=25,
)
