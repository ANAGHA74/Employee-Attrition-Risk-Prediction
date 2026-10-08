import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DATA_PATH = "data/processed/employees_clean.csv"
MODEL_PATH = "ml/models/attrition_model.pkl"
OUTPUT_PATH = "ml/results/test_predictions.csv"

RISK_THRESHOLD = 0.60

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("=" * 70)
print("MODEL EVALUATION - HELD-OUT TEST DATA")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

# Convert target to numerical values
df["Attrition"] = df["Attrition"].map({
    "No": 0,
    "Yes": 1
})

# EmployeeNumber is an identifier, not a predictive feature
X = df.drop(columns=["Attrition", "EmployeeNumber"])
y = df["Attrition"]

# ---------------------------------------------------------
# Recreate the same train/test split used during training
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nDataset:")
print(f"Total records : {len(df)}")
print(f"Training set  : {len(X_train)}")
print(f"Test set      : {len(X_test)}")

# ---------------------------------------------------------
# Load trained model
# ---------------------------------------------------------

model = joblib.load(MODEL_PATH)

print("\nModel loaded successfully.")

# ---------------------------------------------------------
# Predict probabilities
# ---------------------------------------------------------

probabilities = model.predict_proba(X_test)[:, 1]

# Default model prediction at threshold 0.5
predictions_05 = (probabilities >= 0.50).astype(int)

# Project/business prediction at threshold 0.6
predictions_06 = (probabilities >= RISK_THRESHOLD).astype(int)

# ---------------------------------------------------------
# Standard model evaluation at threshold 0.5
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL PERFORMANCE - THRESHOLD 0.50")
print("=" * 70)

accuracy = accuracy_score(y_test, predictions_05)
precision = precision_score(y_test, predictions_05, zero_division=0)
recall = recall_score(y_test, predictions_05, zero_division=0)
f1 = f1_score(y_test, predictions_05, zero_division=0)
roc_auc = roc_auc_score(y_test, probabilities)

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-Score  : {f1:.4f}")
print(f"ROC-AUC    : {roc_auc:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions_05))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions_05,
        target_names=["No Attrition", "Attrition"],
        zero_division=0
    )
)

# ---------------------------------------------------------
# Business threshold evaluation at 0.60
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("BUSINESS PERFORMANCE - RISK THRESHOLD 0.60")
print("=" * 70)

accuracy_06 = accuracy_score(y_test, predictions_06)
precision_06 = precision_score(y_test, predictions_06, zero_division=0)
recall_06 = recall_score(y_test, predictions_06, zero_division=0)
f1_06 = f1_score(y_test, predictions_06, zero_division=0)

print(f"Risk Threshold : {RISK_THRESHOLD:.2f}")
print(f"Accuracy       : {accuracy_06:.4f}")
print(f"Precision      : {precision_06:.4f}")
print(f"Recall         : {recall_06:.4f}")
print(f"F1-Score       : {f1_06:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions_06))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions_06,
        target_names=["No Attrition", "Attrition"],
        zero_division=0
    )
)

# ---------------------------------------------------------
# Save test predictions
# ---------------------------------------------------------

test_results = pd.DataFrame({
    "ActualAttrition": y_test.values,
    "AttritionProbability": probabilities.round(4),
    "PredictedAttrition_0.5": predictions_05,
    "PredictedAttrition_0.6": predictions_06
})

test_results.to_csv(OUTPUT_PATH, index=False)

print("\nTest predictions saved to:")
print(OUTPUT_PATH)

# ---------------------------------------------------------
# ROC Curve data
# ---------------------------------------------------------

fpr, tpr, thresholds = roc_curve(y_test, probabilities)

roc_data = pd.DataFrame({
    "FalsePositiveRate": fpr,
    "TruePositiveRate": tpr,
    "Threshold": thresholds
})

roc_output = "ml/results/roc_curve_data.csv"
roc_data.to_csv(roc_output, index=False)

print("\nROC curve data saved to:")
print(roc_output)

print("\n" + "=" * 70)
print("MODEL EVALUATION COMPLETED")
print("=" * 70)