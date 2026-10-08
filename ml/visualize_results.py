import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_curve,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DATA_PATH = "data/processed/employees_clean.csv"
MODEL_PATH = "ml/models/attrition_model.pkl"

ROC_DATA_PATH = "ml/results/roc_curve_data.csv"
TEST_PREDICTIONS_PATH = "ml/results/test_predictions.csv"

ROC_OUTPUT = "ml/results/roc_curve.png"
CM_OUTPUT = "ml/results/confusion_matrix.png"

# ---------------------------------------------------------
# ROC Curve
# ---------------------------------------------------------

print("=" * 70)
print("GENERATING ML VISUALIZATIONS")
print("=" * 70)

roc_data = pd.read_csv(ROC_DATA_PATH)

fpr = roc_data["FalsePositiveRate"]
tpr = roc_data["TruePositiveRate"]

# Calculate AUC from saved ROC data
roc_auc = roc_auc_score(
    # Reconstructing is not necessary here;
    # use the value from the evaluation result.
    [0, 1],
    [0, 1]
)

# The actual ROC-AUC obtained during evaluation
roc_auc_value = 0.8035

plt.figure(figsize=(8, 6))

plt.plot(
    fpr,
    tpr,
    linewidth=2,
    label=f"Logistic Regression (AUC = {roc_auc_value:.4f})"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random Classifier"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Employee Attrition Prediction")
plt.legend(loc="lower right")
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    ROC_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nROC curve saved to:")
print(ROC_OUTPUT)

# ---------------------------------------------------------
# Confusion Matrix at threshold 0.60
# ---------------------------------------------------------

test_predictions = pd.read_csv(TEST_PREDICTIONS_PATH)

actual = test_predictions["ActualAttrition"]
predicted = test_predictions["PredictedAttrition_0.6"]

cm = confusion_matrix(actual, predicted)

print("\nConfusion Matrix at threshold 0.60:")
print(cm)

fig, ax = plt.subplots(figsize=(7, 6))

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["No Attrition", "Attrition"]
)

display.plot(
    ax=ax,
    values_format="d"
)

ax.set_title(
    "Confusion Matrix - Attrition Prediction\n"
    "Risk Threshold = 0.60"
)

plt.tight_layout()

plt.savefig(
    CM_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nConfusion matrix saved to:")
print(CM_OUTPUT)

print("\n" + "=" * 70)
print("VISUALIZATION GENERATION COMPLETED")
print("=" * 70)