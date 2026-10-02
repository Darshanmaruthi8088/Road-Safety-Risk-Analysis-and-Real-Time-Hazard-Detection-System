import { useEffect, useState } from "react";
import "./App.css";
import RiskMap from "./RiskMap";

function App() {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

  const [riskData, setRiskData] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/statistics")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load statistics.");
        }

        return response.json();
      })
      .then((data) => {
        setStatistics(data);
      })
      .catch(() => {
        setError(
          "Could not load dashboard statistics. Make sure FastAPI is running."
        );
      })
      .finally(() => {
        setStatsLoading(false);
      });

    fetch("http://127.0.0.1:8000/analysis")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load analysis.");
        }

        return response.json();
      })
      .then((data) => {
        setAnalysis(data);
      })
      .catch(() => {
        setError(
          "Could not load EDA analysis data. Make sure the /analysis endpoint is available."
        );
      });
  }, []);

  const detectLocation = () => {
    setError("");

    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      return;
    }

    setLoading(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        setLatitude(lat);
        setLongitude(lon);

        try {
          const response = await fetch(
            `http://127.0.0.1:8000/risk?latitude=${lat}&longitude=${lon}`
          );

          if (!response.ok) {
            throw new Error("Failed to fetch risk data.");
          }

          const data = await response.json();

          setRiskData(data);
        } catch (err) {
          setError(
            "Could not connect to the RoadSafe backend. Make sure FastAPI is running."
          );
        } finally {
          setLoading(false);
        }
      },
      () => {
        setLoading(false);

        setError(
          "Location permission was denied. Please allow location access."
        );
      }
    );
  };

  const userLocation = riskData
    ? {
        latitude: Number(latitude),
        longitude: Number(longitude),
      }
    : null;

  return (
    <div className="app">

      <header className="navbar">

        <div>
          <h1>RoadSafe</h1>

          <p>
            Road Accident Risk Analysis System
          </p>
        </div>

        <div className="status">

          <span className="status-dot"></span>

          System Online

        </div>

      </header>


      <main className="dashboard">

        <section className="hero">

          <div>

            <h2>
              Road Safety Dashboard
            </h2>

            <p>
              Data-driven analysis of accident patterns,
              geographical hotspots and road safety risk.
            </p>

          </div>


          <button
            className="location-btn"
            onClick={detectLocation}
            disabled={loading}
          >

            {loading
              ? "Detecting..."
              : "📍 Detect My Location"}

          </button>

        </section>


        {error && (

          <div className="error-message">
            {error}
          </div>

        )}


        {/* ================= STATISTICS ================= */}

        <section className="stats-grid">

          <div className="stat-card">

            <span>
              Total Accidents
            </span>

            <strong>

              {statsLoading
                ? "..."
                : statistics?.total_accidents?.toLocaleString()}

            </strong>

            <small>
              Historical records
            </small>

          </div>


          <div className="stat-card">

            <span>
              Fatal Accidents
            </span>

            <strong>

              {statsLoading
                ? "..."
                : statistics?.fatal_accidents?.toLocaleString()}

            </strong>

            <small>

              {statistics
                ? (
                    (statistics.fatal_accidents /
                      statistics.total_accidents) *
                    100
                  ).toFixed(2)
                : "0.00"}
              % of records

            </small>

          </div>


          <div className="stat-card">

            <span>
              Risk Zones
            </span>

            <strong>

              {statsLoading
                ? "..."
                : statistics?.total_risk_zones}

            </strong>

            <small>
              Geographical zones
            </small>

          </div>


          <div className="stat-card">

            <span>
              Critical Zones
            </span>

            <strong>

              {statsLoading
                ? "..."
                : statistics?.risk_levels?.critical}

            </strong>

            <small>
              Highest risk category
            </small>

          </div>

        </section>


        {/* ================= MAP + CURRENT RISK ================= */}

        <section className="content-grid">


          <div className="panel map-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Risk Zone Map
                </h3>

                <p>
                  Historical accident risk distribution
                </p>

              </div>


              <span className="live-badge">
                LIVE
              </span>

            </div>


            <div className="real-map-container">

              <RiskMap
                userLocation={userLocation}
              />

            </div>


            <div className="legend">

              <span>
                <i className="low"></i>
                Low
              </span>

              <span>
                <i className="moderate"></i>
                Moderate
              </span>

              <span>
                <i className="high"></i>
                High
              </span>

              <span>
                <i className="critical-color"></i>
                Critical
              </span>

            </div>

          </div>


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Current Risk
                </h3>

                <p>
                  Your current location
                </p>

              </div>

            </div>


            {riskData ? (

              <div className="risk-display">

                <div className="risk-circle">

                  <strong>
                    {riskData.risk_score}
                  </strong>

                  <span>
                    Risk Score
                  </span>

                </div>


                <h2>
                  {riskData.risk_level} Risk
                </h2>


                <p>
                  Historical accident risk detected near
                  your current location.
                </p>


                <div className="location-details">

                  <p>
                    Latitude:{" "}
                    {Number(latitude).toFixed(6)}
                  </p>

                  <p>
                    Longitude:{" "}
                    {Number(longitude).toFixed(6)}
                  </p>

                  <p>
                    Nearby accidents:{" "}
                    {riskData.accident_count}
                  </p>

                  <p>
                    Distance to zone:{" "}
                    {riskData.distance_to_zone_km} km
                  </p>

                </div>

              </div>

            ) : (

              <div className="risk-display">

                <div className="risk-circle">

                  <strong>
                    --
                  </strong>

                  <span>
                    Risk Score
                  </span>

                </div>


                <h2>
                  Location not detected
                </h2>


                <p>
                  Allow location access to determine
                  the historical accident risk near you.
                </p>


                <button
                  className="primary-btn"
                  onClick={detectLocation}
                  disabled={loading}
                >

                  {loading
                    ? "Detecting..."
                    : "Detect Location"}

                </button>

              </div>

            )}

          </div>

        </section>


        {/* ================= SEVERITY + RISK SUMMARY ================= */}

        <section className="content-grid">


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Accident Severity
                </h3>

                <p>
                  Distribution of historical accidents
                </p>

              </div>

            </div>


            {statistics && (

              <div className="bar-chart">


                <div className="bar-row">

                  <span>
                    Minor
                  </span>

                  <div className="bar-container">

                    <div
                      className="bar minor-bar"
                      style={{
                        width: `${
                          (statistics.minor_accidents /
                            statistics.total_accidents) *
                          100
                        }%`,
                      }}
                    ></div>

                  </div>

                  <strong>

                    {(
                      (statistics.minor_accidents /
                        statistics.total_accidents) *
                      100
                    ).toFixed(1)}
                    %

                  </strong>

                </div>


                <div className="bar-row">

                  <span>
                    Major
                  </span>

                  <div className="bar-container">

                    <div
                      className="bar major-bar"
                      style={{
                        width: `${
                          (statistics.major_accidents /
                            statistics.total_accidents) *
                          100
                        }%`,
                      }}
                    ></div>

                  </div>

                  <strong>

                    {(
                      (statistics.major_accidents /
                        statistics.total_accidents) *
                      100
                    ).toFixed(1)}
                    %

                  </strong>

                </div>


                <div className="bar-row">

                  <span>
                    Fatal
                  </span>

                  <div className="bar-container">

                    <div
                      className="bar fatal-bar"
                      style={{
                        width: `${
                          (statistics.fatal_accidents /
                            statistics.total_accidents) *
                          100
                        }%`,
                      }}
                    ></div>

                  </div>

                  <strong>

                    {(
                      (statistics.fatal_accidents /
                        statistics.total_accidents) *
                      100
                    ).toFixed(1)}
                    %

                  </strong>

                </div>

              </div>

            )}

          </div>


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Risk Zone Summary
                </h3>

                <p>
                  Geographic classification
                </p>

              </div>

            </div>


            {statistics && (

              <div className="risk-summary">


                <div>

                  <span className="summary-dot low"></span>

                  <span>
                    Low
                  </span>

                  <strong>
                    {statistics.risk_levels.low}
                  </strong>

                </div>


                <div>

                  <span className="summary-dot moderate"></span>

                  <span>
                    Moderate
                  </span>

                  <strong>
                    {statistics.risk_levels.moderate}
                  </strong>

                </div>


                <div>

                  <span className="summary-dot high"></span>

                  <span>
                    High
                  </span>

                  <strong>
                    {statistics.risk_levels.high}
                  </strong>

                </div>


                <div>

                  <span className="summary-dot critical-color"></span>

                  <span>
                    Critical
                  </span>

                  <strong>
                    {statistics.risk_levels.critical}
                  </strong>

                </div>

              </div>

            )}

          </div>

        </section>


        {/* ================= ACCIDENT CAUSES + WEATHER ================= */}

        <section className="content-grid">


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Accident Causes
                </h3>

                <p>
                  Distribution of recorded accident causes
                </p>

              </div>

            </div>


            {analysis && statistics && (

              <div className="bar-chart">

                {Object.entries(analysis.causes).map(
                  ([cause, count]) => {

                    const percentage =
                      (count /
                        statistics.total_accidents) *
                      100;

                    return (

                      <div
                        className="bar-row"
                        key={cause}
                      >

                        <span>
                          {cause}
                        </span>

                        <div className="bar-container">

                          <div
                            className="bar cause-bar"
                            style={{
                              width: `${percentage}%`,
                            }}
                          ></div>

                        </div>

                        <strong>
                          {percentage.toFixed(1)}%
                        </strong>

                      </div>

                    );
                  }
                )}

              </div>

            )}

          </div>


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Weather Conditions
                </h3>

                <p>
                  Accident records by weather
                </p>

              </div>

            </div>


            {analysis && statistics && (

              <div className="bar-chart">

                {Object.entries(analysis.weather).map(
                  ([weather, count]) => {

                    const percentage =
                      (count /
                        statistics.total_accidents) *
                      100;

                    return (

                      <div
                        className="bar-row"
                        key={weather}
                      >

                        <span>
                          {weather}
                        </span>

                        <div className="bar-container">

                          <div
                            className="bar weather-bar"
                            style={{
                              width: `${percentage}%`,
                            }}
                          ></div>

                        </div>

                        <strong>
                          {percentage.toFixed(1)}%
                        </strong>

                      </div>

                    );
                  }
                )}

              </div>

            )}

          </div>

        </section>


        <footer>

          <p>
            RoadSafe • Data Exploration & Visualization Project
          </p>

        </footer>

      </main>

    </div>
  );
}

export default App;