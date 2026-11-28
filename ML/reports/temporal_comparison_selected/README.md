# RoadSafe temporal model comparison

## Protocol

- Dataset: `Data/indian_roads_project_selected.csv`; only valid labeled rows dated 2022-01-01 through 2024-12-31 were eligible (18266 rows; 0 invalid-label rows excluded within that date window).
- Fold 1: train on 2022; validate on 2023.
- Fold 2: train on 2022-2023; validate on 2024.
- The January-April 2025 holdout was not used for fitting, preprocessing, scoring, candidate selection, or threshold tuning.
- All candidates use the four requested predictors (`road_type`, `weather`, `traffic_density`, and `hour`) and a fresh preprocessing pipeline fitted only on that fold's training rows: median imputation and standard scaling for `hour`; most-frequent imputation and one-hot encoding with unknown categories ignored for the categorical columns. `date` is used only to establish chronology; `cause` and `casualties` are excluded because they describe the recorded accident outcome.
- Class weighting is compared within logistic regression (none vs `balanced`) and random forest (none vs `balanced_subsample`). The forest settings are fixed at 100 trees, depth 12, and minimum leaf size 3. No hyperparameter search was run.
- No probability thresholds were tuned; predictions use each classifier's default `predict` decision. Fit and prediction durations are measured separately for every fold and candidate.
- Per-fold accuracy, macro-F1, weighted-F1, fatal precision/recall, per-class results, and confusion counts are recorded below and in the accompanying CSV files. Summary means give the two validation years equal weight; standard deviations are also saved in `summary.csv`.

## Mean results across folds

| Model (mean across folds)          | Accuracy | Macro-F1 | Weighted-F1 | Fatal precision | Fatal recall | Fit sec | Predict sec |
| ---------------------------------- | -------- | -------- | ----------- | --------------- | ------------ | ------- | ----------- |
| Majority baseline                  | 0.5537   | 0.2376   | 0.3947      | 0.0000          | 0.0000       | 0.051   | 0.008       |
| Logistic Regression (unweighted)   | 0.5537   | 0.2376   | 0.3947      | 0.0000          | 0.0000       | 0.051   | 0.010       |
| Logistic Regression (balanced)     | 0.3217   | 0.3029   | 0.3449      | 0.1412          | 0.3539       | 0.060   | 0.012       |
| Random Forest (unweighted)         | 0.5177   | 0.3003   | 0.4358      | 0.1997          | 0.0155       | 0.368   | 0.062       |
| Random Forest (balanced_subsample) | 0.3571   | 0.3257   | 0.3766      | 0.1516          | 0.3016       | 0.442   | 0.074       |

## Per-fold results

| Fold                          | Model                              | Accuracy | Macro-F1 | Weighted-F1 | Fatal P | Fatal R | Fit sec | Predict sec |
| ----------------------------- | ---------------------------------- | -------- | -------- | ----------- | ------- | ------- | ------- | ----------- |
| train_2022_validate_2023      | Majority baseline                  | 0.5562   | 0.2383   | 0.3976      | 0.0000  | 0.0000  | 0.077   | 0.008       |
| train_2022_validate_2023      | Logistic Regression (unweighted)   | 0.5562   | 0.2383   | 0.3976      | 0.0000  | 0.0000  | 0.031   | 0.007       |
| train_2022_validate_2023      | Logistic Regression (balanced)     | 0.3284   | 0.3055   | 0.3543      | 0.1346  | 0.3468  | 0.040   | 0.008       |
| train_2022_validate_2023      | Random Forest (unweighted)         | 0.5151   | 0.3114   | 0.4447      | 0.1900  | 0.0213  | 0.359   | 0.054       |
| train_2022_validate_2023      | Random Forest (balanced_subsample) | 0.3706   | 0.3306   | 0.3901      | 0.1517  | 0.2941  | 0.394   | 0.095       |
| train_2022_2023_validate_2024 | Majority baseline                  | 0.5512   | 0.2369   | 0.3918      | 0.0000  | 0.0000  | 0.024   | 0.007       |
| train_2022_2023_validate_2024 | Logistic Regression (unweighted)   | 0.5512   | 0.2369   | 0.3918      | 0.0000  | 0.0000  | 0.072   | 0.013       |
| train_2022_2023_validate_2024 | Logistic Regression (balanced)     | 0.3150   | 0.3004   | 0.3355      | 0.1477  | 0.3611  | 0.081   | 0.017       |
| train_2022_2023_validate_2024 | Random Forest (unweighted)         | 0.5204   | 0.2892   | 0.4269      | 0.2093  | 0.0097  | 0.376   | 0.070       |
| train_2022_2023_validate_2024 | Random Forest (balanced_subsample) | 0.3437   | 0.3208   | 0.3631      | 0.1514  | 0.3092  | 0.490   | 0.053       |

