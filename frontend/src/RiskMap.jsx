import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import { API_BASE_URL } from "./api";

function MapController({ latitude, longitude }) {
  const map = useMap();

  useEffect(() => {
    if (
      Number.isFinite(latitude) &&
      Number.isFinite(longitude)
    ) {
      map.setView([latitude, longitude], 12);
    }
  }, [latitude, longitude, map]);

  return null;
}

function getRiskColor(level) {
  switch (String(level).toLowerCase()) {
    case "critical":
      return "#ef4444";
    case "high":
      return "#f97316";
    case "moderate":
      return "#facc15";
    default:
      return "#22c55e";
  }
}

function RiskMap({
  userLocation,
  city = "All",
  severity = "All",
  weather = "All",
  timePeriod = "All",
}) {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadZones() {
      setLoading(true);
      setError("");

      try {
        const params = new URLSearchParams({
          city,
          severity,
          weather,
          time_period: timePeriod,
        });

        const response = await fetch(
          `${API_BASE_URL}/filtered-risk-zones?${params.toString()}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Failed to load filtered risk zones.");
        }

        const data = await response.json();
        setZones(Array.isArray(data.zones) ? data.zones : []);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError("Unable to load map zones. Check the backend.");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadZones();

    return () => controller.abort();
  }, [city, severity, weather, timePeriod]);

  return (
    <div className="real-map">
      {loading && <div className="map-error">Updating map...</div>}

      {error && <div className="map-error">{error}</div>}

      {!loading && !error && zones.length === 0 && (
        <div className="map-error">
          No risk zones match the selected filters.
        </div>
      )}

      <MapContainer
        center={[22.5, 80]}
        zoom={5}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {zones.map((zone, index) => {
          const color = getRiskColor(zone.risk_level);

          return (
            <CircleMarker
              key={`${zone.latitude}-${zone.longitude}-${index}`}
              center={[zone.latitude, zone.longitude]}
              radius={Math.max(
                6,
                Math.min(18, Number(zone.accident_count || 0) / 50)
              )}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: 0.65,
              }}
            >
              <Popup>
                <strong>{zone.risk_level} Severity Index</strong>
                <br />
                Severity index: {zone.risk_score}
                <br />
                Accidents: {zone.accident_count}
                <br />
                Fatal: {zone.fatal_count} · Major: {zone.major_count} · Minor: {zone.minor_count}
                <br />
                Casualties: {zone.total_casualties}
                <br />
                Coordinates: {zone.latitude}, {zone.longitude}
              </Popup>
            </CircleMarker>
          );
        })}

        {userLocation && (
          <>
            <CircleMarker
              center={[
                userLocation.latitude,
                userLocation.longitude,
              ]}
              radius={9}
              pathOptions={{
                color: "#2563eb",
                fillColor: "#2563eb",
                fillOpacity: 1,
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
