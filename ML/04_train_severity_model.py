"""Train and select an offline accident-severity classifier.

The chronology is fixed to train on 2022-2023 and select on 2024. The
2025-01 through 2025-04 holdout is reserved for 05_evaluate_severity_model.py.
No application module imports this script.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "Data" / "indian_roads_project_selected.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "model_artifacts"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
MODEL_PATH = ARTIFACT_DIR / "severity_pipeline.joblib"
METADATA_PATH = ARTIFACT_DIR / "severity_model_metadata.json"
COMPARISON_PATH = REPORT_DIR / "validation_model_comparison.csv"
AUDIT_PATH = REPORT_DIR / "training_data_audit.json"
REPORT_PATH = REPORT_DIR / "training_report.md"

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
TRAIN_START = pd.Timestamp("2022-01-01")
VALIDATION_START = pd.Timestamp("2024-01-01")
TEST_START = pd.Timestamp("2025-01-01")
TEST_END_EXCLUSIVE = pd.Timestamp("2025-05-01")


def _json_write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    rendered = [[str(value) for value in row] for row in rows]
    widths = [len(str(header)) for header in headers]
    for row in rendered:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    header_line = "| " + " | ".join(
        str(value).ljust(widths[index]) for index, value in enumerate(headers)
    ) + " |"
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    body = [
        "| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(row)) + " |"
        for row in rendered
    ]
    return "\n".join([header_line, separator, *body])


def _metrics(y_true: pd.Series, y_pred, labels: list[str]) -> dict[str, float]:
    result = {"accuracy": float(accuracy_score(y_true, y_pred))}
    for average in ("macro", "weighted"):
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            average=average,
            zero_division=0,
        )
        result[f"{average}_precision"] = float(precision)
        result[f"{average}_recall"] = float(recall)
        result[f"{average}_f1"] = float(f1)
    return result


def _split_summary(labels: pd.Series) -> dict[str, int]:
    return {label: int((labels == label).sum()) for label in LABELS}


def _load_and_audit() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, dict]:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    required = [DATE_COLUMN, TARGET_COLUMN, *FEATURES]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(
            "Required date, target, or feature columns are missing: "
            + ", ".join(missing)
        )

    parsed_dates = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    normalized_labels = df[TARGET_COLUMN].astype("string").str.strip().str.lower()
    valid_label = normalized_labels.isin(LABELS).fillna(False)
    valid_date = parsed_dates.notna()

    train_mask = (
        valid_date
        & valid_label
        & (parsed_dates >= TRAIN_START)
        & (parsed_dates < VALIDATION_START)
    )
    validation_mask = (
        valid_date
        & valid_label
        & (parsed_dates >= VALIDATION_START)
        & (parsed_dates < TEST_START)
    )
    test_mask = (
        valid_date
        & valid_label
        & (parsed_dates >= TEST_START)
        & (parsed_dates < TEST_END_EXCLUSIVE)
    )
    in_window = train_mask | validation_mask | test_mask
    date_invalid = ~valid_date
    label_invalid = ~valid_label
    invalid_union = date_invalid | label_invalid
    outside_window = valid_date & valid_label & ~in_window

    train_df = df.loc[train_mask, FEATURES].copy()
    validation_df = df.loc[validation_mask, FEATURES].copy()
    y_train = normalized_labels.loc[train_mask].astype(str)
    y_validation = normalized_labels.loc[validation_mask].astype(str)

    for column in NUMERIC_FEATURES:
        train_df[column] = pd.to_numeric(train_df[column], errors="coerce")
        validation_df[column] = pd.to_numeric(validation_df[column], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        train_df[column] = train_df[column].astype("string")
        validation_df[column] = validation_df[column].astype("string")

    if train_df.empty or validation_df.empty:
        raise ValueError("Chronological train or validation split is empty.")
    missing_train_classes = sorted(set(LABELS) - set(y_train.unique()))
    if missing_train_classes:
        raise ValueError(
            "Training years do not contain all expected classes: "
            + ", ".join(missing_train_classes)
        )

    date_min = parsed_dates.min()
    date_max = parsed_dates.max()
    audit = {
        "dataset_path": str(DATA_PATH),
        "dataset_rows": int(len(df)),
        "dataset_columns": int(len(df.columns)),
        "available_columns": list(df.columns),
        "target_class_distribution_all_valid_labels": {
            label: int((normalized_labels == label).sum()) for label in LABELS
        },
        "dataset_missing_values_by_column": {
            column: int(df[column].isna().sum()) for column in df.columns
        },
        "dataset_duplicate_rows": int(df.duplicated().sum()),
        "dataset_duplicate_accident_ids": None,
        "date_column": DATE_COLUMN,
        "date_source_dtype": str(df[DATE_COLUMN].dtype),
        "date_parse_method": "pandas.to_datetime(errors='coerce')",
        "date_parse_failures": int(date_invalid.sum()),
        "parsed_date_min": None if pd.isna(date_min) else date_min.date().isoformat(),
        "parsed_date_max": None if pd.isna(date_max) else date_max.date().isoformat(),
        "target_column": TARGET_COLUMN,
        "valid_labels": LABELS,
        "invalid_label_rows": int(label_invalid.sum()),
        "invalid_date_only_rows": int((date_invalid & ~label_invalid).sum()),
        "invalid_label_only_rows": int((label_invalid & ~date_invalid).sum()),
        "invalid_date_and_label_rows": int((date_invalid & label_invalid).sum()),
        "rows_excluded_for_invalid_date_or_label": int(invalid_union.sum()),
        "rows_excluded_outside_requested_periods": int(outside_window.sum()),
        "rows_in_train_period": int(train_mask.sum()),
        "rows_in_validation_period": int(validation_mask.sum()),
        "rows_in_test_period": int(test_mask.sum()),
        "train_period": "2022-01-01 through 2023-12-31",
        "validation_period": "2024-01-01 through 2024-12-31",
        "test_period": "2025-01-01 through 2025-04-30",
        "train_class_distribution": _split_summary(y_train),
        "validation_class_distribution": _split_summary(y_validation),
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "feature_columns": FEATURES,
        "feature_missing_values": {
            column: int(df[column].isna().sum()) for column in FEATURES
        },
        "feature_dtypes": {column: str(df[column].dtype) for column in FEATURES},
    }
    return train_df, y_train, validation_df, y_validation, audit


def _make_preprocessor(scale_numeric: bool) -> ColumnTransformer:
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    numeric_pipeline = Pipeline(steps=numeric_steps)

    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ],
        remainder="drop",
    )


def main() -> None:
    train_df, y_train, validation_df, y_validation, audit = _load_and_audit()

    baseline = DummyClassifier(strategy="most_frequent")
    started = time.perf_counter()
    baseline.fit(train_df, y_train)
    baseline_fit_seconds = time.perf_counter() - started
    started = time.perf_counter()
    baseline_predictions = baseline.predict(validation_df)
    baseline_validation_seconds = time.perf_counter() - started
    rows = [
        {
            "model": "Majority-class baseline",
            **_metrics(y_validation, baseline_predictions, LABELS),
            "fit_seconds": baseline_fit_seconds,
            "validation_predict_seconds": baseline_validation_seconds,
            "selected": False,
        }
    ]

    candidate_factories = [
        (
            "Logistic Regression",
            lambda: Pipeline(
                steps=[
                    ("preprocessor", _make_preprocessor(scale_numeric=True)),
                    (
                        "classifier",
                        LogisticRegression(
                            max_iter=1000,
                            class_weight="balanced",
                            random_state=RANDOM_STATE,
                        ),
                    ),
                ]
            ),
        ),
        (
            "Decision Tree",
            lambda: Pipeline(
                steps=[
                    ("preprocessor", _make_preprocessor(scale_numeric=False)),
                    (
                        "classifier",
                        DecisionTreeClassifier(
                            max_depth=12,
                            min_samples_leaf=5,
                            class_weight="balanced",
                            random_state=RANDOM_STATE,
                        ),
                    ),
                ]
            ),
        ),
        (
            "Random Forest",
            lambda: Pipeline(
                steps=[
                    ("preprocessor", _make_preprocessor(scale_numeric=False)),
                    (
                        "classifier",
                        RandomForestClassifier(
                            n_estimators=100,
                            max_depth=12,
                            min_samples_leaf=3,
                            class_weight="balanced_subsample",
                            random_state=RANDOM_STATE,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
        ),
    ]

    pipelines = {}
    for name, factory in candidate_factories:
        pipeline = factory()
        started = time.perf_counter()
        pipeline.fit(train_df, y_train)
        fit_seconds = time.perf_counter() - started
        started = time.perf_counter()
        predictions = pipeline.predict(validation_df)
        predict_seconds = time.perf_counter() - started
        pipelines[name] = pipeline
        rows.append(
            {
                "model": name,
                **_metrics(y_validation, predictions, LABELS),
                "fit_seconds": fit_seconds,
                "validation_predict_seconds": predict_seconds,
                "selected": False,
            }
        )

    candidate_rows = rows[1:]
    selected_row = max(candidate_rows, key=lambda row: row["macro_f1"])
    selected_row["selected"] = True
    selected_name = selected_row["model"]
    selected_pipeline = pipelines[selected_name]
    baseline_class = str(y_train.value_counts().idxmax())

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_pipeline, MODEL_PATH)

    comparison = pd.DataFrame(rows)
    comparison.to_csv(COMPARISON_PATH, index=False)
    audit["random_state"] = RANDOM_STATE
    audit["selected_by"] = "highest 2024 validation macro-F1; no 2025 data used"
    _json_write(AUDIT_PATH, audit)

    metadata = {
        "selected_model": selected_name,
        "selected_validation_metrics": {
            key: float(selected_row[key])
            for key in [
                "accuracy",
                "macro_precision",
                "macro_recall",
                "macro_f1",
                "weighted_precision",
                "weighted_recall",
                "weighted_f1",
            ]
        },
        "selected_training_seconds": float(selected_row["fit_seconds"]),
        "selected_validation_predict_seconds": float(
            selected_row["validation_predict_seconds"]
        ),
        "baseline_class": baseline_class,
        "baseline_validation_metrics": {
            key: float(rows[0][key])
            for key in [
                "accuracy",
                "macro_precision",
                "macro_recall",
                "macro_f1",
                "weighted_precision",
                "weighted_recall",
                "weighted_f1",
            ]
        },
        "feature_columns": FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "target_column": TARGET_COLUMN,
        "date_column": DATE_COLUMN,
        "class_labels": LABELS,
        "train_period": audit["train_period"],
        "validation_period": audit["validation_period"],
        "test_period": audit["test_period"],
        "train_rows": audit["rows_in_train_period"],
        "validation_rows": audit["rows_in_validation_period"],
        "test_rows": audit["rows_in_test_period"],
        "train_class_distribution": audit["train_class_distribution"],
        "validation_class_distribution": audit["validation_class_distribution"],
        "invalid_date_or_label_rows": audit[
            "rows_excluded_for_invalid_date_or_label"
        ],
        "out_of_period_rows": audit["rows_excluded_outside_requested_periods"],
        "random_state": RANDOM_STATE,
        "preprocessing_fit_rows": audit["rows_in_train_period"],
        "preprocessing_fit_period": audit["train_period"],
        "scikit_learn_version": sklearn.__version__,
        "dataset_path": str(DATA_PATH),
    }
    _json_write(METADATA_PATH, metadata)

    table_rows = [
        [
            row["model"],
            f"{row['accuracy']:.4f}",
            f"{row['macro_precision']:.4f}",
            f"{row['macro_recall']:.4f}",
            f"{row['macro_f1']:.4f}",
            f"{row['weighted_f1']:.4f}",
            f"{row['fit_seconds']:.3f}",
            "yes" if row["selected"] else "no",
        ]
        for row in rows
    ]
    report = f"""# RoadSafe severity model training and validation