Full per-class precision, recall, F1, and support are in `per_class_metrics.csv`.

## Confusion matrices

Rows are actual labels and columns are predicted labels, ordered `minor`, `major`, `fatal`.

### train_2022_validate_2023: Majority baseline

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3386  | 0     | 0     |
| major              | 1811  | 0     | 0     |
| fatal              | 891   | 0     | 0     |

### train_2022_validate_2023: Logistic Regression (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3386  | 0     | 0     |
| major              | 1811  | 0     | 0     |
| fatal              | 891   | 0     | 0     |

### train_2022_validate_2023: Logistic Regression (balanced)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 1174  | 924   | 1288  |
| major              | 596   | 516   | 699   |
| fatal              | 319   | 263   | 309   |

### train_2022_validate_2023: Random Forest (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 2797  | 538   | 51    |
| major              | 1461  | 320   | 30    |
| fatal              | 737   | 135   | 19    |

### train_2022_validate_2023: Random Forest (balanced_subsample)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 1438  | 999   | 949   |
| major              | 739   | 556   | 516   |
| fatal              | 372   | 257   | 262   |

### train_2022_2023_validate_2024: Majority baseline

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3341  | 0     | 0     |
| major              | 1795  | 0     | 0     |
| fatal              | 925   | 0     | 0     |

### train_2022_2023_validate_2024: Logistic Regression (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3341  | 0     | 0     |
| major              | 1795  | 0     | 0     |
| fatal              | 925   | 0     | 0     |

### train_2022_2023_validate_2024: Logistic Regression (balanced)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 1006  | 1062  | 1273  |
| major              | 572   | 569   | 654   |
| fatal              | 283   | 308   | 334   |

### train_2022_2023_validate_2024: Random Forest (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 2930  | 390   | 21    |
| major              | 1567  | 215   | 13    |
| fatal              | 820   | 96    | 9     |

### train_2022_2023_validate_2024: Random Forest (balanced_subsample)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 1136  | 1148  | 1057  |
| major              | 588   | 661   | 546   |
| fatal              | 334   | 305   | 286   |

## Class-weighting comparison

| Fold                          | Classifier          | Unweighted fatal R | Weighted fatal R | Unweighted fatal P | Weighted fatal P | Unweighted accuracy | Weighted accuracy |
| ----------------------------- | ------------------- | ------------------ | ---------------- | ------------------ | ---------------- | ------------------- | ----------------- |
| train_2022_validate_2023      | Logistic Regression | 0.0000             | 0.3468           | 0.0000             | 0.1346           | 0.5562              | 0.3284            |
| train_2022_validate_2023      | Random Forest       | 0.0213             | 0.2941           | 0.1900             | 0.1517           | 0.5151              | 0.3706            |
| train_2022_2023_validate_2024 | Logistic Regression | 0.0000             | 0.3611           | 0.0000             | 0.1477           | 0.5512              | 0.3150            |
| train_2022_2023_validate_2024 | Random Forest       | 0.0097             | 0.3092           | 0.2093             | 0.1514           | 0.5204              | 0.3437            |

Class weighting can change both fatal recall and false-positive behavior. A higher fatal recall does not by itself mean a better or safer model; the corresponding fatal precision and confusion matrices show the tradeoff, and acceptable costs have not been established for this project.

## Limitations

- The repository does not establish the dataset's upstream source, whether records are observed or synthetic, or how severity labels were assigned. See `ML/DATASET_PROVENANCE.md`.
- These are two chronological validation folds from one supplied CSV. They do not establish real-world performance or performance after 2024.
- The comparison uses the existing feature set for consistency; field measurement definitions and availability are not fully documented.
- No model is selected or claimed to outperform the existing model by this report. The 2025 holdout remains outside this comparison.
- Execution times depend on the machine and its current load; they are descriptive, not a benchmark.
