# RoadSafe: presentation briefing

## Project in one sentence

RoadSafe is a road-safety analysis prototype that turns historical accident records into charts and map-based hotspot summaries, with a separate machine-learning model that classifies the severity of an accident record as minor, major, or fatal.

## Why we built it

Accident data has location, time, road, weather, and severity information. Looking at these records together can help people see where accidents have been recorded, how the records vary by time or conditions, and which geographic areas have higher historical scores. RoadSafe presents those patterns in one dashboard.

It is an analysis and awareness tool. It does not predict whether a new accident will happen, provide live traffic risk, or send emergency alerts.

## Dataset

The main data file used by the dashboard and severity-model workflow is `Data/indian_roads_cleaned.csv`.

- It has **20,000 records and 24 columns**.
- Its recorded dates run from **January 1, 2022 to April 15, 2025**.
- Fields include location (city, state, latitude, longitude), date and time, road type, lanes, traffic signals, weather, visibility, traffic density, temperature, accident cause, vehicles involved, casualties, severity, and risk score.
- The severity labels are **minor, major, and fatal**. In this file there are 11,025 minor records (55.1%), 5,988 major records (29.9%), and 2,987 fatal records (14.9%). This imbalance matters when judging the model.
- The checked-in cleaned file has no missing cells, duplicate rows, or duplicate accident IDs. The cleaning script also fills missing festival values, parses date/time, and checks ranges and consistency for fields such as coordinates, hour, and weekend flags.

The repository also contains a second accident dataset used by some exploratory-analysis and cleaning scripts. The dashboard and the severity-model workflow described below use `indian_roads_cleaned.csv`. The repository does not document the original publisher or collection method for the data, so we should describe the results as findings from the supplied dataset rather than verified national accident statistics.

## How the project works

```text
Accident CSV
    ↓
Cleaning and validation
    ↓
Exploratory analysis ──→ charts and historical patterns
    ↓
Coordinate grouping ───→ risk-zone map and location lookup
    ↓
Separate ML workflow ──→ minor / major / fatal classification
    ↓
FastAPI backend + React dashboard
```

### 1. Cleaning and exploratory analysis

Python and pandas are used to inspect columns, fill the missing festival category, parse dates and times, and check data ranges and consistency. The EDA scripts compare accident counts by severity, cause, road type, weather, traffic density, visibility, time of day, city, and geographic location. These comparisons describe associations in the records; they do not prove that a particular condition caused an accident.

### 2. Geographic risk zones

The hotspot-generation script rounds latitude and longitude to one decimal place and groups records into approximate geographic cells. For each cell, it calculates an accident-frequency score and a severity-weighted score. Severity weights are minor = 1, major = 2, and fatal = 3. Each score is scaled from 0 to 100 across the cells, then combined equally:

**Risk score = 50% frequency score + 50% severity score**

The script labels scores up to 25 as Low, up to 50 as Moderate, up to 75 as High, and above 75 as Critical. This is a relative score based on the dataset and the chosen formula, not a probability that an accident will occur.

The dashboard can filter accident records by city, severity, weather, and time of day. Its filterable map groups the matching records by rounded coordinates and averages their existing `risk_score` values. The separate location lookup uses the precomputed risk-zone file and returns the nearest cell to the user's browser location, including its score, level, accident count, and distance. Both views summarize historical data.

### 3. Machine-learning severity classification

This is a **supervised classification** task: the model learns from accident records that already have a severity label, then chooses one of three labels for another record. The input is not “will an accident happen?”

The model uses 11 context fields: road type, weather, visibility, traffic density, festival, number of lanes, traffic-signal flag, temperature, hour, weekend flag, and peak-hour flag. Date is used to split records chronologically, not as a predictor. The model excludes severity itself (the answer), and also excludes fields such as casualties, risk score, cause, vehicles involved, and location to reduce the chance of using information that may be known only after the event or of memorizing locations.

