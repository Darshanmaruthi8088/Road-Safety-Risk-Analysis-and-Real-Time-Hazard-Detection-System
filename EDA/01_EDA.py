"""Run the complete exploratory analysis supported by the selected dataset.

Run from any directory with:
    python EDA/01_EDA.py

Charts, summary tables, and a Markdown report are saved in
EDA/selected_eda_outputs. The source CSV is never modified.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "Data" / "indian_roads_project_selected.csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "selected_eda_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEVERITY_ORDER = ["minor", "major", "fatal"]
SEVERITY_COLORS = ["#4c9f70", "#e9a23b", "#c94c4c"]
TIME_PERIOD_ORDER = ["Night", "Morning", "Afternoon", "Evening"]
REQUIRED_COLUMNS = [
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


def save_figure(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=170, bbox_inches="tight")
    plt.close(fig)


def save_table(table: pd.DataFrame | pd.Series, filename: str) -> None:
    if isinstance(table, pd.Series):
        table = table.to_frame()
    table.to_csv(OUTPUT_DIR / filename, index=True)


def severity_share(data: pd.DataFrame, group_column: str) -> pd.DataFrame:
    table = pd.crosstab(
        data[group_column],
        data["accident_severity"],
        normalize="index",
    )
    return table.reindex(columns=SEVERITY_ORDER, fill_value=0).mul(100)


def plot_severity_share(table: pd.DataFrame, title: str, filename: str, rotation: int = 0) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    table.plot(kind="bar", stacked=True, color=SEVERITY_COLORS, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("Records within group (%)")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=rotation)
    ax.legend(title="Severity", loc="upper right")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    save_figure(fig, filename)


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Selected dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Selected dataset is missing required columns: {missing_columns}")

    df = df[REQUIRED_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise")
    for column in ["city"]:
        df[column] = df[column].astype("string").str.strip()
    for column in ["road_type", "weather", "traffic_density", "cause", "accident_severity"]:
        df[column] = df[column].astype("string").str.strip().str.lower()
    for column in ["latitude", "longitude", "hour", "casualties"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["time_period"] = pd.cut(
        df["hour"],
        bins=[-1, 5, 11, 17, 23],
        labels=TIME_PERIOD_ORDER,
        include_lowest=True,
    )

    row_count = len(df)
    severity_counts = (
        df["accident_severity"]
        .value_counts()
        .reindex(SEVERITY_ORDER, fill_value=0)
        .rename("records")
    )
    severity_summary = pd.DataFrame({
        "records": severity_counts,
        "percent": (severity_counts / row_count * 100).round(2),
    })
    save_table(severity_summary, "severity_distribution.csv")

    # 1. Severity distribution.
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(SEVERITY_ORDER, severity_counts.values, color=SEVERITY_COLORS)
    ax.set_title("Accident Records by Severity")
    ax.set_xlabel("Severity")
    ax.set_ylabel("Records")
    ax.bar_label(bars, labels=[f"{value:,}" for value in severity_counts.values], padding=3)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    save_figure(fig, "01_severity_distribution.png")

    # 2. Annual and monthly accident-record trends.
    yearly = df.groupby("year").size().rename("records")
    monthly = df.groupby("month").size().rename("records")
    save_table(yearly, "records_by_year.csv")
    save_table(monthly, "records_by_month.csv")
    fig, axes = plt.subplots(2, 1, figsize=(11, 8))
    yearly.plot(kind="bar", ax=axes[0], color="#3273a8")
    axes[0].set_title("Accident Records by Year (2025 is partial)")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Records")
    axes[0].tick_params(axis="x", rotation=0)
    monthly.plot(ax=axes[1], marker="o", color="#c65b52")
    axes[1].set_title("Accident Records by Month (2025 through April 15)")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Records")
    axes[1].tick_params(axis="x", rotation=60)
    axes[1].grid(alpha=0.2)
    save_figure(fig, "02_accidents_over_time.png")

    # 3. City counts and city severity proportions.
    city_counts = df["city"].value_counts().sort_values(ascending=False).rename("records")
    save_table(city_counts, "records_by_city.csv")
    city_order = city_counts.index.tolist()
    fig, ax = plt.subplots(figsize=(9, 6))
    city_counts.sort_values().plot(kind="barh", ax=ax, color="#3273a8")
    ax.set_title("Accident Records by City")
    ax.set_xlabel("Records")
    ax.set_ylabel("City")
    ax.grid(axis="x", alpha=0.2)
    save_figure(fig, "03_records_by_city.png")
    city_severity = severity_share(df, "city").reindex(city_order)
    save_table(city_severity.round(2), "severity_percentage_by_city.csv")
    plot_severity_share(city_severity, "Severity Distribution by City", "04_severity_by_city.png", 25)

    # 4. Causes and severity by cause.
    cause_counts = df["cause"].value_counts().sort_values(ascending=False).rename("records")
    save_table(cause_counts, "records_by_cause.csv")
    fig, ax = plt.subplots(figsize=(9, 5))
    cause_counts.sort_values().plot(kind="barh", ax=ax, color="#3273a8")
    ax.set_title("Accident Records by Reported Cause")
    ax.set_xlabel("Records")
    ax.set_ylabel("Cause")
    save_figure(fig, "05_records_by_cause.png")
    cause_severity = severity_share(df, "cause")
    save_table(cause_severity.round(2), "severity_percentage_by_cause.csv")
    plot_severity_share(cause_severity, "Severity Distribution by Reported Cause", "06_severity_by_cause.png", 15)

    # 5. Road, weather, and traffic conditions versus severity.
    for index, column, label in [
        (7, "road_type", "Road Type"),
        (8, "weather", "Weather"),
        (9, "traffic_density", "Traffic Density"),
    ]:
        table = severity_share(df, column)
        save_table(table.round(2), f"severity_percentage_by_{column}.csv")
        plot_severity_share(table, f"Severity Distribution by {label}", f"{index:02d}_severity_by_{column}.png")

    # 6. Time-of-day and hourly patterns.
    period_severity = severity_share(df.dropna(subset=["time_period"]), "time_period")
    period_severity = period_severity.reindex(TIME_PERIOD_ORDER)
    save_table(period_severity.round(2), "severity_percentage_by_time_period.csv")
    plot_severity_share(period_severity, "Severity Distribution by Time of Day", "10_severity_by_time_period.png")
    hourly_counts = df["hour"].value_counts().reindex(range(24), fill_value=0).sort_index().rename("records")
    save_table(hourly_counts, "records_by_hour.csv")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(hourly_counts.index, hourly_counts.values, marker="o", color="#3273a8")
    ax.set_title("Accident Records by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Records")
    ax.set_xticks(range(24))
    ax.grid(alpha=0.25)
    save_figure(fig, "11_records_by_hour.png")

    # 7. Casualty summaries by the recorded severity label.
    casualty_summary = (
        df.groupby("accident_severity")["casualties"]
        .agg(records="size", total_casualties="sum", mean="mean", median="median", maximum="max")
        .reindex(SEVERITY_ORDER)
    )
    save_table(casualty_summary.round(2), "casualties_by_severity.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    casualty_data = [df.loc[df["accident_severity"] == label, "casualties"] for label in SEVERITY_ORDER]
    ax.boxplot(casualty_data, tick_labels=SEVERITY_ORDER, showfliers=False)
    ax.set_title("Casualties per Record by Severity")
    ax.set_xlabel("Recorded Severity")
    ax.set_ylabel("Casualties")
    ax.grid(axis="y", alpha=0.2)
    save_figure(fig, "12_casualties_by_severity.png")

    # 8. Geographic distribution and coordinate-grid hotspots.
    fig, ax = plt.subplots(figsize=(9, 7))
    for label, color in zip(SEVERITY_ORDER, SEVERITY_COLORS):
        part = df[df["accident_severity"] == label]
        ax.scatter(part["longitude"], part["latitude"], s=9, alpha=0.35, label=label, color=color)
    ax.set_title("Accident Locations by Recorded Severity")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(title="Severity", frameon=False)
    ax.grid(alpha=0.15)
    save_figure(fig, "13_geographic_distribution.png")

    severity_weight = {"minor": 1, "major": 2, "fatal": 3}
    grid = df.copy()
    grid["latitude_grid"] = grid["latitude"].round(1)
    grid["longitude_grid"] = grid["longitude"].round(1)
    grid["severity_weight"] = grid["accident_severity"].map(severity_weight)
    hotspot_summary = (
        grid.groupby(["latitude_grid", "longitude_grid"])
        .agg(
            accident_count=("accident_severity", "size"),
            fatal_count=("accident_severity", lambda values: int((values == "fatal").sum())),
            total_casualties=("casualties", "sum"),
            severity_weighted_total=("severity_weight", "sum"),
        )
        .reset_index()
        .sort_values(["accident_count", "severity_weighted_total"], ascending=False)
    )
    save_table(hotspot_summary, "hotspot_grid_summary.csv")
    top_hotspots = hotspot_summary.head(15).copy()
    save_table(top_hotspots, "top_15_hotspots.csv")
    fig, ax = plt.subplots(figsize=(10, 7))
    hotspot_labels = [
        f"({row.latitude_grid:.1f}, {row.longitude_grid:.1f})"
        for row in top_hotspots.itertuples(index=False)
    ]
    counts_for_plot = top_hotspots["accident_count"].iloc[::-1]
    labels_for_plot = hotspot_labels[::-1]
    bars = ax.barh(labels_for_plot, counts_for_plot, color="#c65b52")
    ax.bar_label(bars, labels=[f"{int(value):,}" for value in counts_for_plot], padding=4)
    ax.set_title("Top 15 Approximate Hotspot Cells by Record Count")
    ax.set_xlabel("Records in 0.1-degree coordinate cell")
    ax.set_ylabel("Rounded latitude, longitude")
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    save_figure(fig, "14_top_geographic_hotspots.png")

    # Write a concise, reproducible narrative summary.
    top_city = city_counts.index[0]
    top_cause = cause_counts.index[0]
    casualty_total = int(df["casualties"].sum())
    severity_markdown = "\n".join(
        [
            "| Severity | Records | Percent |",
            "|---|---:|---:|",
            *[
                f"| {label} | {int(severity_summary.loc[label, 'records']):,} | {severity_summary.loc[label, 'percent']:.2f}% |"
                for label in SEVERITY_ORDER
            ],
        ]
    )
    report = [
        "# Exploratory analysis: selected RoadSafe dataset",
        "",
        f"- Records analyzed: {row_count:,}",
        f"- Selected columns: {len(REQUIRED_COLUMNS)}",
        f"- Date range: {df['date'].min().date()} to {df['date'].max().date()}",
        f"- Cities represented: {df['city'].nunique()}",
        f"- Total recorded casualties: {casualty_total:,}",
        f"- Most represented city by record count: {top_city} ({int(city_counts.iloc[0]):,})",
        f"- Most common reported cause: {top_cause} ({int(cause_counts.iloc[0]):,})",
        "",
        "## Severity distribution",
        "",
        severity_markdown,
        "",
        "## Analyses produced",
        "",
        "- Severity counts and percentages.",
        "- Annual and monthly record counts.",
        "- City counts and severity percentages by city.",
        "- Reported causes and severity percentages by cause.",
        "- Severity percentages by road type, weather, and traffic density.",
        "- Severity by time-of-day period and record counts by hour.",
        "- Casualty summaries by recorded severity.",
        "- Geographic distribution and approximate coordinate-grid hotspot summaries.",
        "",
        "## Interpretation notes",
        "",
        "These charts describe records in the supplied dataset. They do not establish that a factor caused an accident.",
        "City counts are not exposure-adjusted risk rates; population, road length, and traffic volume are not included.",
        "The dataset ends on April 15, 2025, so 2025 annual and monthly counts are partial and should not be compared directly with full years.",
        "Hotspot cells are approximate 0.1-degree coordinate groups. The source-level risk_score field is not in this selected dataset; hotspot summaries use observed counts, casualties, and severity weights instead.",
        "",
        "## Output files",
        "",
        *[f"- `{path.name}`" for path in sorted(OUTPUT_DIR.glob("*.png"))],
        *[f"- `{path.name}`" for path in sorted(OUTPUT_DIR.glob("*.csv"))],
    ]
    (OUTPUT_DIR / "EDA_summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Analyzed {row_count:,} rows across {len(REQUIRED_COLUMNS)} selected columns.")
    print("Severity distribution:")
    print(severity_summary.to_string())
    print(f"\nEDA charts, summary tables, and report saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
