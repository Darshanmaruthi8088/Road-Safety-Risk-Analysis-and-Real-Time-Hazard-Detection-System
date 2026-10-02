import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, classification_report


df = pd.read_csv("../data/indian_roads_cleaned.csv")


features = [
    "road_type",
    "lanes",
    "traffic_signal",
    "weather",
    "visibility",
    "temperature",
    "traffic_density",
    "cause",
    "vehicles_involved",
    "hour",
    "is_weekend",
    "is_peak_hour",
    "festival"
]


target = "accident_severity"


X = df[features]
y = df[target]


categorical_features = [
    "road_type",
    "weather",
    "visibility",
    "traffic_density",
    "cause",
    "festival"
]


numeric_features = [
    "lanes",
    "traffic_signal",
    "temperature",
    "vehicles_involved",
    "hour",
    "is_weekend",
    "is_peak_hour"
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)


print("Training data shape:", X_train.shape)
print("Testing data shape:", X_test.shape)

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())


models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ),

    "Decision Tree": DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )
}


print("\n========== MODEL COMPARISON ==========")


for name, model in models.items():

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"\n{name}")
    print(f"Accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, predictions))


import matplotlib.pyplot as plt

random_forest = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

random_forest.fit(X_train, y_train)

feature_names = preprocessor.get_feature_names_out()

importance = pd.Series(
    random_forest.feature_importances_,
    index=feature_names
).sort_values(ascending=False)

print("\n========== TOP 15 FEATURE IMPORTANCES ==========")
print(importance.head(15))

plt.figure(figsize=(10, 6))
importance.head(15).sort_values().plot(kind="barh")
plt.title("Top 15 Feature Importances - Random Forest")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()

print("\n========== FEATURE VS SEVERITY ANALYSIS ==========")

print("\nAverage Temperature by Severity:")
print(df.groupby("accident_severity")["temperature"].mean())

print("\nAverage Hour by Severity:")
print(df.groupby("accident_severity")["hour"].mean())

print("\nAverage Lanes by Severity:")
print(df.groupby("accident_severity")["lanes"].mean())

print("\nAverage Vehicles Involved by Severity:")
print(df.groupby("accident_severity")["vehicles_involved"].mean())


print("\nVehicles Involved vs Severity:")
print(pd.crosstab(
    df["vehicles_involved"],
    df["accident_severity"],
    normalize="index"
).round(3))


print("\nRoad Type vs Severity:")
print(pd.crosstab(
    df["road_type"],
    df["accident_severity"],
    normalize="index"
).round(3))


print("\nWeather vs Severity:")
print(pd.crosstab(
    df["weather"],
    df["accident_severity"],
    normalize="index"
).round(3))