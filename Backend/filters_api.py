"""Filtered dashboard and geographic hotspot endpoints for the selected CSV."""

from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Query

router = APIRouter(tags=["Dashboard Filters"])

DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "Data"
    / "indian_roads_project_selected.csv"
)
REQUIRED_COLUMNS = {
    "date",
    "city",
    "latitude",
    "longitude",
    "hour",
    "road_type",
    "weather",
    "traffic_density",
    "cause",
    "casualties",
    "accident_severity",
}
SEVERITY_WEIGHT = {"minor": 1, "major": 2, "fatal": 3}
GRID_DECIMALS = 1


@lru_cache(maxsize=1)
def _load_data() -> pd.DataFrame:
    """Load the project's selected dataset once per backend process."""
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Selected dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(
            "Selected dataset is missing required columns: "
            + ", ".join(sorted(missing))
        )

    for column in [
        "city",
        "accident_severity",
        "weather",
        "cause",
        "road_type",
        "traffic_density",
    ]:
        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
        )

    for column in ["accident_severity", "weather", "cause", "road_type", "traffic_density"]:
        df[column] = df[column].str.lower()

    for column in ["hour", "latitude", "longitude", "casualties"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["casualties"] = df["casualties"].fillna(0).clip(lower=0)
    return df


def _period(hour):
    """Map an hour value to the dashboard's time-of-day category."""
    if pd.isna(hour):
        return "Unknown"

    hour = int(hour)
    if 5 <= hour < 12:
        return "Morning"
    if 12 <= hour < 17:
        return "Afternoon"
    if 17 <= hour < 21:
        return "Evening"
    return "Night"


def _counts(series: pd.Series) -> dict[str, int]:
    clean = series.fillna("Unknown").astype(str)
    return {str(key): int(value) for key, value in clean.value_counts().sort_index().items()}


def _risk_level(score: float) -> str:
    if score < 0.4:
        return "Low"
    if score < 0.6:
        return "Moderate"
    if score < 0.8:
        return "High"
    return "Critical"


def _hotspots(df: pd.DataFrame) -> list[dict]:
    """Aggregate approximate 0.1-degree cells using location and severity.

    The severity index is the mean class weight (minor=1, major=2, fatal=3),
    normalized to 0..1. It describes recorded severity mix, not exposure-adjusted
    real-world crash risk.
    """
    zones = df.dropna(subset=["latitude", "longitude"]).copy()
    zones = zones[
        zones["latitude"].between(-90, 90)
        & zones["longitude"].between(-180, 180)
        & zones["accident_severity"].isin(SEVERITY_WEIGHT)
    ]
    if zones.empty:
        return []

    zones["lat_grid"] = zones["latitude"].round(GRID_DECIMALS)
    zones["lon_grid"] = zones["longitude"].round(GRID_DECIMALS)
    zones["severity_weight"] = zones["accident_severity"].map(SEVERITY_WEIGHT)
    output = []

    for (latitude, longitude), group in zones.groupby(
        ["lat_grid", "lon_grid"], sort=True
    ):
        counts = group["accident_severity"].value_counts()
        weighted_total = int(group["severity_weight"].sum())
        average_weight = weighted_total / len(group)
        score = average_weight / max(SEVERITY_WEIGHT.values())
        output.append(
            {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "accident_count": int(len(group)),
                "minor_count": int(counts.get("minor", 0)),
                "major_count": int(counts.get("major", 0)),
                "fatal_count": int(counts.get("fatal", 0)),
                "total_casualties": int(group["casualties"].sum()),
                "severity_weighted_score": weighted_total,
                "average_severity_weight": round(float(average_weight), 3),
                "risk_score": round(float(score), 3),
                "risk_level": _risk_level(score),
            }
        )

    return output


def _summarize(df: pd.DataFrame) -> tuple[dict, dict]:
    total = int(len(df))
    severity_counts = df["accident_severity"].value_counts()
    minor = int(severity_counts.get("minor", 0))
    major = int(severity_counts.get("major", 0))
    fatal = int(severity_counts.get("fatal", 0))
    hotspots = _hotspots(df)
    risk_counts = pd.Series(
        [zone["risk_level"].lower() for zone in hotspots], dtype="string"
    ).value_counts()

    hourly_series = pd.to_numeric(df["hour"], errors="coerce")
    hourly_series = hourly_series[hourly_series.between(0, 23)].astype(int)
    hourly = {str(hour): int((hourly_series == hour).sum()) for hour in range(24)}
    periods = df["hour"].map(_period).value_counts()
    time_period = {
        name: int(periods.get(name, 0))
        for name in ["Morning", "Afternoon", "Evening", "Night"]
    }

    stats = {
        "total_accidents": total,
        "minor_accidents": minor,
        "major_accidents": major,
        "fatal_accidents": fatal,
        "total_casualties": int(df["casualties"].sum()),
        "total_risk_zones": len(hotspots),
        "risk_levels": {
            level: int(risk_counts.get(level, 0))
            for level in ["low", "moderate", "high", "critical"]
        },
    }
    analysis = {
        "causes": _counts(df["cause"]),
        "weather": _counts(df["weather"]),
        "road_types": _counts(df["road_type"]),
        "traffic_density": _counts(df["traffic_density"]),
        "hourly": hourly,
        "time_period": time_period,
        "severity": {"minor": minor, "major": major, "fatal": fatal},
    }
    return stats, analysis


def _apply_filters(df: pd.DataFrame, city: str, severity: str, weather: str, time_period: str):
    filtered = df
    if city.strip().lower() != "all":
        filtered = filtered[filtered["city"].str.lower() == city.strip().lower()]
    if severity.strip().lower() != "all":
        filtered = filtered[
            filtered["accident_severity"] == severity.strip().lower()
        ]
    if weather.strip().lower() != "all":
        filtered = filtered[filtered["weather"] == weather.strip().lower()]
    if time_period.strip().lower() != "all":
        filtered = filtered[
            filtered["hour"].map(_period).str.lower() == time_period.strip().lower()
        ]
    return filtered


@router.get("/filtered-dashboard")
def filtered_dashboard(
    city: str = Query("All"),
    severity: str = Query("All"),
    weather: str = Query("All"),
    time_period: str = Query("All"),
):
    df = _load_data()
    filtered = _apply_filters(df, city, severity, weather, time_period)
    stats, analysis = _summarize(filtered)
    return {
        "statistics": stats,
        "analysis": analysis,
        "filter_options": {
            "cities": sorted(df["city"].unique().tolist()),
            "severities": sorted(df["accident_severity"].unique().tolist()),
            "weather": sorted(df["weather"].unique().tolist()),
            "time_periods": ["Morning", "Afternoon", "Evening", "Night"],
        },
        "applied_filters": {
            "city": city,
            "severity": severity,
            "weather": weather,
            "time_period": time_period,
        },
        "dataset": DATASET_PATH.name,
        "hotspot_method": "0.1-degree coordinate cells; severity-weighted index",
    }


@router.get("/filtered-risk-zones")
def filtered_risk_zones(
    city: str = Query("All"),
    severity: str = Query("All"),
    weather: str = Query("All"),
    time_period: str = Query("All"),
):
    filtered = _apply_filters(_load_data(), city, severity, weather, time_period)
    zones = _hotspots(filtered)
    return {"status": "success", "count": len(zones), "zones": zones}
