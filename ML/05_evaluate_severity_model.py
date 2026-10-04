"""Evaluate the saved severity pipeline once on the Jan-Apr 2025 holdout."""

from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "Data" / "indian_roads_cleaned.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "model_artifacts"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
MODEL_PATH = ARTIFACT_DIR / "severity_pipeline.joblib"
METADATA_PATH = ARTIFACT_DIR / "severity_model_metadata.json"
METRICS_PATH = REPORT_DIR / "test_evaluation_metrics.json"
CLASSIFICATION_PATH = REPORT_DIR / "test_classification_report.csv"
PIPELINE_CONFUSION_PATH = REPORT_DIR / "test_confusion_matrix_selected_model.csv"
BASELINE_CONFUSION_PATH = REPORT_DIR / "test_confusion_matrix_baseline.csv"
REPORT_PATH = REPORT_DIR / "evaluation_report.md"

DATE_COLUMN = "date"
TARGET_COLUMN = "accident_severity"
LABELS = ["minor", "major", "fatal"]
CATEGORICAL_FEATURES = [
    "road_type",
    "weather",
    "visibility",
    "traffic_density",
    "festival",
]
NUMERIC_FEATURES = [
    "lanes",
    "traffic_signal",
    "temperature",
    "hour",
    "is_weekend",
    "is_peak_hour",
]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TEST_START = pd.Timestamp("2025-01-01")
TEST_END_EXCLUSIVE = pd.Timestamp("2025-05-01")


def _json_write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _metrics(y_true: pd.Series, y_pred) -> dict[str, float]:
    result = {"accuracy": float(accuracy_score(y_true, y_pred))}
    for average in ("macro", "weighted"):
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=LABELS,
            average=average,
            zero_division=0,
        )
        result[f"{average}_precision"] = float(precision)
        result[f"{average}_recall"] = float(recall)
        result[f"{average}_f1"] = float(f1)
    return result


