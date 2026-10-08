import pandas as pd

from predict import load_model, predict_employee


DATA_PATH = "data/processed/employees_clean.csv"


# Load one employee from the dataset
df = pd.read_csv(DATA_PATH)

employee = df.iloc[[0]].copy()

# Keep actual attrition separately for demonstration
actual_attrition = employee["Attrition"].iloc[0]
employee_number = employee["EmployeeNumber"].iloc[0]

# Load model
model = load_model()

# Generate prediction
result = predict_employee(
    model,
    employee
)

print("=" * 70)
print("SINGLE EMPLOYEE ATTRITION PREDICTION")
print("=" * 70)

print(f"\nEmployee Number       : {employee_number}")
print(f"Actual Attrition      : {actual_attrition}")
print(
    f"Predicted Probability : "
    f"{result['AttritionProbability'].iloc[0]:.4f}"
)
print(
    f"Risk Level            : "
    f"{result['RiskLevel'].iloc[0]}"
)
print(
    f"HR Review             : "
    f"{result['HRReview'].iloc[0]}"
)

print("\n" + "=" * 70)