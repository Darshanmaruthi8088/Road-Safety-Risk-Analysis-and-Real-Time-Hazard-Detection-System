# RoadSafe severity model training and validation

## Dataset and split

- Dataset: `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\Data\indian_roads_project_selected.csv` (20000 rows, 11 columns).
- Valid target-class distribution across the source file: `{"fatal": 2987, "major": 5988, "minor": 11025}`.
- Data quality check: 0 missing cells across all columns; 0 duplicate rows. Accident IDs are not part of this selected schema, so duplicate IDs cannot be checked here.
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

Used features: `road_type`, `weather`, `traffic_density`, `hour`.

Excluded fields: `accident_severity` is the target; `cause` and `casualties` describe the accident outcome and are deliberately excluded; `city` and coordinates are excluded to avoid geographic memorization; `date` is used only to create the chronological splits. The model classifies severity among recorded accidents and does not estimate whether an accident will occur.

## 2024 validation comparison

Models were selected using validation macro-F1. The 2025 holdout was not used for model selection.

| Model                   | Accuracy | Macro-P | Macro-R | Macro-F1 | Weighted-F1 | Fit sec | Selected |
| ----------------------- | -------- | ------- | ------- | -------- | ----------- | ------- | -------- |
| Majority-class baseline | 0.5512   | 0.1837  | 0.3333  | 0.2369   | 0.3918      | 0.066   | no       |
| Logistic Regression     | 0.3150   | 0.3272  | 0.3264  | 0.3004   | 0.3355      | 0.058   | no       |
| Decision Tree           | 0.3362   | 0.3438  | 0.3451  | 0.3196   | 0.3562      | 0.065   | no       |
| Random Forest           | 0.3437   | 0.3387  | 0.3392  | 0.3208   | 0.3631      | 0.400   | yes      |

Selected model: **Random Forest**. Its fitted preprocessing pipeline is saved at `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\model_artifacts\severity_pipeline.joblib`. The majority baseline predicts `minor` from the training class distribution.

## Outputs

- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\model_artifacts\severity_pipeline.joblib`: selected fitted pipeline.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\model_artifacts\severity_model_metadata.json`: model, split, feature, and validation metadata.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\validation_model_comparison.csv`: validation comparison table.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\training_data_audit.json`: data and exclusion audit.

Validation scores describe this dataset only. Dataset provenance is not documented in the repository, and these metrics do not establish real-world predictive accuracy.