def _class_distribution(labels: pd.Series) -> dict[str, int]:
    return {label: int((labels == label).sum()) for label in LABELS}


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    rendered = [[str(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in rendered:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    header_line = "| " + " | ".join(
        value.ljust(widths[index]) for index, value in enumerate(headers)
    ) + " |"
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    body = [
        "| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(row)) + " |"
        for row in rendered
    ]
    return "\n".join([header_line, separator, *body])


def _classification_rows(model_name: str, y_true: pd.Series, y_pred) -> list[dict]:
    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )
    return [
        {
            "model": model_name,
            "class_or_average": label,
            "precision": float(report[label]["precision"]),
            "recall": float(report[label]["recall"]),
            "f1_score": float(report[label]["f1-score"]),
            "support": int(report[label]["support"]),
        }
        for label in [*LABELS, "macro avg", "weighted avg"]
    ] + [
        {
            "model": model_name,
            "class_or_average": "accuracy",
            "precision": None,
            "recall": None,
            "f1_score": float(report["accuracy"]),
            "support": int(report["macro avg"]["support"]),
        }
    ]


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")
    if not MODEL_PATH.is_file() or not METADATA_PATH.is_file():
        raise FileNotFoundError(
            "Run ML/04_train_severity_model.py before evaluating the model."
        )

    df = pd.read_csv(DATA_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    required = [DATE_COLUMN, TARGET_COLUMN, *FEATURES]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(
            "Required date, target, or feature columns are missing: "
            + ", ".join(missing)
        )
    if metadata.get("feature_columns") != FEATURES:
        raise ValueError("Saved model feature schema does not match this evaluator.")
    if metadata.get("target_column") != TARGET_COLUMN:
        raise ValueError("Saved model target does not match this evaluator.")

    parsed_dates = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    normalized_labels = df[TARGET_COLUMN].astype("string").str.strip().str.lower()
    valid_label = normalized_labels.isin(LABELS).fillna(False)
    valid_date = parsed_dates.notna()
    invalid_date = ~valid_date
    invalid_label = ~valid_label
    invalid_union = invalid_date | invalid_label
    test_mask = (
        valid_date
        & valid_label
        & (parsed_dates >= TEST_START)
        & (parsed_dates < TEST_END_EXCLUSIVE)
    )
    outside_period = valid_date & valid_label & ~test_mask

    test_df = df.loc[test_mask, FEATURES].copy()
    y_test = normalized_labels.loc[test_mask].astype(str)
    if test_df.empty:
        raise ValueError("The requested Jan-Apr 2025 test holdout is empty.")
    for column in NUMERIC_FEATURES:
        test_df[column] = pd.to_numeric(test_df[column], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        test_df[column] = test_df[column].astype("string")

    expected_test_rows = metadata.get("test_rows")
    if expected_test_rows != len(test_df):
        raise ValueError(
            "The holdout row count differs from training metadata; "
            "the source dataset may have changed since training."
        )

    pipeline = joblib.load(MODEL_PATH)
    started = time.perf_counter()
    predictions = pipeline.predict(test_df)
    pipeline_evaluation_seconds = time.perf_counter() - started

    baseline_class = metadata["baseline_class"]
    started = time.perf_counter()
    baseline_predictions = [baseline_class] * len(y_test)
    baseline_evaluation_seconds = time.perf_counter() - started

    pipeline_metrics = _metrics(y_test, predictions)
    baseline_metrics = _metrics(y_test, baseline_predictions)
    pipeline_matrix = confusion_matrix(y_test, predictions, labels=LABELS)
    baseline_matrix = confusion_matrix(y_test, baseline_predictions, labels=LABELS)
    pipeline_report = _classification_rows(
        metadata["selected_model"], y_test, predictions
    )
    baseline_report = _classification_rows(
        "Majority-class baseline", y_test, baseline_predictions
    )
    all_target_counts = {
        label: int((normalized_labels[valid_label] == label).sum())
        for label in LABELS
    }
    missing_values_by_column = {
        column: int(df[column].isna().sum()) for column in df.columns
    }
    duplicate_rows = int(df.duplicated().sum())
    duplicate_accident_ids = (
        int(df["accident_id"].duplicated().sum())
        if "accident_id" in df.columns
        else None
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pipeline_confusion_df = pd.DataFrame(
        pipeline_matrix,
        index=pd.Index(LABELS, name="actual"),
        columns=pd.Index(LABELS, name="predicted"),
    )
    baseline_confusion_df = pd.DataFrame(
        baseline_matrix,
        index=pd.Index(LABELS, name="actual"),
        columns=pd.Index(LABELS, name="predicted"),
    )
    classification_df = pd.DataFrame(pipeline_report + baseline_report)
    pipeline_confusion_df.to_csv(PIPELINE_CONFUSION_PATH)
    baseline_confusion_df.to_csv(BASELINE_CONFUSION_PATH)
    classification_df.to_csv(CLASSIFICATION_PATH, index=False)

    results = {
        "dataset_path": str(DATA_PATH),
        "dataset_rows": int(len(df)),
        "dataset_columns": int(len(df.columns)),
        "dataset_target_class_distribution": all_target_counts,
        "dataset_missing_values_by_column": missing_values_by_column,
        "dataset_missing_value_count": int(sum(missing_values_by_column.values())),
        "dataset_duplicate_rows": duplicate_rows,
        "dataset_duplicate_accident_ids": duplicate_accident_ids,
        "test_period": "2025-01-01 through 2025-04-30",
        "date_column": DATE_COLUMN,
        "date_parse_method": "pandas.to_datetime(errors='coerce')",
        "date_parse_failures": int(invalid_date.sum()),
        "invalid_label_rows": int(invalid_label.sum()),
        "invalid_date_only_rows": int((invalid_date & ~invalid_label).sum()),
        "invalid_label_only_rows": int((invalid_label & ~invalid_date).sum()),
        "invalid_date_and_label_rows": int((invalid_date & invalid_label).sum()),
        "rows_excluded_for_invalid_date_or_label": int(invalid_union.sum()),
        "valid_rows_outside_test_period": int(outside_period.sum()),
        "test_rows": int(len(test_df)),
        "test_class_distribution": _class_distribution(y_test),
        "selected_model": metadata["selected_model"],
        "selected_model_validation_macro_f1": metadata[
            "selected_validation_metrics"
        ]["macro_f1"],
        "baseline_class": baseline_class,
        "selected_model_test_metrics": pipeline_metrics,
        "baseline_test_metrics": baseline_metrics,
        "selected_model_test_evaluation_seconds": float(
            pipeline_evaluation_seconds
        ),
        "baseline_test_evaluation_seconds": float(baseline_evaluation_seconds),
        "pipeline_saved_at": str(MODEL_PATH),
        "scikit_learn_version": sklearn.__version__,
        "preprocessing_fit_period": metadata["preprocessing_fit_period"],
        "preprocessing_fit_rows": metadata["preprocessing_fit_rows"],
    }
    _json_write(METRICS_PATH, results)

    metric_rows = []
    for name, values in [
        (metadata["selected_model"], pipeline_metrics),
        ("Majority-class baseline", baseline_metrics),
    ]:
        metric_rows.append(
            [
                name,
                f"{values['accuracy']:.4f}",
                f"{values['macro_precision']:.4f}",
                f"{values['macro_recall']:.4f}",
                f"{values['macro_f1']:.4f}",
                f"{values['weighted_precision']:.4f}",
                f"{values['weighted_recall']:.4f}",
                f"{values['weighted_f1']:.4f}",
            ]
        )
    comparison_table = _markdown_table(
        [
            "Model",
            "Accuracy",
            "Macro-P",
            "Macro-R",
            "Macro-F1",
            "Weighted-P",
            "Weighted-R",
            "Weighted-F1",
        ],
        metric_rows,
    )
    class_rows = []
    for row in pipeline_report + baseline_report:
        class_rows.append(
            [
                row["model"],
                row["class_or_average"],
                "" if row["precision"] is None else f"{row['precision']:.4f}",
                "" if row["recall"] is None else f"{row['recall']:.4f}",
                f"{row['f1_score']:.4f}",
                row["support"],
            ]
        )
    class_table = _markdown_table(
        ["Model", "Class / average", "Precision", "Recall", "F1", "Support"],
        class_rows,
    )
    pipeline_confusion_table = _markdown_table(
        ["Actual \\ Predicted", *LABELS],
        [[label, *pipeline_confusion_df.loc[label].astype(int).tolist()] for label in LABELS],
    )
    baseline_confusion_table = _markdown_table(
        ["Actual \\ Predicted", *LABELS],
        [[label, *baseline_confusion_df.loc[label].astype(int).tolist()] for label in LABELS],
    )

    report = f"""# RoadSafe severity model holdout evaluation

## Evaluation design

- Dataset: {len(df)} rows by {len(df.columns)} columns. Valid target-class distribution across the source file: `{json.dumps(all_target_counts, sort_keys=True)}`.
- Data quality check: {sum(missing_values_by_column.values())} missing cells, {duplicate_rows} duplicate rows, and {duplicate_accident_ids} duplicate accident IDs.
- Selected model: **{metadata['selected_model']}**, chosen using 2024 validation macro-F1 ({metadata['selected_validation_metrics']['macro_f1']:.4f}).
- Holdout: {results['test_period']} ({results['test_rows']} rows), evaluated once after model selection.
- Training and preprocessing fit period: {metadata['preprocessing_fit_period']} ({metadata['preprocessing_fit_rows']} rows). The saved pipeline is loaded and used for prediction; this script does not fit or tune it.
- Date column: `{DATE_COLUMN}` parsed with `{results['date_parse_method']}`. Invalid dates: {results['date_parse_failures']}; invalid labels: {results['invalid_label_rows']}; rows excluded for either: {results['rows_excluded_for_invalid_date_or_label']}.
- Valid rows outside the holdout period: {results['valid_rows_outside_test_period']}; they were not used for this evaluation.
- Test class distribution: `{json.dumps(results['test_class_distribution'], sort_keys=True)}`.

## Test metrics

{comparison_table}

### Per-class metrics

{class_table}

### Confusion matrix: selected model

Rows are actual classes and columns are predicted classes.

{pipeline_confusion_table}

### Confusion matrix: majority baseline

{baseline_confusion_table}

Evaluation elapsed time: selected pipeline {pipeline_evaluation_seconds:.6f} seconds; baseline prediction {baseline_evaluation_seconds:.6f} seconds. Fit and validation time for every candidate is recorded in `validation_model_comparison.csv`.

## Interpretation and limitations

These metrics describe a held-out slice of the supplied CSV only. The repository does not document the dataset's source or establish that its rows are verified real-world accident observations. The model predicts severity conditional on an accident record; it does not predict whether an accident will happen or detect accidents in real time. The Jan-Apr 2025 holdout is relatively short and cannot establish performance in other years, locations, or operating conditions.

The classes are imbalanced, with minor accidents making up the largest share. The majority baseline has higher accuracy than the selected model, while the selected model has higher macro-F1; accuracy alone therefore hides weak performance on major and fatal cases. Test fatal-class recall is especially low, so this model should not be used as an operational safety decision system.

## Outputs

- `{METRICS_PATH}`: aggregate metrics, split audit, and elapsed evaluation times.
- `{CLASSIFICATION_PATH}`: per-class and aggregate classification metrics.
- `{PIPELINE_CONFUSION_PATH}`: selected model confusion matrix, actual rows by predicted columns.
- `{BASELINE_CONFUSION_PATH}`: majority baseline confusion matrix, actual rows by predicted columns.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"Loaded pipeline: {MODEL_PATH}")
    print(f"Selected model: {metadata['selected_model']}")
    print(f"Test holdout: {len(test_df)} rows; invalid date/label exclusions: {int(invalid_union.sum())}")
    print(f"Test metrics: {json.dumps(pipeline_metrics, sort_keys=True)}")
    print(f"Majority baseline: {json.dumps(baseline_metrics, sort_keys=True)}")
    print(f"Evaluation report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
