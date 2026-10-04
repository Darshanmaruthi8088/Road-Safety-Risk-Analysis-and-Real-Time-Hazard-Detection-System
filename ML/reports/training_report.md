# RoadSafe severity model training and validation

## Dataset and split

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
