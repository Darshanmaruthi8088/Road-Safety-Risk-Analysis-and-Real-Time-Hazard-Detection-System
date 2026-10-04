from pathlib import Path
from functools import lru_cache

import pandas as pd
from fastapi import APIRouter, Query

router = APIRouter(tags=["Dashboard Filters"])


def _find_dataset() -> Path:
    """Find the cleaned RoadSafe accident CSV in common project locations."""
    backend_dir = Path(__file__).resolve().parent
    candidates = [
        backend_dir.parent / "data" / "indian_roads_cleaned.csv",
        backend_dir / "data" / "indian_roads_cleaned.csv",
        backend_dir.parent / "indian_roads_cleaned.csv",
        Path.cwd().parent / "data" / "indian_roads_cleaned.csv",
        Path.cwd() / "data" / "indian_roads_cleaned.csv",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not find indian_roads_cleaned.csv. Put it in the project's "
        "data folder: data/indian_roads_cleaned.csv"
    )


@lru_cache(maxsize=1)
def _load_data() -> pd.DataFrame:
    """Load and lightly normalize the dataset once per server process."""
    df = pd.read_csv(_find_dataset())

    required = {
        "city",
        "accident_severity",
        "weather",
        "hour",
        "latitude",
        "longitude",
        "risk_score",
        "cause",
        "road_type",
        "traffic_density",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(sorted(missing))}"
        )

    # Normalize text columns so filters and counts use consistent labels.
    text_columns = [
        "city",
        "accident_severity",
        "weather",
        "cause",
        "road_type",
        "traffic_density",
    ]
    for column in text_columns:
        df[column] = df[column].fillna("Unknown").astype(str).str.strip()

    # Keep severity labels consistent (minor / major / fatal).
    df["accident_severity"] = df["accident_severity"].str.lower()

    df["hour"] = pd.to_numeric(df["hour"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0)

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


def _counts(series):
    """Return stable JSON-safe category counts."""
    clean = series.fillna("Unknown").astype(str)
    return {
        str(key): int(value)
        for key, value in clean.value_counts().sort_index().items()
    }


def _summarize(df: pd.DataFrame):
    total = int(len(df))

    severity = df["accident_severity"].fillna("Unknown").astype(str).str.lower()
    severity_counts = severity.value_counts()

    # Include every severity field expected by the React dashboard.
    minor = int(severity_counts.get("minor", 0))
    major = int(severity_counts.get("major", 0))
    fatal = int(severity_counts.get("fatal", 0))

    # Estimate geographic zones from rounded coordinates in the filtered data.
    # These are approximate dataset-derived zones, not verified real-world hotspots.
    valid_coordinates = df.dropna(subset=["latitude", "longitude"]).copy()

    if not valid_coordinates.empty:
        valid_coordinates["lat_cell"] = valid_coordinates["latitude"].round(1)
        valid_coordinates["lon_cell"] = valid_coordinates["longitude"].round(1)

        zone_scores = valid_coordinates.groupby(
            ["lat_cell", "lon_cell"]
        )["risk_score"].mean()

        risk_levels = {
            "low": int((zone_scores < 0.25).sum()),
            "moderate": int(
                ((zone_scores >= 0.25) & (zone_scores < 0.5)).sum()
            ),
            "high": int(
                ((zone_scores >= 0.5) & (zone_scores < 0.75)).sum()
            ),
            "critical": int((zone_scores >= 0.75).sum()),
        }
        total_zones = int(len(zone_scores))
    else:
        risk_levels = {
            "low": 0,
            "moderate": 0,
            "high": 0,
            "critical": 0,
        }
        total_zones = 0

    hourly_series = pd.to_numeric(df["hour"], errors="coerce").dropna()
    hourly_series = hourly_series[hourly_series.between(0, 23)].astype(int)
    hourly = {
        str(hour): int((hourly_series == hour).sum())
        for hour in range(24)
    }

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
        "total_risk_zones": total_zones,
        "risk_levels": risk_levels,
    }

    analysis = {
        "causes": _counts(df["cause"]),
        "weather": _counts(df["weather"]),
        "road_types": _counts(df["road_type"]),
        "traffic_density": _counts(df["traffic_density"]),
        "hourly": hourly,
        "time_period": time_period,
        "severity": {
            "minor": minor,
            "major": major,
            "fatal": fatal,
            **{
                key: value
                for key, value in _counts(severity).items()
                if key not in {"minor", "major", "fatal"}
            },
        },
    }

    return stats, analysis


@router.get("/filtered-dashboard")
def filtered_dashboard(
    city: str = Query("All"),
    severity: str = Query("All"),
    weather: str = Query("All"),
    time_period: str = Query("All"),
):
    df = _load_data()
    filtered = df.copy()

    if city != "All":
        filtered = filtered[filtered["city"] == city]

    if severity != "All":
        filtered = filtered[filtered["accident_severity"] == severity.lower()]

    if weather != "All":
        filtered = filtered[filtered["weather"].str.lower() == weather.lower()]

    if time_period != "All":
        filtered = filtered[filtered["hour"].map(_period) == time_period]

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
    }


@router.get("/filtered-risk-zones")
def filtered_risk_zones(
    city: str = Query("All"),
    severity: str = Query("All"),
    weather: str = Query("All"),
    time_period: str = Query("All"),
):
    df = _load_data()
    filtered = df.copy()

    if city != "All":
        filtered = filtered[filtered["city"] == city]

    if severity != "All":
        filtered = filtered[
            filtered["accident_severity"] == severity.strip().lower()
        ]

    if weather != "All":
        filtered = filtered[
            filtered["weather"].str.lower() == weather.strip().lower()
        ]

    if time_period != "All":
        filtered = filtered[
            filtered["hour"].map(_period) == time_period
        ]

    zones = filtered.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    if zones.empty:
        return {"status": "success", "count": 0, "zones": []}

    zones["lat_grid"] = zones["latitude"].round(1)
    zones["lon_grid"] = zones["longitude"].round(1)

    result = []

    for (lat, lon), group in zones.groupby(["lat_grid", "lon_grid"]):
        score = float(group["risk_score"].mean())

        if score >= 0.75:
            level = "Critical"
        elif score >= 0.5:
            level = "High"
        elif score >= 0.25:
            level = "Moderate"
        else:
            level = "Low"

        casualties = (
            pd.to_numeric(group["casualties"], errors="coerce").fillna(0).sum()
            if "casualties" in group.columns
            else 0
        )

        result.append({
            "latitude": float(lat),
            "longitude": float(lon),
            "accident_count": int(len(group)),
            "total_casualties": int(casualties),
            "risk_score": round(score, 2),
            "risk_level": level,
        })

    return {
        "status": "success",
        "count": len(result),
        "zones": result,
    }