Categorical fields are one-hot encoded; missing numeric values are handled with the median and missing categories with the most common value. Logistic Regression, Decision Tree, and Random Forest were compared. The selected model is a class-weighted Random Forest, an ensemble of decision trees that combines their votes. It was selected by **macro-F1** on 2024 validation data. Macro-F1 gives each severity class equal importance, which is helpful when minor records are the majority.

The time-based split is:

- **Training:** 2022–2023, 12,205 records
- **Validation/model selection:** 2024, 6,061 records
- **Held-out evaluation:** January–April 2025, 1,734 records

The 2025 records were kept out of model fitting and model selection, then used once for the final evaluation.

## Implementation

- **Data and ML:** Python, pandas, and scikit-learn.
- **Backend:** FastAPI reads the CSV files and provides endpoints for filtered summaries, risk zones, statistics, and nearest-zone lookup. The nearest-zone calculation uses geographic distance from the user's coordinates to each precomputed cell.
- **Frontend:** React presents the dashboard and filters. Leaflet displays the map with OpenStreetMap tiles. If the user allows browser location access, the page requests the nearby historical risk zone.
- **Model output:** The trained preprocessing-and-classification pipeline is saved as a joblib artifact under `ML/model_artifacts/`.

The current web dashboard displays historical summaries and risk zones. The saved Random Forest is trained and evaluated in the separate ML workflow; the frontend/backend code does not currently call it to classify a new record.

## Results and what they mean

On the 1,734-record 2025 holdout, the selected Random Forest achieved **44.3% accuracy** and **34.7% macro-F1**. A simple baseline that always predicts the majority class, minor, achieved **56.7% accuracy** but only **24.1% macro-F1**. So the forest is better at balancing performance across the three classes, while the baseline gets more records right overall by always choosing the most common label.

Fatal-class recall for the Random Forest was about **14.9%** on this holdout, which is weak. The model should therefore be presented as an experimental classifier, not as a reliable safety decision system. These scores describe this particular supplied CSV and short test period; they do not establish real-world performance.

## Important points to say accurately

- The map shows **historical, dataset-derived risk**, not live or future accident risk.
- The ML model classifies severity **given an accident record**; it does not predict accident occurrence.
- The severity model is separate from the current dashboard and is not yet used by the web interface.
- The data source and the rules used to assign the severity labels are not documented in the repository.
- The score and model results depend on the supplied data, grouping choices, and evaluation period.

## Short presentation script

“Our project is RoadSafe, a road-accident analysis dashboard. We start with a cleaned dataset of 20,000 accident records containing location, time, road, weather, and severity information. We explore patterns in the data, then group locations into approximate map cells to show historical accident hotspots. The dashboard is built with React and Leaflet, while a FastAPI backend supplies filtered statistics and location-based risk information. Separately, we trained a Random Forest to classify an already-recorded accident as minor, major, or fatal. We used older years for training, 2024 for model selection, and January to April 2025 for a held-out evaluation. The model's results are limited, especially for fatal cases, and the dashboard is historical analysis rather than a live accident predictor.”

## Suggested speaking split for five people

1. **Problem and aim:** why accident patterns and hotspot summaries are useful.
2. **Dataset and cleaning:** what the records contain and how the data was checked.
3. **EDA and hotspot logic:** charts, coordinate cells, severity weights, and score levels.
4. **Machine learning:** target, input fields, Random Forest, chronological split, and honest results.
5. **Implementation and demo:** React dashboard, FastAPI, Leaflet map, filters, location lookup, and limitations.

## Quick answers for questions

**Why Random Forest?** It had the highest macro-F1 among the compared candidate models on the 2024 validation period.

**Why show both accuracy and macro-F1?** Accuracy can look good when the model mostly predicts the majority class. Macro-F1 weighs minor, major, and fatal equally, so it shows class balance more clearly.

**Does it predict future accidents?** No. The model classifies severity for an accident record, and the dashboard summarizes historical records.

**What would improve it?** Verify and document the data source and label definitions, collect stronger and more representative examples—especially fatal cases—and improve the model before considering any real-world use.
