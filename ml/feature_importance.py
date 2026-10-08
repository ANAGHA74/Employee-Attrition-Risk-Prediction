import joblib
import pandas as pd
import matplotlib.pyplot as plt

MODEL_PATH = "ml/models/attrition_model.pkl"
OUTPUT_CSV = "ml/results/feature_coefficients.csv"
OUTPUT_PNG = "ml/results/top_attrition_factors.png"

print("=" * 70)
print("LOGISTIC REGRESSION - FEATURE IMPORTANCE")
print("=" * 70)

# Load trained pipeline
model = joblib.load(MODEL_PATH)

# Get preprocessing and classifier steps
preprocessor = model.named_steps["preprocessing"]
classifier = model.named_steps["classifier"]

# Get transformed feature names
feature_names = preprocessor.get_feature_names_out()

# Get logistic regression coefficients
coefficients = classifier.coef_[0]

# Create dataframe
importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Coefficient": coefficients
})

# Positive coefficient = higher predicted attrition probability
# Negative coefficient = lower predicted attrition probability
importance_df["AbsoluteCoefficient"] = (
    importance_df["Coefficient"].abs()
)

importance_df = importance_df.sort_values(
    "AbsoluteCoefficient",
    ascending=False
)

# Save complete coefficient table
importance_df.to_csv(OUTPUT_CSV, index=False)

print("\nTop factors associated with higher attrition risk:")
print(
    importance_df[
        importance_df["Coefficient"] > 0
    ].head(15)[
        ["Feature", "Coefficient"]
    ].to_string(index=False)
)

print("\nTop factors associated with lower attrition risk:")
print(
    importance_df[
        importance_df["Coefficient"] < 0
    ].head(15)[
        ["Feature", "Coefficient"]
    ].to_string(index=False)
)

# ---------------------------------------------------------
# Plot top positive and negative coefficients
# ---------------------------------------------------------

positive = (
    importance_df[importance_df["Coefficient"] > 0]
    .sort_values("Coefficient", ascending=False)
    .head(10)
)

negative = (
    importance_df[importance_df["Coefficient"] < 0]
    .sort_values("Coefficient")
    .head(10)
)

plot_df = pd.concat([
    positive,
    negative
]).sort_values("Coefficient")

plt.figure(figsize=(10, 8))

plt.barh(
    plot_df["Feature"],
    plot_df["Coefficient"]
)

plt.axvline(
    x=0,
    linewidth=1
)

plt.xlabel("Logistic Regression Coefficient")
plt.ylabel("Feature")
plt.title("Top Factors Associated with Employee Attrition Risk")

plt.tight_layout()

plt.savefig(
    OUTPUT_PNG,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nCoefficient table saved to:")
print(OUTPUT_CSV)

print("\nFeature importance chart saved to:")
print(OUTPUT_PNG)

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
print("=" * 70)