## Dataset and split

- Dataset: `{DATA_PATH}` ({audit['dataset_rows']} rows, {audit['dataset_columns']} columns).
- Valid target-class distribution across the source file: `{json.dumps(audit['target_class_distribution_all_valid_labels'], sort_keys=True)}`.
- Data quality check: {sum(audit['dataset_missing_values_by_column'].values())} missing cells across all columns; {audit['dataset_duplicate_rows']} duplicate rows. Accident IDs are not part of this selected schema, so duplicate IDs cannot be checked here.
- Date column: `{DATE_COLUMN}`; parsed with `{audit['date_parse_method']}`. Parse failures: {audit['date_parse_failures']}.
- Target: `{TARGET_COLUMN}`; accepted labels: {', '.join(LABELS)}.
- Train: {audit['train_period']} ({audit['rows_in_train_period']} rows).
- Validation: {audit['validation_period']} ({audit['rows_in_validation_period']} rows).
- Reserved test: {audit['test_period']} ({audit['rows_in_test_period']} eligible rows); those rows are not used for fitting, preprocessing, validation scoring, or selection. Date and label validity are audited across the source file.
- Invalid date or label rows excluded: {audit['rows_excluded_for_invalid_date_or_label']} (date-only {audit['invalid_date_only_rows']}, label-only {audit['invalid_label_only_rows']}, both {audit['invalid_date_and_label_rows']}).
- Valid rows outside the requested periods excluded: {audit['rows_excluded_outside_requested_periods']}.
- Preprocessing is inside each pipeline and is fitted by `Pipeline.fit` on 2022-2023 rows only. Validation and holdout data are not used to fit preprocessing.

