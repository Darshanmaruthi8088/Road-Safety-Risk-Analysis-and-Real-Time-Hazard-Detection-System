
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import math


app = FastAPI(
    title="RoadSafe API",
    description="Road Accident Risk Analysis and Monitoring System",
    version="1.0.0"
)

from filters_api import router as filters_router

app.include_router(filters_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


accident_data = pd.read_csv(
    "../data/indian_roads_cleaned.csv"
)

risk_zones = pd.read_csv(
    "../data/risk_zones.csv"
)


def calculate_distance(lat1, lon1, lat2, lon2):

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    a = max(0.0, min(1.0, a))

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    earth_radius = 6371

    return earth_radius * c


@app.get("/")
def home():

    return {
        "message": "RoadSafe API is running",
        "status": "success"
    }


@app.get("/risk")
def get_risk(
    latitude: float,
    longitude: float
):

    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=422,
            detail="Latitude must be between -90 and 90"
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=422,
            detail="Longitude must be between -180 and 180"
        )

    nearest_zone = None
    nearest_distance = float("inf")


    for _, zone in risk_zones.iterrows():

        distance = calculate_distance(
            latitude,
            longitude,
            float(zone["lat_grid"]),
            float(zone["lon_grid"])
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest_zone = zone


    if nearest_zone is None:

        return {
            "status": "error",
            "message": "No risk zone found"
        }


    return {

        "status": "success",

        "latitude": latitude,

        "longitude": longitude,

        "risk_score": round(
            float(nearest_zone["risk_score"]),
            2
        ),

        "risk_level": str(nearest_zone["risk_level"]),

        "accident_count": int(
            nearest_zone["accident_count"]
        ),

        "total_casualties": int(
            nearest_zone["total_casualties"]
        ),

        "severity_weighted_score": int(
            nearest_zone["severity_weighted_score"]
        ),

        "distance_to_zone_km": round(
            nearest_distance,
            2
        )
    }


@app.get("/risk-zones")
def get_risk_zones():

    zones = []


    for _, zone in risk_zones.iterrows():

        zones.append({

            "latitude": float(
                zone["lat_grid"]
            ),

            "longitude": float(
                zone["lon_grid"]
            ),

            "accident_count": int(
                zone["accident_count"]
            ),

            "total_casualties": int(
                zone["total_casualties"]
            ),

            "severity_score": int(
                zone["severity_weighted_score"]
            ),

            "frequency_score": round(
                float(zone["frequency_score"]),
                2
            ),

            "risk_score": round(
                float(zone["risk_score"]),
                2
            ),

            "risk_level": str(zone["risk_level"])
        })


    return {

        "status": "success",

        "count": len(zones),

        "zones": zones
    }


@app.get("/statistics")
def get_statistics():

    total_accidents = len(
        accident_data
    )


    severity_counts = (
        accident_data[
            "accident_severity"
        ]
        .value_counts()
        .to_dict()
    )


    total_casualties = int(
        accident_data[
            "casualties"
        ].sum()
    )


    risk_counts = (
        risk_zones[
            "risk_level"
        ]
        .value_counts()
        .to_dict()
    )


    return {

        "status": "success",

        "total_accidents": total_accidents,

        "minor_accidents": int(
            severity_counts.get(
                "minor",
                0
            )
        ),

        "major_accidents": int(
            severity_counts.get(
                "major",
                0
            )
        ),

        "fatal_accidents": int(
            severity_counts.get(
                "fatal",
                0
            )
        ),

        "total_casualties": total_casualties,

        "total_risk_zones": len(
            risk_zones
        ),

        "risk_levels": {

            "low": int(
                risk_counts.get(
                    "Low",
                    0
                )
            ),

            "moderate": int(
                risk_counts.get(
                    "Moderate",
                    0
                )
            ),

            "high": int(
                risk_counts.get(
                    "High",
                    0
                )
            ),

            "critical": int(
                risk_counts.get(
                    "Critical",
                    0
                )
            )
        }
    }



@app.get("/analysis")
def get_analysis():

    cause_counts = (
        accident_data["cause"]
        .value_counts()
        .to_dict()
    )

    weather_counts = (
        accident_data["weather"]
        .value_counts()
        .to_dict()
    )

    road_type_counts = (
        accident_data["road_type"]
        .value_counts()
        .to_dict()
    )

    traffic_density_counts = (
        accident_data["traffic_density"]
        .value_counts()
        .to_dict()
    )

    # Hourly accident distribution
    hourly_counts = (
        accident_data["hour"]
        .value_counts()
        .reindex(range(24), fill_value=0)
        .sort_index()
        .to_dict()
    )

    # Classify accidents by time of day
    def classify_time(hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"

    time_period_counts = (
        accident_data["hour"]
        .apply(classify_time)
        .value_counts()
        .reindex(
            ["Morning", "Afternoon", "Evening", "Night"],
            fill_value=0
        )
        .to_dict()
    )

    return {
        "status": "success",

        "causes": {
            str(key): int(value)
            for key, value in cause_counts.items()
        },

        "weather": {
            str(key): int(value)
            for key, value in weather_counts.items()
        },

        "road_types": {
            str(key): int(value)
            for key, value in road_type_counts.items()
        },

        "traffic_density": {
            str(key): int(value)
            for key, value in traffic_density_counts.items()
        },

        "hourly": {
            str(key): int(value)
            for key, value in hourly_counts.items()
        },

        "time_period": {
            str(key): int(value)
            for key, value in time_period_counts.items()
        }
    }