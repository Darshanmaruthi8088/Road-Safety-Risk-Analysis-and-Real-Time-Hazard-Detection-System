# RoadSafe severity dataset: provenance and field notes

## Dataset lineage

The severity-model scripts read `Data/indian_roads_cleaned.csv`. The repository contains `Data/indian_roads_dataset.csv` and `Cleaning/01_data_cleaning.py`; that cleaning script reads a file named `indian_roads_dataset.csv`, fills missing `festival` values with `No Festival`, parses `date` and `time`, and writes a file named `indian_roads_cleaned.csv`.

The cleaning script uses paths relative to its working directory and does not record a source URL, publisher, collection method, license, version, or checksum. The repository does not establish that the checked-in cleaned CSV was produced from the checked-in raw CSV by a particular run. The upstream source and whether the records are observed, synthetic, or mixed are **unknown**.

The checked-in cleaned CSV has 20,000 rows and 24 columns. Its dates parse from 2022-01-01 through 2025-04-15. These are properties of the current file, not claims about the upstream data source.

## Target label

The training code uses `accident_severity` as the target and accepts the labels `minor`, `major`, and `fatal` after trimming whitespace and converting text to lowercase. The evaluation code treats the output as severity conditional on an accident record.

The repository does not document who assigned these labels, their operational definitions, any severity thresholds, whether they were reported or derived, or how they relate to `casualties`, `risk_score`, or fatalities. Those label-generation rules are **unknown**. The cleaned file has no separate fatalities-count column.

## Features used by the temporal comparison

The new comparison uses the same 11 columns as `ML/04_train_severity_model.py`. Values and ranges below were inspected in the checked-in CSV. A field name or observed value does not establish its measurement method or real-world meaning.

| Field | Type in comparison | Verified information | Unknown details |
| --- | --- | --- | --- |
| `road_type` | Categorical | Observed values: `highway`, `rural`, `urban`. | Classification rules and who assigned them. |
| `weather` | Categorical | Observed values: `clear`, `fog`, `rain`. | Observation source, timing, and category rules. |
| `visibility` | Categorical | Observed values: `high`, `medium`, `low`. | Units, thresholds, and observation method. |
| `traffic_density` | Categorical | Observed values: `high`, `medium`, `low`. | Measurement method, thresholds, and observation timing. |
| `festival` | Categorical | Observed values: `Diwali`, `Eid`, `Holi`, `New Year`, `No Festival`. The cleaning script replaces missing values with `No Festival`. | Event calendar, geographic radius, date window, and assignment rules. |
| `lanes` | Numeric | Integer values from 1 through 6 in this file; the field is named `lanes`. | Counting convention and whether the value describes the accident location. |
| `traffic_signal` | Numeric | Values are 0 or 1 in this file; the field is named `traffic_signal`. | Exact meaning of each code and whether it describes the accident location. |
| `temperature` | Numeric | Values from 15 through 40 in this file. | Unit, source, location, and measurement time. |
| `hour` | Numeric | Integer values from 0 through 23; it matches the hour parsed from `time` in the checked-in file. | Time zone and time source. |
| `is_weekend` | Numeric | Values are 0 or 1. In the checked-in file, they match the rule `date` is Saturday or Sunday; the cleaning script contains this consistency check. | Upstream generation process. |
| `is_peak_hour` | Numeric | Values are 0 or 1. In the checked-in file, 1 occurs at hours 8–10 and 17–19. | Whether these hours are an intended definition, and who selected them. |

`date` is used to assign chronological folds; it is not a predictor in the new comparison. `accident_id`, location, `cause`, `vehicles_involved`, `casualties`, and `risk_score` are not included among its model features. This exclusion is a modeling choice and does not establish the provenance or timing of those fields.
