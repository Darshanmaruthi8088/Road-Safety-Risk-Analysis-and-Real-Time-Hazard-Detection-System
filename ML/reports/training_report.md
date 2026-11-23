# RoadSafe severity model training and validation

## Dataset and split

<<<<<<< HEAD
- Dataset: `Data/indian_roads_cleaned.csv` (20000 rows, 24 columns).
- Valid target-class distribution across the source file: `{"fatal": 2987, "major": 5988, "minor": 11025}`.
- Data quality check: 0 missing cells, 0 duplicate rows, and 0 duplicate accident IDs.
- Date column: `date`, parsed with `pandas.to_datetime(errors='coerce')`; 0 parse failures, range 2022-01-01 to 2025-04-15.
- Invalid date or label rows excluded: 0 (date-only 0, label-only 0, both 0).
- Valid rows outside the requested periods excluded: 0.
- Train: 2022-01-01 through 2023-12-31 (12205 rows), validation: 2024-01-01 through 2024-12-31 (6061 rows), test holdout: 2025-01-01 through 2025-04-30 (1734 eligible rows).
- Test rows are excluded from fitting, preprocessing, validation scoring, and selection. The source-wide date/label audit does not fit or tune a model.
- Preprocessing is inside each pipeline and fitted only on 2022-2023 rows. Random state: 42.

### Class distribution by split

| Split      | Minor | Major | Fatal |
| ---------- | ----- | ----- | ----- |
| Train      | 6701  | 3704  | 1800  |
| Validation | 3341  | 1795  | 925   |

## Features and leakage review

Used features: `road_type`, `weather`, `visibility`, `traffic_density`, `festival`, `lanes`, `traffic_signal`, `temperature`, `hour`, `is_weekend`, `is_peak_hour`.

Excluded fields: `accident_severity` is the target; `casualties` and `risk_score` are post-event/outcome proxies; `cause` and `vehicles_involved` may only be known during or after an incident; `accident_id` is an identifier; city/state/coordinates may encourage geographic memorization; date/time are used only to establish chronology. No fatalities column exists in this dataset. This classifies severity among recorded accidents; it does not estimate whether an accident will occur.

## 2024 validation comparison

Candidates were selected by validation macro-F1. The majority-class baseline predicts `minor`. Training and validation prediction times are measured per candidate.

| Model                   | Accuracy | Macro-P | Macro-R | Macro-F1 | Weighted-F1 | Fit sec | Val predict sec | Selected |
| ----------------------- | -------- | ------- | ------- | -------- | ----------- | ------- | --------------- | -------- |
| Majority-class baseline | 0.5512   | 0.1837  | 0.3333  | 0.2369   | 0.3918      | 0.235   | 0.002           | no       |
| Logistic Regression     | 0.3094   | 0.3221  | 0.3194  | 0.2947   | 0.3297      | 0.427   | 0.035           | no       |
| Decision Tree           | 0.3272   | 0.3350  | 0.3321  | 0.3088   | 0.3497      | 0.267   | 0.038           | no       |
| Random Forest           | 0.4121   | 0.3281  | 0.3277  | 0.3276   | 0.4099      | 1.362   | 0.160           | yes      |

Selected model: **Random Forest** (validation macro-F1 0.3276). The fitted pipeline is saved at `ML/model_artifacts/severity_pipeline.joblib`.

## Limitations

The target classes are imbalanced (minor is the largest class). Dataset provenance is not documented in the repository. These validation results describe this CSV and do not establish real-world predictive accuracy.
=======
- Dataset: `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\Data\indian_roads_cleaned.csv` (20000 rows, 24 columns).
- Date column: `date`; parsed with `pandas.to_datetime(errors='coerce')`. Parse failures: 0.
- Target: `accident_severity`; accepted labels: minor, major, fatal.
- Train: 2022-01-01 through 2023-12-31 (12205 rows).
- Validation: 2024-01-01 through 2024-12-31 (6061 rows).
- Reserved test: 2025-01-01 through 2025-04-30 (1734 eligible rows); those rows are not used for fitting, preprocessing, validation scoring, or selection. Date and label validity are audited across the source file.
- Invalid date or label rows excluded: 0 (date-only 0, label-only 0, both 0).
- Valid rows outside the requested periods excluded: 0.
- Preprocessing is inside each pipeline and is fitted by `Pipeline.fit` on 2022-2023 rows only. Validation and holdout data are not used to fit preprocessing.

### Class distribution

- Train: `{"fatal": 1800, "major": 3704, "minor": 6701}`
- Validation: `{"fatal": 925, "major": 1795, "minor": 3341}`

## Features

Used features: `road_type`, `weather`, `visibility`, `traffic_density`, `festival`, `lanes`, `traffic_signal`, `temperature`, `hour`, `is_weekend`, `is_peak_hour`.

Excluded fields: `accident_severity` is the target; `casualties` and `risk_score` are post-event/outcome proxies; `cause` and `vehicles_involved` may only be known during or after an incident; `accident_id` is an identifier; city/state/coordinates may encourage geographic memorization; date/time are used only to establish chronology. No fatalities column exists in this selected dataset. These results classify severity among recorded accidents and do not estimate whether an accident will occur.

## 2024 validation comparison

Models were selected using validation macro-F1. The 2025 holdout was not used for model selection.

| Model                   | Accuracy | Macro-P | Macro-R | Macro-F1 | Weighted-F1 | Fit sec | Selected |
| ----------------------- | -------- | ------- | ------- | -------- | ----------- | ------- | -------- |
| Majority-class baseline | 0.5512   | 0.1837  | 0.3333  | 0.2369   | 0.3918      | 0.235   | no       |
| Logistic Regression     | 0.3094   | 0.3221  | 0.3194  | 0.2947   | 0.3297      | 0.427   | no       |
| Decision Tree           | 0.3272   | 0.3350  | 0.3321  | 0.3088   | 0.3497      | 0.267   | no       |
| Random Forest           | 0.4121   | 0.3281  | 0.3277  | 0.3276   | 0.4099      | 1.362   | yes      |

Selected model: **Random Forest**. Its fitted preprocessing pipeline is saved at `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\model_artifacts\severity_pipeline.joblib`. The majority baseline predicts `minor` from the training class distribution.

## Outputs

- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\model_artifacts\severity_pipeline.joblib`: selected fitted pipeline.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\model_artifacts\severity_model_metadata.json`: model, split, feature, and validation metadata.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\validation_model_comparison.csv`: validation comparison table.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\training_data_audit.json`: data and exclusion audit.

Validation scores describe this dataset only. Dataset provenance is not documented in the repository, and these metrics do not establish real-world predictive accuracy.
>>>>>>> 383f80c06fc073766380912f274f0db73d3b64c4
