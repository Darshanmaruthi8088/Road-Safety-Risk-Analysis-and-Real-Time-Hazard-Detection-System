# RoadSafe severity model holdout evaluation

## Evaluation design

- Dataset: 20000 rows by 11 columns. Valid target-class distribution across the source file: `{"fatal": 2987, "major": 5988, "minor": 11025}`.
- Data quality check: 0 missing cells and 0 duplicate rows. Accident IDs are not part of this selected schema, so duplicate IDs cannot be checked here.
- Selected model: **Random Forest**, chosen using 2024 validation macro-F1 (0.3208).
- Holdout: 2025-01-01 through 2025-04-30 (1734 rows), evaluated once after model selection.
- Training and preprocessing fit period: 2022-01-01 through 2023-12-31 (12205 rows). The saved pipeline is loaded and used for prediction; this script does not fit or tune it.
- Date column: `date` parsed with `pandas.to_datetime(errors='coerce')`. Invalid dates: 0; invalid labels: 0; rows excluded for either: 0.
- Valid rows outside the holdout period: 18266; they were not used for this evaluation.
- Test class distribution: `{"fatal": 262, "major": 489, "minor": 983}`.

## Test metrics

| Model                   | Accuracy | Macro-P | Macro-R | Macro-F1 | Weighted-P | Weighted-R | Weighted-F1 |
| ----------------------- | -------- | ------- | ------- | -------- | ---------- | ---------- | ----------- |
| Random Forest           | 0.3576   | 0.3464  | 0.3499  | 0.3299   | 0.4370     | 0.3576     | 0.3791      |
| Majority-class baseline | 0.5669   | 0.1890  | 0.3333  | 0.2412   | 0.3214     | 0.5669     | 0.4102      |

### Per-class metrics

| Model                   | Class / average | Precision | Recall | F1     | Support |
| ----------------------- | --------------- | --------- | ------ | ------ | ------- |
| Random Forest           | minor           | 0.5805    | 0.3703 | 0.4522 | 983     |
| Random Forest           | major           | 0.2947    | 0.3436 | 0.3173 | 489     |
| Random Forest           | fatal           | 0.1639    | 0.3359 | 0.2203 | 262     |
| Random Forest           | macro avg       | 0.3464    | 0.3499 | 0.3299 | 1734    |
| Random Forest           | weighted avg    | 0.4370    | 0.3576 | 0.3791 | 1734    |
| Random Forest           | accuracy        |           |        | 0.3576 | 1734    |
| Majority-class baseline | minor           | 0.5669    | 1.0000 | 0.7236 | 983     |
| Majority-class baseline | major           | 0.0000    | 0.0000 | 0.0000 | 489     |
| Majority-class baseline | fatal           | 0.0000    | 0.0000 | 0.0000 | 262     |
| Majority-class baseline | macro avg       | 0.1890    | 0.3333 | 0.2412 | 1734    |
| Majority-class baseline | weighted avg    | 0.3214    | 0.5669 | 0.4102 | 1734    |
| Majority-class baseline | accuracy        |           |        | 0.5669 | 1734    |

### Confusion matrix: selected model

Rows are actual classes and columns are predicted classes.

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 364   | 314   | 305   |
| major              | 177   | 168   | 144   |
| fatal              | 86    | 88    | 88    |

### Confusion matrix: majority baseline

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 983   | 0     | 0     |
| major              | 489   | 0     | 0     |
| fatal              | 262   | 0     | 0     |

Evaluation elapsed time: selected pipeline 0.094982 seconds; baseline prediction 0.000015 seconds. Fit and validation time for every candidate is recorded in `validation_model_comparison.csv`.

## Interpretation and limitations

These metrics describe a held-out slice of the supplied CSV only. The repository does not document the dataset's source or establish that its rows are verified real-world accident observations. The model predicts severity conditional on an accident record; it does not predict whether an accident will happen or detect accidents in real time. The Jan-Apr 2025 holdout is relatively short and cannot establish performance in other years, locations, or operating conditions.

The classes are imbalanced, with minor accidents making up the largest share. Accuracy should be read together with macro-F1 and the per-class metrics. On the holdout, fatal-class precision is 0.1639, recall is 0.3359, and F1 is 0.2203 (support: 262). This measures classification on this CSV only and is not evidence of operational road-safety performance.

## Outputs

- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_evaluation_metrics.json`: aggregate metrics, split audit, and elapsed evaluation times.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_classification_report.csv`: per-class and aggregate classification metrics.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_confusion_matrix_selected_model.csv`: selected model confusion matrix, actual rows by predicted columns.
- `C:\Users\dd708\OneDrive\Documents\aa5th sem notes\DEV\DEV Filtration\ML\reports\test_confusion_matrix_baseline.csv`: majority baseline confusion matrix, actual rows by predicted columns.
