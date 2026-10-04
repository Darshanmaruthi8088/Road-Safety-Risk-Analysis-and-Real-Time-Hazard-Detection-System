# RoadSafe severity model holdout evaluation

## Evaluation design

- Selected model: **Random Forest**, chosen using 2024 validation macro-F1 (0.3276).
- Holdout: 2025-01-01 through 2025-04-30 (1734 rows), evaluated once after model selection.
- Training and preprocessing fit period: 2022-01-01 through 2023-12-31 (12205 rows). The saved pipeline is loaded and used for prediction; this script does not fit or tune it.
- Date column: `date` parsed with `pandas.to_datetime(errors='coerce')`. Invalid dates: 0; invalid labels: 0; rows excluded for either: 0.
- Valid rows outside the holdout period: 18266; they were not used for this evaluation.
- Test class distribution: `{"fatal": 262, "major": 489, "minor": 983}`.

## Test metrics

| Model                   | Accuracy | Macro-P | Macro-R | Macro-F1 | Weighted-P | Weighted-R | Weighted-F1 |
| ----------------------- | -------- | ------- | ------- | -------- | ---------- | ---------- | ----------- |
| Random Forest           | 0.4429   | 0.3495  | 0.3468  | 0.3472   | 0.4358     | 0.4429     | 0.4389      |
| Majority-class baseline | 0.5669   | 0.1890  | 0.3333  | 0.2412   | 0.3214     | 0.5669     | 0.4102      |

Per-class precision, recall, F1, support, and both confusion matrices are saved in CSV files alongside this report. Evaluation elapsed time: selected pipeline 0.285561 seconds; baseline prediction 0.000016 seconds.

## Interpretation and limitations

These metrics describe a held-out slice of the supplied CSV only. The repository does not document the dataset's source or establish that its rows are verified real-world accident observations. The model predicts severity conditional on an accident record; it does not predict whether an accident will happen or detect accidents in real time. The Jan-Apr 2025 holdout is relatively short and cannot establish performance in other years, locations, or operating conditions.

## Outputs

- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_evaluation_metrics.json`: aggregate metrics, split audit, and elapsed evaluation times.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_classification_report.csv`: per-class and aggregate classification metrics.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_confusion_matrix_selected_model.csv`: selected model confusion matrix, actual rows by predicted columns.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_confusion_matrix_baseline.csv`: majority baseline confusion matrix, actual rows by predicted columns.
