"""Compare severity classifiers with expanding chronological validation.

Only records dated 2022-01-01 through 2024-12-31 are eligible. The folds are
2022 -> 2023 and 2022-2023 -> 2024. This script does not inspect 2025 labels or
features for scoring, fitting, preprocessing, model selection, or thresholds.
It writes only to ML/reports/temporal_comparison_selected/ and never saves a model.
"""

from __future__ import annotations

import json
import platform
import time
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "Data" / "indian_roads_project_selected.csv"
OUTPUT_DIR = (
    Path(__file__).resolve().parent / "reports" / "temporal_comparison_selected"
)

DATE_COLUMN = "date"
TARGET_COLUMN = "accident_severity"
LABELS = ["minor", "major", "fatal"]
CATEGORICAL_FEATURES = [
    "road_type",
    "weather",
    "traffic_density",
]
NUMERIC_FEATURES = [
    "hour",
]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
RANDOM_STATE = 42
HISTORICAL_START = pd.Timestamp("2022-01-01")
HISTORICAL_END_EXCLUSIVE = pd.Timestamp("2025-01-01")

OUTPUT_NAMES = [
    "fold_metrics.csv",
    "per_class_metrics.csv",
    "confusion_matrices.csv",
    "summary.csv",
    "run_metadata.json",
    "README.md",
]


def _make_preprocessor() -> ColumnTransformer:
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ],
        remainder="drop",
    )


def _make_pipeline(classifier) -> Pipeline:
    # A fresh preprocessor is fitted inside every model/fold pipeline.
    return Pipeline(
        steps=[
            ("preprocessor", _make_preprocessor()),
            ("classifier", classifier),
        ]
    )


