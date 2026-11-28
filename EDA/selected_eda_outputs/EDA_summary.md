# Exploratory analysis: selected RoadSafe dataset

- Records analyzed: 20,000
- Selected columns: 11
- Date range: 2022-01-01 to 2025-04-15
- Cities represented: 8
- Total recorded casualties: 34,529
- Most represented city by record count: Chandigarh (2,577)
- Most common reported cause: distraction (4,026)

## Severity distribution

| Severity | Records | Percent |
|---|---:|---:|
| minor | 11,025 | 55.12% |
| major | 5,988 | 29.94% |
| fatal | 2,987 | 14.94% |

## Analyses produced

- Severity counts and percentages.
- Annual and monthly record counts.
- City counts and severity percentages by city.
- Reported causes and severity percentages by cause.
- Severity percentages by road type, weather, and traffic density.
- Severity by time-of-day period and record counts by hour.
- Casualty summaries by recorded severity.
- Geographic distribution and approximate coordinate-grid hotspot summaries.

## Interpretation notes

These charts describe records in the supplied dataset. They do not establish that a factor caused an accident.
City counts are not exposure-adjusted risk rates; population, road length, and traffic volume are not included.
The dataset ends on April 15, 2025, so 2025 annual and monthly counts are partial and should not be compared directly with full years.
Hotspot cells are approximate 0.1-degree coordinate groups. The source-level risk_score field is not in this selected dataset; hotspot summaries use observed counts, casualties, and severity weights instead.

## Output files

- `01_severity_distribution.png`
- `02_accidents_over_time.png`
- `03_records_by_city.png`
- `04_severity_by_city.png`
- `05_records_by_cause.png`
- `06_severity_by_cause.png`
- `07_severity_by_road_type.png`
- `08_severity_by_weather.png`
- `09_severity_by_traffic_density.png`
- `10_severity_by_time_period.png`
- `11_records_by_hour.png`
- `12_casualties_by_severity.png`
- `13_geographic_distribution.png`
- `14_top_geographic_hotspots.png`
- `casualties_by_severity.csv`
- `hotspot_grid_summary.csv`
- `records_by_cause.csv`
- `records_by_city.csv`
- `records_by_hour.csv`
- `records_by_month.csv`
- `records_by_year.csv`
- `severity_distribution.csv`
- `severity_percentage_by_cause.csv`
- `severity_percentage_by_city.csv`
- `severity_percentage_by_road_type.csv`
- `severity_percentage_by_time_period.csv`
- `severity_percentage_by_traffic_density.csv`
- `severity_percentage_by_weather.csv`
- `top_15_hotspots.csv`
