# RoadSafe temporal model comparison

## Protocol

- Dataset: `Data/indian_roads_cleaned.csv`; only valid labeled rows dated 2022-01-01 through 2024-12-31 were eligible (18266 rows; 0 invalid-label rows excluded within that date window).
- Fold 1: train on 2022; validate on 2023.
- Fold 2: train on 2022-2023; validate on 2024.
- The January-April 2025 holdout was not used for fitting, preprocessing, scoring, candidate selection, or threshold tuning.
- All candidates use the same 11 features and a fresh preprocessing pipeline fitted only on that fold's training rows: median imputation and standard scaling for numeric columns; most-frequent imputation and one-hot encoding with unknown categories ignored for categorical columns.
- Class weighting is compared within logistic regression (none vs `balanced`) and random forest (none vs `balanced_subsample`). The forest settings are fixed at 100 trees, depth 12, and minimum leaf size 3. No hyperparameter search was run.
- No probability thresholds were tuned; predictions use each classifier's default `predict` decision. Fit and prediction durations are measured separately for every fold and candidate.
- Per-fold accuracy, macro-F1, weighted-F1, fatal precision/recall, per-class results, and confusion counts are recorded below and in the accompanying CSV files. Summary means give the two validation years equal weight; standard deviations are also saved in `summary.csv`.

## Mean results across folds

| Model (mean across folds)          | Accuracy | Macro-F1 | Weighted-F1 | Fatal precision | Fatal recall | Fit sec | Predict sec |
| ---------------------------------- | -------- | -------- | ----------- | --------------- | ------------ | ------- | ----------- |
| Majority baseline                  | 0.5537   | 0.2376   | 0.3947      | 0.0000          | 0.0000       | 0.131   | 0.024       |
| Logistic Regression (unweighted)   | 0.5536   | 0.2377   | 0.3948      | 0.0000          | 0.0000       | 0.204   | 0.023       |
| Logistic Regression (balanced)     | 0.3178   | 0.3001   | 0.3393      | 0.1409          | 0.3346       | 0.183   | 0.027       |
| Random Forest (unweighted)         | 0.5417   | 0.2608   | 0.4119      | 0.1250          | 0.0006       | 0.698   | 0.133       |
| Random Forest (balanced_subsample) | 0.4284   | 0.3326   | 0.4225      | 0.1449          | 0.1180       | 0.999   | 0.135       |

## Per-fold results

| Fold                          | Model                              | Accuracy | Macro-F1 | Weighted-F1 | Fatal P | Fatal R | Fit sec | Predict sec |
| ----------------------------- | ---------------------------------- | -------- | -------- | ----------- | ------- | ------- | ------- | ----------- |
| train_2022_validate_2023      | Majority baseline                  | 0.5562   | 0.2383   | 0.3976      | 0.0000  | 0.0000  | 0.192   | 0.025       |
| train_2022_validate_2023      | Logistic Regression (unweighted)   | 0.5562   | 0.2383   | 0.3976      | 0.0000  | 0.0000  | 0.136   | 0.024       |
| train_2022_validate_2023      | Logistic Regression (balanced)     | 0.3262   | 0.3056   | 0.3489      | 0.1377  | 0.3244  | 0.115   | 0.028       |
| train_2022_validate_2023      | Random Forest (unweighted)         | 0.5424   | 0.2774   | 0.4278      | 0.2500  | 0.0011  | 0.682   | 0.132       |
| train_2022_validate_2023      | Random Forest (balanced_subsample) | 0.4428   | 0.3359   | 0.4335      | 0.1313  | 0.0988  | 0.883   | 0.133       |
| train_2022_2023_validate_2024 | Majority baseline                  | 0.5512   | 0.2369   | 0.3918      | 0.0000  | 0.0000  | 0.070   | 0.023       |
| train_2022_2023_validate_2024 | Logistic Regression (unweighted)   | 0.5511   | 0.2372   | 0.3920      | 0.0000  | 0.0000  | 0.271   | 0.022       |
| train_2022_2023_validate_2024 | Logistic Regression (balanced)     | 0.3094   | 0.2947   | 0.3297      | 0.1441  | 0.3449  | 0.252   | 0.025       |
| train_2022_2023_validate_2024 | Random Forest (unweighted)         | 0.5410   | 0.2442   | 0.3960      | 0.0000  | 0.0000  | 0.714   | 0.135       |
| train_2022_2023_validate_2024 | Random Forest (balanced_subsample) | 0.4140   | 0.3293   | 0.4116      | 0.1586  | 0.1373  | 1.114   | 0.136       |

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
| minor              | 1095  | 1111  | 1180  |
| major              | 579   | 602   | 630   |
| fatal              | 312   | 290   | 289   |

