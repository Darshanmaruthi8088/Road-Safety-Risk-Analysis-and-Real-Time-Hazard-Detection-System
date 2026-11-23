# RoadSafe severity model holdout evaluation

## Evaluation design and data audit

- Dataset: 20000 rows by 24 columns. Valid target-class distribution: `{"fatal": 2987, "major": 5988, "minor": 11025}`.
- Data quality check: 0 missing cells, 0 duplicate rows, and 0 duplicate accident IDs.
- Date column: `date`, parsed with `pandas.to_datetime(errors='coerce')`. Invalid date rows: 0; invalid label rows: 0; excluded for invalid date or label: 0.
- Selected model: **Random Forest**, selected using 2024 validation macro-F1 (0.3276). Candidate comparison and fit times are in `validation_model_comparison.csv`.
- Holdout: 2025-01-01 through 2025-04-30 (1734 records), evaluated once after selection. Test distribution: `{"fatal": 262, "major": 489, "minor": 983}`.
- The saved pipeline was loaded from `ML/model_artifacts/severity_pipeline.joblib`; its preprocessing was fitted only on 2022-01-01 through 2023-12-31 (12205 rows). The evaluator did not fit or tune the model.

## Holdout metrics

| Model                   | Accuracy | Macro-P | Macro-R | Macro-F1 | Weighted-P | Weighted-R | Weighted-F1 |
| ----------------------- | -------- | ------- | ------- | -------- | ---------- | ---------- | ----------- |
| Random Forest           | 0.4429   | 0.3495  | 0.3468  | 0.3472   | 0.4358     | 0.4429     | 0.4389      |
| Majority-class baseline | 0.5669   | 0.1890  | 0.3333  | 0.2412   | 0.3214     | 0.5669     | 0.4102      |

### Per-class precision, recall, and F1

| Model                   | Class / average | Precision | Recall | F1     | Support |
| ----------------------- | --------------- | --------- | ------ | ------ | ------- |
| Random Forest           | minor           | 0.5789    | 0.5931 | 0.5859 | 983     |
| Random Forest           | major           | 0.2802    | 0.2986 | 0.2891 | 489     |
| Random Forest           | fatal           | 0.1893    | 0.1489 | 0.1667 | 262     |
| Random Forest           | macro avg       | 0.3495    | 0.3468 | 0.3472 | 1734    |
| Random Forest           | weighted avg    | 0.4358    | 0.4429 | 0.4389 | 1734    |
| Random Forest           | accuracy        |           |        | 0.4429 | 1734    |
| Majority-class baseline | minor           | 0.5669    | 1.0000 | 0.7236 | 983     |
| Majority-class baseline | major           | 0.0000    | 0.0000 | 0.0000 | 489     |
| Majority-class baseline | fatal           | 0.0000    | 0.0000 | 0.0000 | 262     |
| Majority-class baseline | macro avg       | 0.1890    | 0.3333 | 0.2412 | 1734    |
| Majority-class baseline | weighted avg    | 0.3214    | 0.5669 | 0.4102 | 1734    |
| Majority-class baseline | accuracy        |           |        | 0.5669 | 1734    |

### Confusion matrix: selected model

Rows are actual classes; columns are predicted classes.

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 583   | 295   | 105   |
| major              | 281   | 146   | 62    |
| fatal              | 143   | 80    | 39    |

### Confusion matrix: majority baseline

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 983   | 0     | 0     |
| major              | 489   | 0     | 0     |
| fatal              | 262   | 0     | 0     |

Selected-model prediction and metric time: 0.285561 seconds. Baseline prediction and metric time: 0.000016 seconds. Candidate fit and validation prediction times are in the training comparison CSV.

## Limitations

Minor records are the largest class. The majority baseline has higher accuracy than the selected model, while the selected model has higher macro-F1 and weighted-F1. Fatal recall is low, so performance is weak for the rarest class. Dataset provenance is not documented in the repository; these figures describe only the supplied CSV and do not establish real-world predictive accuracy. This model classifies severity conditional on an accident record; it does not predict whether an accident will occur or detect accidents in real time. The Jan-Apr 2025 test period is short and cannot establish performance in other years, places, or operating conditions.

## Saved outputs

- `ML/model_artifacts/severity_pipeline.joblib`
- `ML/model_artifacts/severity_model_metadata.json`
- `ML/reports/test_evaluation_metrics.json`
- `ML/reports/test_classification_report.csv`
- `ML/reports/test_confusion_matrix_selected_model.csv`
- `ML/reports/test_confusion_matrix_baseline.csv`
