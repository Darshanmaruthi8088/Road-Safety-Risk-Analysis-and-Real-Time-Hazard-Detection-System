"""Create a clear before/after view of the changes made during cleaning.

Run from any directory with:
    python EDA/02_cleaning_impact_comparison.py

The chart compares the checked-in raw and cleaned CSV files and is saved next
to this script as ``cleaning_impact_comparison.png``.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "Data"
OUTPUT_PATH = Path(__file__).resolve().parent / "cleaning_impact_comparison.png"

roads_before = pd.read_csv(DATA_DIR / "indian_roads_dataset.csv")
roads_after = pd.read_csv(DATA_DIR / "indian_roads_cleaned.csv")
prediction_before = pd.read_csv(DATA_DIR / "accident_prediction_india.csv")
prediction_after = pd.read_csv(
    DATA_DIR / "accident_prediction_india_cleaned.csv"
)

BEFORE_COLOR = "#3979a8"
AFTER_COLOR = "#e58b36"


def _as_categories(series: pd.Series, missing_label: str) -> pd.Series:
    """Keep missing values visible as a chart category, including blank text."""
    values = series.astype("string").str.strip()
    values = values.mask(values.eq(""), pd.NA)
    return values.fillna(missing_label).astype(str)


def _plot_category_comparison(ax, before, after, column, title, before_missing):
    before_counts = _as_categories(before[column], before_missing).value_counts()
    after_counts = _as_categories(after[column], "(Missing)").value_counts()
    categories = sorted(set(before_counts.index) | set(after_counts.index))

    y = np.arange(len(categories))
    height = 0.36
    before_values = [int(before_counts.get(category, 0)) for category in categories]
    after_values = [int(after_counts.get(category, 0)) for category in categories]

    ax.barh(y - height / 2, before_values, height, color=BEFORE_COLOR, label="Before")
    ax.barh(y + height / 2, after_values, height, color=AFTER_COLOR, label="After")
    ax.set_yticks(y, categories)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel("Records")
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)


missing_columns = [
    ("Indian Roads\nFestival", roads_before, roads_after, "festival"),
    (
        "Accident Prediction\nTraffic Control Presence",
        prediction_before,
        prediction_after,
        "Traffic Control Presence",
    ),
    (
        "Accident Prediction\nDriver License Status",
        prediction_before,
        prediction_after,
        "Driver License Status",
    ),
]
missing_before = [int(before[column].isna().sum()) for _, before, _, column in missing_columns]
missing_after = [int(after[column].isna().sum()) for _, _, after, column in missing_columns]
labels = [label for label, _, _, _ in missing_columns]

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle(
    "What changed after data cleaning?",
    fontsize=18,
    fontweight="bold",
    y=0.98,
)
fig.text(
    0.5,
    0.94,
    "Rows were retained; cleaning filled missing categories and standardized fields.",
    ha="center",
    fontsize=11,
    color="#444444",
)

ax = axes[0, 0]
x = np.arange(len(labels))
width = 0.36
ax.bar(x - width / 2, missing_before, width, color=BEFORE_COLOR, label="Before cleaning")
ax.bar(x + width / 2, missing_after, width, color=AFTER_COLOR, label="After cleaning")
ax.set_xticks(x, labels)
ax.set_ylabel("Missing cells")
ax.set_title("Missing values in fields that were cleaned")
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)
ax.legend(frameon=False)
for positions, values in ((x - width / 2, missing_before), (x + width / 2, missing_after)):
    for position, value in zip(positions, values):
        ax.annotate(
            f"{value:,}",
            (position, value),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )

_plot_category_comparison(
    axes[0, 1],
    roads_before,
    roads_after,
    "festival",
    "Indian Roads: festival values",
    "(Missing)",
)
_plot_category_comparison(
    axes[1, 0],
    prediction_before,
    prediction_after,
    "Traffic Control Presence",
    "Accident Prediction: traffic control",
    "(Missing)",
)
_plot_category_comparison(
    axes[1, 1],
    prediction_before,
    prediction_after,
    "Driver License Status",
    "Accident Prediction: license status",
    "(Missing)",
)

handles, legend_labels = axes[0, 1].get_legend_handles_labels()
fig.legend(
    handles,
    legend_labels,
    loc="lower center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.5, 0.005),
)
fig.tight_layout(rect=(0.02, 0.04, 0.98, 0.91))
fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight")
plt.close(fig)

print("CLEANING IMPACT SUMMARY")
for name, before, after in [
    ("Indian Roads", roads_before, roads_after),
    ("Accident Prediction", prediction_before, prediction_after),
]:
    print(
        f"{name}: {len(before):,} -> {len(after):,} rows; "
        f"{int(before.isna().sum().sum()):,} -> "
        f"{int(after.isna().sum().sum()):,} missing cells"
    )
print(f"Comparison chart saved to: {OUTPUT_PATH}")
