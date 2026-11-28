"""Audit the selected RoadSafe dataset without changing it."""

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "Data" / "indian_roads_project_selected.csv"
REPORT_PATH = PROJECT_DIR / "Data" / "indian_roads_project_selected_quality_report.txt"

EXPECTED_COLUMNS = [
    "date",
    "city",
    "latitude",
    "longitude",
    "hour",
    "road_type",
    "weather",
    "traffic_density",
    "cause",
    "casualties",
    "accident_severity",
]
TEXT_COLUMNS = [
    "city",
    "road_type",
    "weather",
    "traffic_density",
    "cause",
    "accident_severity",
]
VALID_SEVERITIES = {"minor", "major", "fatal"}


def main() -> int:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Selected dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    checks: list[tuple[str, bool, str]] = []

    checks.append(
        (
            "Expected 11-column schema",
            list(df.columns) == EXPECTED_COLUMNS,
            f"found {len(df.columns)} columns: {list(df.columns)}",
        )
    )
    checks.append(("Dataset has records", not df.empty, f"{len(df):,} rows"))

    missing_total = int(df.isna().sum().sum())
    checks.append(("No missing cells", missing_total == 0, f"{missing_total:,} missing cells"))

    blank_cells = 0
    for column in TEXT_COLUMNS:
        if column in df:
            blank_cells += int(
                df[column].astype("string").str.strip().eq("").fillna(False).sum()
            )
    checks.append(("No blank category values", blank_cells == 0, f"{blank_cells:,} blank values"))

    duplicate_rows = int(df.duplicated().sum())
    checks.append(("No duplicate selected rows", duplicate_rows == 0, f"{duplicate_rows:,} duplicates"))

    if "date" in df:
        dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
        invalid_dates = int(dates.isna().sum())
        date_detail = (
            f"{invalid_dates:,} invalid; range {dates.min().date()} to {dates.max().date()}"
            if invalid_dates == 0 and dates.notna().any()
            else f"{invalid_dates:,} invalid dates"
        )
        checks.append(("ISO dates parse correctly", invalid_dates == 0, date_detail))

    if "hour" in df:
        hours = pd.to_numeric(df["hour"], errors="coerce")
        invalid_hours = int((hours.isna() | ~hours.between(0, 23) | (hours % 1 != 0)).sum())
        checks.append(("Hours are whole numbers from 0 to 23", invalid_hours == 0, f"{invalid_hours:,} invalid hours"))

    if {"latitude", "longitude"}.issubset(df.columns):
        latitude = pd.to_numeric(df["latitude"], errors="coerce")
        longitude = pd.to_numeric(df["longitude"], errors="coerce")
        invalid_coordinates = int(
            (
                latitude.isna()
                | longitude.isna()
                | ~latitude.between(6, 38)
                | ~longitude.between(68, 98)
            ).sum()
        )
        checks.append(("Coordinates are within the checked India bounds", invalid_coordinates == 0, f"{invalid_coordinates:,} invalid coordinate pairs"))

    if "casualties" in df:
        casualties = pd.to_numeric(df["casualties"], errors="coerce")
        invalid_casualties = int(
            (casualties.isna() | (casualties < 0) | (casualties % 1 != 0)).sum()
        )
        checks.append(("Casualties are non-negative whole numbers", invalid_casualties == 0, f"{invalid_casualties:,} invalid values"))

    if "accident_severity" in df:
        severity = df["accident_severity"].astype("string").str.strip().str.lower()
        unknown_severity = sorted(set(severity.dropna()) - VALID_SEVERITIES)
        severity_detail = "valid labels: minor, major, fatal"
        if unknown_severity:
            severity_detail = f"unexpected labels: {unknown_severity}"
        checks.append(("Severity labels are valid", not unknown_severity and severity.notna().all(), severity_detail))

    lines = [
        "RoadSafe selected dataset quality audit",
        f"File: {DATA_PATH}",
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns)}",
        "",
        "Checks:",
    ]
    for label, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        lines.append(f"{status} - {label}: {detail}")

    overall_pass = all(passed for _, passed, _ in checks)
    lines.extend(["", f"Overall: {'PASS' if overall_pass else 'FAIL'}"])
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nAudit report saved to: {REPORT_PATH}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