def _candidate_factories() -> list[tuple[str, object]]:
    return [
        (
            "Majority baseline",
            lambda: DummyClassifier(strategy="most_frequent"),
        ),
        (
            "Logistic Regression (unweighted)",
            lambda: LogisticRegression(
                max_iter=1000,
                class_weight=None,
                random_state=RANDOM_STATE,
            ),
        ),
        (
            "Logistic Regression (balanced)",
            lambda: LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
        ),
        (
            "Random Forest (unweighted)",
            lambda: RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_leaf=3,
                class_weight=None,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
        (
            "Random Forest (balanced_subsample)",
            lambda: RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_leaf=3,
                class_weight="balanced_subsample",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
    ]


def _load_historical_rows() -> tuple[pd.DataFrame, dict]:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")

    required = [DATE_COLUMN, TARGET_COLUMN, *FEATURES]
    df = pd.read_csv(DATA_PATH, usecols=required)
    parsed_dates = pd.to_datetime(df[DATE_COLUMN], errors="coerce")

    # Filter to the historical validation window before target normalization,
    # feature conversion, or any model operation. No 2025 labels/features are
    # passed into either fold.
    historical_mask = (
        parsed_dates.ge(HISTORICAL_START)
        & parsed_dates.lt(HISTORICAL_END_EXCLUSIVE)
    )
    historical = df.loc[historical_mask].copy()
    historical[DATE_COLUMN] = parsed_dates.loc[historical_mask]

    normalized_labels = (
        historical[TARGET_COLUMN].astype("string").str.strip().str.lower()
    )
    valid_label = normalized_labels.isin(LABELS).fillna(False)
    excluded_invalid_labels = int((~valid_label).sum())
    historical = historical.loc[valid_label].copy()
    historical[TARGET_COLUMN] = normalized_labels.loc[valid_label].astype(str)

    for column in NUMERIC_FEATURES:
        historical[column] = pd.to_numeric(historical[column], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        historical[column] = historical[column].astype("string")

    if historical.empty:
        raise ValueError("No valid 2022-2024 rows were found.")

    audit = {
        "historical_rows_after_date_and_label_filter": int(len(historical)),
        "historical_invalid_label_rows_excluded": excluded_invalid_labels,
        "historical_date_min": historical[DATE_COLUMN].min().date().isoformat(),
        "historical_date_max": historical[DATE_COLUMN].max().date().isoformat(),
        "historical_target_distribution": {
            label: int((historical[TARGET_COLUMN] == label).sum())
            for label in LABELS
        },
    }
    return historical, audit


def _class_distribution(values: pd.Series) -> dict[str, int]:
    return {label: int((values == label).sum()) for label in LABELS}


def _score(y_true: pd.Series, predictions) -> tuple[dict, list[dict]]:
    result = {"accuracy": float(accuracy_score(y_true, predictions))}
    for average in ("macro", "weighted"):
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true,
            predictions,
            labels=LABELS,
            average=average,
            zero_division=0,
        )
        result[f"{average}_precision"] = float(precision)
        result[f"{average}_recall"] = float(recall)
        result[f"{average}_f1"] = float(f1)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        predictions,
        labels=LABELS,
        average=None,
        zero_division=0,
    )
    per_class = [
        {
            "class": label,
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1": float(f1[index]),
            "support": int(support[index]),
        }
        for index, label in enumerate(LABELS)
    ]
    fatal_row = per_class[LABELS.index("fatal")]
    result["fatal_precision"] = fatal_row["precision"]
    result["fatal_recall"] = fatal_row["recall"]
    return result, per_class


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    rendered = [[str(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in rendered:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    header = "| " + " | ".join(
        value.ljust(widths[index]) for index, value in enumerate(headers)
    ) + " |"
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    body = [
        "| " + " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        ) + " |"
        for row in rendered
    ]
    return "\n".join([header, separator, *body])


def _summary_table(summary: pd.DataFrame) -> str:
    rows = []
    for row in summary.itertuples(index=False):
        rows.append(
            [
                row.model,
                f"{row.mean_accuracy:.4f}",
                f"{row.mean_macro_f1:.4f}",
                f"{row.mean_weighted_f1:.4f}",
                f"{row.mean_fatal_precision:.4f}",
                f"{row.mean_fatal_recall:.4f}",
                f"{row.mean_fit_seconds:.3f}",
                f"{row.mean_predict_seconds:.3f}",
            ]
        )
    return _markdown_table(
        [
            "Model (mean across folds)",
            "Accuracy",
            "Macro-F1",
            "Weighted-F1",
            "Fatal precision",
            "Fatal recall",
            "Fit sec",
            "Predict sec",
        ],
        rows,
    )


def _build_summary(fold_metrics: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        "accuracy",
        "macro_f1",
        "weighted_f1",
        "fatal_precision",
        "fatal_recall",
        "fit_seconds",
        "predict_seconds",
        "total_seconds",
    ]
    rows = []
    for model, group in fold_metrics.groupby("model", sort=False):
        row = {"model": model, "folds": int(len(group))}
        for metric in metric_columns:
            row[f"mean_{metric}"] = float(group[metric].mean())
            row[f"std_{metric}"] = float(group[metric].std(ddof=0))
        rows.append(row)
    return pd.DataFrame(rows)


def _write_readme(
    fold_metrics: pd.DataFrame,
    per_class: pd.DataFrame,
    confusion: pd.DataFrame,
    summary: pd.DataFrame,
    audit: dict,
) -> None:
    fold_rows = []
    for row in fold_metrics.itertuples(index=False):
        fold_rows.append(
            [
                row.fold,
                row.model,
                f"{row.accuracy:.4f}",
                f"{row.macro_f1:.4f}",
                f"{row.weighted_f1:.4f}",
                f"{row.fatal_precision:.4f}",
                f"{row.fatal_recall:.4f}",
                f"{row.fit_seconds:.3f}",
                f"{row.predict_seconds:.3f}",
            ]
        )

    report = f"""# RoadSafe temporal model comparison

## Protocol

- Dataset: `Data/indian_roads_project_selected.csv`; only valid labeled rows dated 2022-01-01 through 2024-12-31 were eligible ({audit['historical_rows_after_date_and_label_filter']} rows; {audit['historical_invalid_label_rows_excluded']} invalid-label rows excluded within that date window).
- Fold 1: train on 2022; validate on 2023.
- Fold 2: train on 2022-2023; validate on 2024.
- The January-April 2025 holdout was not used for fitting, preprocessing, scoring, candidate selection, or threshold tuning.
- All candidates use the four requested predictors (`road_type`, `weather`, `traffic_density`, and `hour`) and a fresh preprocessing pipeline fitted only on that fold's training rows: median imputation and standard scaling for `hour`; most-frequent imputation and one-hot encoding with unknown categories ignored for the categorical columns. `date` is used only to establish chronology; `cause` and `casualties` are excluded because they describe the recorded accident outcome.
- Class weighting is compared within logistic regression (none vs `balanced`) and random forest (none vs `balanced_subsample`). The forest settings are fixed at 100 trees, depth 12, and minimum leaf size 3. No hyperparameter search was run.
- No probability thresholds were tuned; predictions use each classifier's default `predict` decision. Fit and prediction durations are measured separately for every fold and candidate.
- Per-fold accuracy, macro-F1, weighted-F1, fatal precision/recall, per-class results, and confusion counts are recorded below and in the accompanying CSV files. Summary means give the two validation years equal weight; standard deviations are also saved in `summary.csv`.

## Mean results across folds

{_summary_table(summary)}

## Per-fold results

{_markdown_table(['Fold', 'Model', 'Accuracy', 'Macro-F1', 'Weighted-F1', 'Fatal P', 'Fatal R', 'Fit sec', 'Predict sec'], fold_rows)}

Full per-class precision, recall, F1, and support are in `per_class_metrics.csv`.

## Confusion matrices

Rows are actual labels and columns are predicted labels, ordered `minor`, `major`, `fatal`.

"""
    for fold in fold_metrics["fold"].drop_duplicates().tolist():
        for model in fold_metrics.loc[fold_metrics["fold"] == fold, "model"]:
            subset = confusion.loc[
                (confusion["fold"] == fold) & (confusion["model"] == model)
            ]
            lookup = {
                (row.actual, row.predicted): int(row.count)
                for row in subset.itertuples(index=False)
            }
            matrix_rows = [
                [actual, *[lookup[(actual, predicted)] for predicted in LABELS]]
                for actual in LABELS
            ]
            report += f"### {fold}: {model}\n\n"
            report += _markdown_table(["Actual \\ Predicted", *LABELS], matrix_rows)
            report += "\n\n"

    # Show the weighting tradeoff without declaring recall alone to be a
    # measure of safety or selecting any candidate.
    report += "## Class-weighting comparison\n\n"
    weighting_rows = []
    for fold in fold_metrics["fold"].drop_duplicates().tolist():
        fold_data = fold_metrics[fold_metrics["fold"] == fold].set_index("model")
        for unweighted, weighted in [
            ("Logistic Regression (unweighted)", "Logistic Regression (balanced)"),
            ("Random Forest (unweighted)", "Random Forest (balanced_subsample)"),
        ]:
            left = fold_data.loc[unweighted]
            right = fold_data.loc[weighted]
            weighting_rows.append(
                [
                    fold,
                    unweighted.replace(" (unweighted)", ""),
                    f"{left['fatal_recall']:.4f}",
                    f"{right['fatal_recall']:.4f}",
                    f"{left['fatal_precision']:.4f}",
                    f"{right['fatal_precision']:.4f}",
                    f"{left['accuracy']:.4f}",
                    f"{right['accuracy']:.4f}",
                ]
            )
    report += _markdown_table(
        [
            "Fold",
            "Classifier",
            "Unweighted fatal R",
            "Weighted fatal R",
            "Unweighted fatal P",
            "Weighted fatal P",
            "Unweighted accuracy",
            "Weighted accuracy",
        ],
        weighting_rows,
    )
    report += """

Class weighting can change both fatal recall and false-positive behavior. A higher fatal recall does not by itself mean a better or safer model; the corresponding fatal precision and confusion matrices show the tradeoff, and acceptable costs have not been established for this project.

## Limitations

- The repository does not establish the dataset's upstream source, whether records are observed or synthetic, or how severity labels were assigned. See `ML/DATASET_PROVENANCE.md`.
- These are two chronological validation folds from one supplied CSV. They do not establish real-world performance or performance after 2024.
- The comparison uses the existing feature set for consistency; field measurement definitions and availability are not fully documented.
- No model is selected or claimed to outperform the existing model by this report. The 2025 holdout remains outside this comparison.
- Execution times depend on the machine and its current load; they are descriptive, not a benchmark.
"""
    (OUTPUT_DIR / "README.md").write_text(report, encoding="utf-8")


def main() -> None:
    output_paths = [OUTPUT_DIR / name for name in OUTPUT_NAMES]
    already_present = [path for path in output_paths if path.exists()]
    if already_present:
        paths = ", ".join(str(path) for path in already_present)
        raise FileExistsError(
            "Refusing to overwrite temporal comparison outputs: " + paths
        )

    historical, audit = _load_historical_rows()
    fold_specs = [
        (
            "train_2022_validate_2023",
            pd.Timestamp("2022-01-01"),
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2024-01-01"),
        ),
        (
            "train_2022_2023_validate_2024",
            pd.Timestamp("2022-01-01"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2025-01-01"),
        ),
    ]

    fold_rows: list[dict] = []
    per_class_rows: list[dict] = []
    confusion_rows: list[dict] = []
    fold_audit: list[dict] = []

    for fold_name, train_start, train_end, valid_start, valid_end in fold_specs:
        train_mask = historical[DATE_COLUMN].ge(train_start) & historical[
            DATE_COLUMN
        ].lt(train_end)
        valid_mask = historical[DATE_COLUMN].ge(valid_start) & historical[
            DATE_COLUMN
        ].lt(valid_end)

        train_df = historical.loc[train_mask, FEATURES].copy()
        valid_df = historical.loc[valid_mask, FEATURES].copy()
        y_train = historical.loc[train_mask, TARGET_COLUMN].astype(str)
        y_valid = historical.loc[valid_mask, TARGET_COLUMN].astype(str)
        if train_df.empty or valid_df.empty:
            raise ValueError(f"Fold {fold_name} has an empty train or validation split.")

        missing_train_labels = sorted(set(LABELS) - set(y_train.unique()))
        if missing_train_labels:
            raise ValueError(
                f"Fold {fold_name} training rows lack classes: "
                + ", ".join(missing_train_labels)
            )

        fold_audit.append(
            {
                "fold": fold_name,
                "train_start": train_start.date().isoformat(),
                "train_end_inclusive": (train_end - pd.Timedelta(days=1)).date().isoformat(),
                "validation_start": valid_start.date().isoformat(),
                "validation_end_inclusive": (valid_end - pd.Timedelta(days=1)).date().isoformat(),
                "train_rows": int(len(train_df)),
                "validation_rows": int(len(valid_df)),
                "train_class_distribution": _class_distribution(y_train),
                "validation_class_distribution": _class_distribution(y_valid),
            }
        )

        for model_name, factory in _candidate_factories():
            pipeline = _make_pipeline(factory())
            fit_started = time.perf_counter()
            pipeline.fit(train_df, y_train)
            fit_seconds = time.perf_counter() - fit_started

            predict_started = time.perf_counter()
            predictions = pipeline.predict(valid_df)
            predict_seconds = time.perf_counter() - predict_started

            metrics, class_rows = _score(y_valid, predictions)
            fold_rows.append(
                {
                    "fold": fold_name,
                    "model": model_name,
                    "train_rows": int(len(train_df)),
                    "validation_rows": int(len(valid_df)),
                    **metrics,
                    "fit_seconds": float(fit_seconds),
                    "predict_seconds": float(predict_seconds),
                    "total_seconds": float(fit_seconds + predict_seconds),
                }
            )
            per_class_rows.extend(
                {"fold": fold_name, "model": model_name, **row}
                for row in class_rows
            )

            matrix = confusion_matrix(y_valid, predictions, labels=LABELS)
            for actual_index, actual in enumerate(LABELS):
                for predicted_index, predicted in enumerate(LABELS):
                    confusion_rows.append(
                        {
                            "fold": fold_name,
                            "model": model_name,
                            "actual": actual,
                            "predicted": predicted,
                            "count": int(matrix[actual_index, predicted_index]),
                        }
                    )

    fold_metrics = pd.DataFrame(fold_rows)
    per_class = pd.DataFrame(per_class_rows)
    confusion = pd.DataFrame(confusion_rows)
    summary = _build_summary(fold_metrics)
    run_metadata = {
        "dataset_path": str(DATA_PATH),
        "target_column": TARGET_COLUMN,
        "class_labels": LABELS,
        "date_column": DATE_COLUMN,
        "historical_window": "2022-01-01 through 2024-12-31",
        "future_holdout_used": False,
        "folds": fold_audit,
        "historical_data_audit": audit,
        "feature_columns": FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "preprocessing": {
            "categorical": "most-frequent imputation then one-hot encoding; unknown categories ignored",
            "numeric": "median imputation then standard scaling",
            "fit_scope": "inside each candidate pipeline, on that fold's training rows only",
        },
        "candidates": [
            {
                "name": "Majority baseline",
                "estimator": "DummyClassifier",
                "parameters": {"strategy": "most_frequent"},
            },
            {
                "name": "Logistic Regression (unweighted)",
                "estimator": "LogisticRegression",
                "parameters": {"max_iter": 1000, "class_weight": None, "random_state": RANDOM_STATE},
            },
            {
                "name": "Logistic Regression (balanced)",
                "estimator": "LogisticRegression",
                "parameters": {"max_iter": 1000, "class_weight": "balanced", "random_state": RANDOM_STATE},
            },
            {
                "name": "Random Forest (unweighted)",
                "estimator": "RandomForestClassifier",
                "parameters": {
                    "n_estimators": 100,
                    "max_depth": 12,
                    "min_samples_leaf": 3,
                    "class_weight": None,
                    "random_state": RANDOM_STATE,
                    "n_jobs": -1,
                },
            },
            {
                "name": "Random Forest (balanced_subsample)",
                "estimator": "RandomForestClassifier",
                "parameters": {
                    "n_estimators": 100,
                    "max_depth": 12,
                    "min_samples_leaf": 3,
                    "class_weight": "balanced_subsample",
                    "random_state": RANDOM_STATE,
                    "n_jobs": -1,
                },
            },
        ],
        "probability_threshold_tuning": "not performed",
        "random_state": RANDOM_STATE,
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "scikit_learn_version": sklearn.__version__,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fold_metrics.to_csv(OUTPUT_DIR / "fold_metrics.csv", index=False)
    per_class.to_csv(OUTPUT_DIR / "per_class_metrics.csv", index=False)
    confusion.to_csv(OUTPUT_DIR / "confusion_matrices.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "summary.csv", index=False)
    (OUTPUT_DIR / "run_metadata.json").write_text(
        json.dumps(run_metadata, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    _write_readme(fold_metrics, per_class, confusion, summary, audit)

    print(f"Historical rows evaluated: {audit['historical_rows_after_date_and_label_filter']}")
    print(f"2025 holdout used: {run_metadata['future_holdout_used']}")
    print(f"Outputs: {OUTPUT_DIR}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
