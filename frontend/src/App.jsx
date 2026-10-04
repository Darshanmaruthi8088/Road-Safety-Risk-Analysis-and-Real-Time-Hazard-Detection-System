import { useEffect, useState } from "react";
import "./App.css";
import RiskMap from "./RiskMap";

const safePercentage = (value, total) => {
  const numerator = Number(value);
  const denominator = Number(total);
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator <= 0) return 0;
  return (numerator / denominator) * 100;
};

function App() {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

  const [riskData, setRiskData] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState("");

  const [filters, setFilters] = useState({
    city: "All",
    severity: "All",
    weather: "All",
    time_period: "All",
  });
  const [filterOptions, setFilterOptions] = useState({
    cities: [],
    severities: [],
    weather: [],
    time_periods: [],
  });

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== "All") params.set(key, value);
    });

    setStatsLoading(true);
    fetch(`http://127.0.0.1:8000/filtered-dashboard?${params.toString()}`, {
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) throw new Error("Failed to load filtered dashboard data.");
        return response.json();
      })
      .then((data) => {
        setStatistics(data.statistics);
        setAnalysis(data.analysis);
        setFilterOptions(data.filter_options);
        setError("");
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(
            "Could not load filtered dashboard data. Check that the FastAPI filters router is registered and the backend is running."
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setStatsLoading(false);
      });

    return () => controller.abort();
  }, [filters]);

  const updateFilter = (name, value) => {
    setFilters((current) => ({ ...current, [name]: value }));
  };

  const resetFilters = () => {
    setFilters({ city: "All", severity: "All", weather: "All", time_period: "All" });
  };

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


        <section className="filter-panel panel">
          <div className="filter-heading">
            <div>
              <h3>Filter Accident Records</h3>
              <p>Choose one or more conditions to update the statistics and charts.</p>
            </div>
            <button className="reset-filters-btn" type="button" onClick={resetFilters}>
              Reset filters
            </button>
          </div>

          <div className="filter-grid">
            <label className="filter-control">
              <span>City</span>
              <select value={filters.city} onChange={(event) => updateFilter("city", event.target.value)}>
                <option value="All">All cities</option>
                {filterOptions.cities.map((city) => <option key={city} value={city}>{city}</option>)}
              </select>
            </label>

            <label className="filter-control">
              <span>Accident severity</span>
              <select value={filters.severity} onChange={(event) => updateFilter("severity", event.target.value)}>
                <option value="All">All severities</option>
                {filterOptions.severities.map((severity) => <option key={severity} value={severity}>{severity}</option>)}
              </select>
            </label>

            <label className="filter-control">
              <span>Weather</span>
              <select value={filters.weather} onChange={(event) => updateFilter("weather", event.target.value)}>
                <option value="All">All weather conditions</option>
                {filterOptions.weather.map((weather) => <option key={weather} value={weather}>{weather}</option>)}
              </select>
            </label>

            <label className="filter-control">
              <span>Time of day</span>
              <select value={filters.time_period} onChange={(event) => updateFilter("time_period", event.target.value)}>
                <option value="All">All time periods</option>
                {filterOptions.time_periods.map((period) => <option key={period} value={period}>{period}</option>)}
              </select>
            </label>
          </div>

          <div className="filter-status" aria-live="polite">
            {statsLoading ? "Updating dashboard…" : `${Number(statistics?.total_accidents ?? 0).toLocaleString()} matching accident records`}
            {Object.values(filters).some((value) => value !== "All") && !statsLoading ? " • Filters applied" : ""}
          </div>
        </section>

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

              {statistics && statistics.total_accidents > 0
                ? safePercentage(statistics.fatal_accidents, statistics.total_accidents).toFixed(2)
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
                HISTORICAL
              </span>

            </div>


            <div className="real-map-container">

              <RiskMap
                userLocation={userLocation}
                city={filters.city}
                severity={filters.severity}
                weather={filters.weather}
                timePeriod={filters.time_period}
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
                          safePercentage(statistics.minor_accidents, statistics.total_accidents)
                        }%`,
                      }}
                    ></div>

                  </div>

                  <strong>

                    {(
                      safePercentage(statistics.minor_accidents, statistics.total_accidents)
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
                          safePercentage(statistics.major_accidents, statistics.total_accidents)
                        }%`,
                      }}
                    ></div>

                  </div>

                  <strong>

                    {(
                      safePercentage(statistics.major_accidents, statistics.total_accidents)
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
                          safePercentage(statistics.fatal_accidents, statistics.total_accidents)
                        }%`,
                      }}
                    ></div>

                  </div>

                  <strong>

                    {(
                      safePercentage(statistics.fatal_accidents, statistics.total_accidents)
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

                    const percentage = statistics.total_accidents
                      ? (count / statistics.total_accidents) * 100
                      : 0;

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
                              width: `${Number.isFinite(percentage) ? Math.max(0, Math.min(100, percentage)) : 0}%`,
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

                    const percentage = statistics.total_accidents
                      ? (count / statistics.total_accidents) * 100
                      : 0;

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
                              width: `${Number.isFinite(percentage) ? Math.max(0, Math.min(100, percentage)) : 0}%`,
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


        {/* ================= ROAD TYPE + TRAFFIC DENSITY ================= */}

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Road Type Analysis</h3>
                <p>Accident records by road type</p>
              </div>
            </div>

            {analysis && statistics && (
              <div className="bar-chart">
                {Object.entries(analysis.road_types || {}).map(
                  ([roadType, count]) => {
                    const percentage = statistics.total_accidents
                      ? (count / statistics.total_accidents) * 100
                      : 0;

                    return (
                      <div className="bar-row" key={roadType}>
                        <span>{roadType}</span>
                        <div className="bar-container">
                          <div
                            className="bar road-type-bar"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <strong>{percentage.toFixed(1)}%</strong>
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
                <h3>Traffic Density Analysis</h3>
                <p>Accident records by traffic density</p>
              </div>
            </div>

            {analysis && statistics && (
              <div className="bar-chart">
                {Object.entries(analysis.traffic_density || {}).map(
                  ([density, count]) => {
                    const percentage = statistics.total_accidents
                      ? (count / statistics.total_accidents) * 100
                      : 0;

                    return (
                      <div className="bar-row" key={density}>
                        <span>{density}</span>
                        <div className="bar-container">
                          <div
                            className="bar traffic-density-bar"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <strong>{percentage.toFixed(1)}%</strong>
                      </div>
                    );
                  }
                )}
              </div>
            )}
          </div>
        </section>


        {/* ================= HOURLY + TIME-OF-DAY ANALYSIS ================= */}
        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Hourly Accident Distribution</h3>
                <p>Historical accident records across the 24-hour day</p>
              </div>
            </div>

            {analysis?.hourly && (
              <div className="bar-chart">
                {Object.entries(analysis.hourly)
                  .sort(([hourA], [hourB]) => Number(hourA) - Number(hourB))
                  .map(([hour, count]) => {
                    const hourlyValues = Object.values(analysis.hourly).map(Number);
                    const maxCount = Math.max(...hourlyValues, 1);
                    const percentage = (Number(count) / maxCount) * 100;

                    return (
                      <div className="bar-row" key={hour}>
                        <span>{String(hour).padStart(2, "0")}:00</span>
                        <div className="bar-container">
                          <div
                            className="bar hourly-bar"
                            style={{
                              width: `${Number.isFinite(percentage) ? Math.max(0, Math.min(100, percentage)) : 0}%`,
                              background: "#8b5cf6"
                            }}
                          />
                        </div>
                        <strong>{Number(count).toLocaleString()}</strong>
                      </div>
                    );
                  })}
              </div>
            )}
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Time-of-Day Analysis</h3>
                <p>Historical accident records by time period</p>
              </div>
            </div>

            {analysis?.time_period && (
              <div className="bar-chart">
                {["Morning", "Afternoon", "Evening", "Night"].map((period) => {
                  const count = Number(analysis.time_period[period] ?? 0);
                  const values = Object.values(analysis.time_period).map(Number);
                  const maxCount = Math.max(...values, 1);
                  const percentage = statistics?.total_accidents
                    ? (count / statistics.total_accidents) * 100
                    : 0;
                  const barWidth = (count / maxCount) * 100;

                  return (
                    <div className="bar-row" key={period}>
                      <span>{period}</span>
                      <div className="bar-container">
                        <div
                          className="bar time-period-bar"
                          style={{
                            width: `${Number.isFinite(barWidth) ? Math.max(0, Math.min(100, barWidth)) : 0}%`,
                            background: "#14b8a6"
                          }}
                        />
                      </div>
                      <strong>{percentage.toFixed(1)}%</strong>
                    </div>
                  );
                })}
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