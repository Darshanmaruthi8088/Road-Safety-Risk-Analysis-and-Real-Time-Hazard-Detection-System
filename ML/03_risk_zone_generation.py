import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("../data/indian_roads_cleaned.csv")

print("Dataset shape:", df.shape)


df["lat_grid"] = df["latitude"].round(1)
df["lon_grid"] = df["longitude"].round(1)


severity_weights = {
    "minor": 1,
    "major": 2,
    "fatal": 3
}

df["severity_weight"] = df["accident_severity"].map(severity_weights)


risk_zones = df.groupby(
    ["lat_grid", "lon_grid"]
).agg(
    accident_count=("accident_id", "count"),
    total_casualties=("casualties", "sum"),
    severity_weighted_score=("severity_weight", "sum")
).reset_index()


frequency_min = risk_zones["accident_count"].min()
frequency_max = risk_zones["accident_count"].max()

risk_zones["frequency_score"] = (
    (risk_zones["accident_count"] - frequency_min)
    / (frequency_max - frequency_min)
) * 100


severity_min = risk_zones["severity_weighted_score"].min()
severity_max = risk_zones["severity_weighted_score"].max()

risk_zones["severity_score"] = (
    (risk_zones["severity_weighted_score"] - severity_min)
    / (severity_max - severity_min)
) * 100


risk_zones["risk_score"] = (
    risk_zones["frequency_score"] * 0.5
    + risk_zones["severity_score"] * 0.5
)


def classify_risk(score):

    if score <= 25:
        return "Low"

    elif score <= 50:
        return "Moderate"

    elif score <= 75:
        return "High"

    else:
        return "Critical"


risk_zones["risk_level"] = risk_zones["risk_score"].apply(
    classify_risk
)


risk_zones = risk_zones.sort_values(
    "risk_score",
    ascending=False
)


print("\n========== RISK ZONE SUMMARY ==========")

print(
    risk_zones[
        [
            "lat_grid",
            "lon_grid",
            "accident_count",
            "total_casualties",
            "severity_weighted_score",
            "frequency_score",
            "severity_score",
            "risk_score",
            "risk_level"
        ]
    ].head(20)
)


print("\n========== RISK LEVEL COUNTS ==========")

print(
    risk_zones["risk_level"].value_counts()
)


risk_zones.to_csv(
    "../data/risk_zones.csv",
    index=False
)


print("\nRisk-zone dataset saved successfully.")


plt.figure(figsize=(10, 7))

plt.scatter(
    risk_zones["lon_grid"],
    risk_zones["lat_grid"],
    s=risk_zones["accident_count"] * 2,
    c=risk_zones["risk_score"],
    cmap="RdYlGn_r",
    alpha=0.7
)

plt.colorbar(label="Risk Score")

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.title("Road Accident Risk Zones")

plt.tight_layout()

plt.show()