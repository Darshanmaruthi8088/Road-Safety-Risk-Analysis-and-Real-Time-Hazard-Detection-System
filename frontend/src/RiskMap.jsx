import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap
} from "react-leaflet";

import "leaflet/dist/leaflet.css";


function MapController({ latitude, longitude }) {

  const map = useMap();

  useEffect(() => {

    if (latitude && longitude) {

      map.setView(
        [latitude, longitude],
        12
      );
    }

  }, [latitude, longitude, map]);

  return null;
}


function getRiskColor(level) {

  if (level === "Critical") {
    return "#ef4444";
  }

  if (level === "High") {
    return "#f97316";
  }

  if (level === "Moderate") {
    return "#facc15";
  }

  return "#22c55e";
}


function RiskMap({ userLocation }) {

  const [zones, setZones] = useState([]);
  const [error, setError] = useState("");


  useEffect(() => {

    fetch("http://127.0.0.1:8000/risk-zones")
      .then((response) => {

        if (!response.ok) {
          throw new Error("Failed to load risk zones");
        }

        return response.json();
      })
      .then((data) => {

        setZones(data.zones);

      })
      .catch(() => {

        setError("Unable to load risk zones.");

      });

  }, []);


  return (
    <div className="real-map">

      {error && (
        <div className="map-error">
          {error}
        </div>
      )}

      <MapContainer
        center={[22.5, 80]}
        zoom={5}
        style={{
          height: "100%",
          width: "100%"
        }}
      >

        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />


        {zones.map((zone, index) => (

          <CircleMarker
            key={index}
            center={[
              zone.latitude,
              zone.longitude
            ]}
            radius={Math.max(
              6,
              Math.min(
                18,
                zone.accident_count / 50
              )
            )}
            pathOptions={{
              color: getRiskColor(zone.risk_level),
              fillColor: getRiskColor(zone.risk_level),
              fillOpacity: 0.65
            }}
          >

            <Popup>

              <strong>
                {zone.risk_level} Risk
              </strong>

              <br />

              Risk Score:
              {" "}
              {zone.risk_score}

              <br />

              Accidents:
              {" "}
              {zone.accident_count}

              <br />

              Casualties:
              {" "}
              {zone.total_casualties}

              <br />

              Coordinates:
              {" "}
              {zone.latitude},
              {" "}
              {zone.longitude}

            </Popup>

          </CircleMarker>

        ))}


        {userLocation && (

          <>
            <CircleMarker
              center={[
                userLocation.latitude,
                userLocation.longitude
              ]}
              radius={9}
              pathOptions={{
                color: "#2563eb",
                fillColor: "#2563eb",
                fillOpacity: 1
              }}
            >

              <Popup>
                <strong>Your Location</strong>
                <br />
                Latitude: {userLocation.latitude}
                <br />
                Longitude: {userLocation.longitude}
              </Popup>

            </CircleMarker>

            <MapController
              latitude={userLocation.latitude}
              longitude={userLocation.longitude}
            />
          </>

        )}

      </MapContainer>

    </div>
  );
}

export default RiskMap;