### train_2022_validate_2023: Random Forest (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3153  | 230   | 3     |
| major              | 1663  | 148   | 0     |
| fatal              | 829   | 61    | 1     |

### train_2022_validate_2023: Random Forest (balanced_subsample)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 2048  | 964   | 374   |
| major              | 1043  | 560   | 208   |
| fatal              | 554   | 249   | 88    |

### train_2022_2023_validate_2024: Majority baseline

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3341  | 0     | 0     |
| major              | 1795  | 0     | 0     |
| fatal              | 925   | 0     | 0     |

### train_2022_2023_validate_2024: Logistic Regression (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3339  | 2     | 0     |
| major              | 1794  | 1     | 0     |
| fatal              | 924   | 1     | 0     |

### train_2022_2023_validate_2024: Logistic Regression (balanced)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 983   | 1128  | 1230  |
| major              | 557   | 573   | 665   |
| fatal              | 283   | 323   | 319   |

### train_2022_2023_validate_2024: Random Forest (unweighted)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 3249  | 91    | 1     |
| major              | 1765  | 30    | 0     |
| fatal              | 905   | 20    | 0     |

### train_2022_2023_validate_2024: Random Forest (balanced_subsample)

| Actual \ Predicted | minor | major | fatal |
| ------------------ | ----- | ----- | ----- |
| minor              | 1847  | 1060  | 434   |
| major              | 1020  | 535   | 240   |
| fatal              | 515   | 283   | 127   |

## Class-weighting comparison

| Fold                          | Classifier          | Unweighted fatal R | Weighted fatal R | Unweighted fatal P | Weighted fatal P | Unweighted accuracy | Weighted accuracy |
| ----------------------------- | ------------------- | ------------------ | ---------------- | ------------------ | ---------------- | ------------------- | ----------------- |
| train_2022_validate_2023      | Logistic Regression | 0.0000             | 0.3244           | 0.0000             | 0.1377           | 0.5562              | 0.3262            |
| train_2022_validate_2023      | Random Forest       | 0.0011             | 0.0988           | 0.2500             | 0.1313           | 0.5424              | 0.4428            |
| train_2022_2023_validate_2024 | Logistic Regression | 0.0000             | 0.3449           | 0.0000             | 0.1441           | 0.5511              | 0.3094            |
| train_2022_2023_validate_2024 | Random Forest       | 0.0000             | 0.1373           | 0.0000             | 0.1586           | 0.5410              | 0.4140            |

Class weighting can change both fatal recall and false-positive behavior. A higher fatal recall does not by itself mean a better or safer model; the corresponding fatal precision and confusion matrices show the tradeoff, and acceptable costs have not been established for this project.

## Limitations

- The repository does not establish the dataset's upstream source, whether records are observed or synthetic, or how severity labels were assigned. See `ML/DATASET_PROVENANCE.md`.
- These are two chronological validation folds from one supplied CSV. They do not establish real-world performance or performance after 2024.
- The comparison uses the existing feature set for consistency; field measurement definitions and availability are not fully documented.
- No model is selected or claimed to outperform the existing model by this report. The 2025 holdout remains outside this comparison.
- Execution times depend on the machine and its current load; they are descriptive, not a benchmark.
