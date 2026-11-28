"""RoadSafe API backed by the 11-column selected project dataset."""

import math

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:  # Supports both `uvicorn Backend.main:app` and running inside Backend/.
    from .filters_api import DATASET_PATH, _hotspots, _load_data, _summarize, router
except ImportError:
    from filters_api import DATASET_PATH, _hotspots, _load_data, _summarize, router


app = FastAPI(
    title="RoadSafe API",
    description="Accident severity summaries and approximate geographic hotspots",
    version="2.0.0",
)
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometres using the haversine formula."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    value = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    value = max(0.0, min(1.0, value))
    return 6371 * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


@app.get("/")
def home():
    return {
        "message": "RoadSafe API is running",
        "status": "success",
        "dataset": DATASET_PATH.name,
    }


@app.get("/risk")
def get_risk(latitude: float, longitude: float):
    if not -90 <= latitude <= 90:
        raise HTTPException(status_code=422, detail="Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="Longitude must be between -180 and 180")

    zones = _hotspots(_load_data())
    if not zones:
        return {"status": "error", "message": "No geographic hotspot data found"}

    nearest = min(
        zones,
        key=lambda zone: calculate_distance(
            latitude, longitude, zone["latitude"], zone["longitude"]
        ),
    )
    distance = calculate_distance(
        latitude, longitude, nearest["latitude"], nearest["longitude"]
    )
    return {
        "status": "success",
        "latitude": latitude,
        "longitude": longitude,
        **nearest,
        "distance_to_zone_km": round(distance, 2),
        "interpretation": "Severity-weighted summary of recorded accidents near this location; not exposure-adjusted risk.",
    }


@app.get("/risk-zones")
def get_risk_zones():
    zones = _hotspots(_load_data())
    return {"status": "success", "count": len(zones), "zones": zones}


@app.get("/statistics")
def get_statistics():
    stats, _ = _summarize(_load_data())
    return {"status": "success", **stats}


@app.get("/analysis")
def get_analysis():
    _, analysis = _summarize(_load_data())
    return {"status": "success", **analysis}