### Class distribution

- Train: `{json.dumps(audit['train_class_distribution'], sort_keys=True)}`
- Validation: `{json.dumps(audit['validation_class_distribution'], sort_keys=True)}`

## Features

Used features: {', '.join(f'`{feature}`' for feature in FEATURES)}.

Excluded fields: `accident_severity` is the target; `cause` and `casualties` describe the accident outcome and are deliberately excluded; `city` and coordinates are excluded to avoid geographic memorization; `date` is used only to create the chronological splits. The model classifies severity among recorded accidents and does not estimate whether an accident will occur.

## 2024 validation comparison

Models were selected using validation macro-F1. The 2025 holdout was not used for model selection.

{_markdown_table(['Model', 'Accuracy', 'Macro-P', 'Macro-R', 'Macro-F1', 'Weighted-F1', 'Fit sec', 'Selected'], table_rows)}

Selected model: **{selected_name}**. Its fitted preprocessing pipeline is saved at `{MODEL_PATH}`. The majority baseline predicts `{baseline_class}` from the training class distribution.

## Outputs

- `{MODEL_PATH}`: selected fitted pipeline.
- `{METADATA_PATH}`: model, split, feature, and validation metadata.
- `{COMPARISON_PATH}`: validation comparison table.
- `{AUDIT_PATH}`: data and exclusion audit.

Validation scores describe this dataset only. Dataset provenance is not documented in the repository, and these metrics do not establish real-world predictive accuracy.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"Dataset: {DATA_PATH}")
    print(f"Rows: {audit['dataset_rows']}; columns: {audit['dataset_columns']}")
    print(f"Date column: {DATE_COLUMN}; parse failures: {audit['date_parse_failures']}")
    print(f"Invalid date/label exclusions: {audit['rows_excluded_for_invalid_date_or_label']}")
    print(f"Out-of-period exclusions: {audit['rows_excluded_outside_requested_periods']}")
    print(f"Selected by 2024 validation macro-F1: {selected_name}")
    print(f"Saved pipeline: {MODEL_PATH}")
    print(f"Training report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
