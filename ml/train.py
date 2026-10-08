import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# Configuration
# ============================================================

DATA_PATH = "data/processed/employees_clean.csv"

MODEL_DIR = "ml/models"
RESULTS_DIR = "ml/results"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# Load Data
# ============================================================

print("=" * 70)
print("EMPLOYEE ATTRITION - ML MODEL TRAINING")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")


# ============================================================
# Prepare Target Variable
# ============================================================

print("\nPreparing target variable...")

# No  -> 0
# Yes -> 1

df["Attrition"] = df["Attrition"].map({
    "No": 0,
    "Yes": 1
})


# ============================================================
# Separate Features and Target
# ============================================================

X = df.drop(columns=["Attrition", "EmployeeNumber"])
y = df["Attrition"]


print(f"Features: {X.shape[1]}")
print(f"Target: Attrition")


# ============================================================
# Identify Column Types
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


print("\nCategorical features:")
print(categorical_features)

print("\nNumerical features:")
print(numerical_features)


# ============================================================
# Train/Test Split
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTrain samples:", len(X_train))
print("Test samples:", len(X_test))


# ============================================================
# Preprocessing
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            StandardScaler(),
            numerical_features
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                drop="first"
            ),
            categorical_features
        )
    ]
)


# ============================================================
# Models
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
}


# ============================================================
# Train and Evaluate Models
# ============================================================

results = []

trained_models = {}

for model_name, classifier in models.items():

    print("\n" + "=" * 70)
    print(f"TRAINING: {model_name}")
    print("=" * 70)

    pipeline = Pipeline(
        steps=[
            ("preprocessing", preprocessor),
            ("classifier", classifier)
        ]
    )

    # Train
    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred = pipeline.predict(X_test)

    # Probability of Attrition = Yes
    y_probability = pipeline.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        y_probability
    )

    print(f"\nAccuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["No Attrition", "Attrition"],
            zero_division=0
        )
    )

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC_AUC": roc_auc
    })

    trained_models[model_name] = pipeline


# ============================================================
# Compare Models
# ============================================================

results_df = pd.DataFrame(results)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# Select Best Model
# ============================================================

# We use F1 as the primary selection metric
# because the dataset is imbalanced.

best_model_name = results_df.loc[
    results_df["F1"].idxmax(),
    "Model"
]

best_model = trained_models[best_model_name]


print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)

print(f"Selected model: {best_model_name}")


# ============================================================
# Save Best Model
# ============================================================

model_path = os.path.join(
    MODEL_DIR,
    "attrition_model.pkl"
)

joblib.dump(
    best_model,
    model_path
)

print(f"\nModel saved to: {model_path}")


# ============================================================
# Save Model Comparison
# ============================================================

results_path = os.path.join(
    RESULTS_DIR,
    "model_comparison.csv"
)

results_df.to_csv(
    results_path,
    index=False
)

print(f"Model comparison saved to: {results_path}")


print("\n" + "=" * 70)
print("MODEL TRAINING COMPLETED")
print("=" * 70)