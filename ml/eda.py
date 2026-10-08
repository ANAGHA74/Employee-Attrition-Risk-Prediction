import pandas as pd

# ============================================================
# Configuration
# ============================================================

DATA_PATH = "data/processed/employees_clean.csv"


# ============================================================
# Load Dataset
# ============================================================

print("=" * 70)
print("EMPLOYEE ATTRITION - EXPLORATORY DATA ANALYSIS")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print("\nDataset loaded successfully.")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")


# ============================================================
# Basic Information
# ============================================================

print("\n" + "=" * 70)
print("FIRST 5 ROWS")
print("=" * 70)

print(df.head())


print("\n" + "=" * 70)
print("COLUMN NAMES")
print("=" * 70)

for column in df.columns:
    print(column)


print("\n" + "=" * 70)
print("DATA TYPES")
print("=" * 70)

print(df.dtypes)


# ============================================================
# Missing Values
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

missing_values = df.isnull().sum()

print(missing_values[missing_values > 0])

if missing_values.sum() == 0:
    print("No missing values found.")


# ============================================================
# Duplicate Rows
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE ROWS")
print("=" * 70)

print(f"Duplicate rows: {df.duplicated().sum()}")


# ============================================================
# Target Variable: Attrition
# ============================================================

print("\n" + "=" * 70)
print("ATTRITION DISTRIBUTION")
print("=" * 70)

attrition_counts = df["Attrition"].value_counts()

print(attrition_counts)


print("\nAttrition percentages:")

attrition_percentages = (
    df["Attrition"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print(attrition_percentages)


# ============================================================
# Attrition by Overtime
# ============================================================

print("\n" + "=" * 70)
print("ATTRITION BY OVERTIME (%)")
print("=" * 70)

overtime_analysis = pd.crosstab(
    df["OverTime"],
    df["Attrition"],
    normalize="index"
) * 100

print(overtime_analysis.round(2))


# ============================================================
# Attrition by Job Satisfaction
# ============================================================

print("\n" + "=" * 70)
print("ATTRITION BY JOB SATISFACTION (%)")
print("=" * 70)

satisfaction_analysis = pd.crosstab(
    df["JobSatisfaction"],
    df["Attrition"],
    normalize="index"
) * 100

print(satisfaction_analysis.round(2))


# ============================================================
# Attrition by Department
# ============================================================

print("\n" + "=" * 70)
print("ATTRITION BY DEPARTMENT (%)")
print("=" * 70)

department_analysis = pd.crosstab(
    df["Department"],
    df["Attrition"],
    normalize="index"
) * 100

print(department_analysis.round(2))


# ============================================================
# Attrition by Job Role
# ============================================================

print("\n" + "=" * 70)
print("ATTRITION BY JOB ROLE (%)")
print("=" * 70)

job_role_analysis = pd.crosstab(
    df["JobRole"],
    df["Attrition"],
    normalize="index"
) * 100

print(job_role_analysis.round(2))


# ============================================================
# Numerical Summary
# ============================================================

print("\n" + "=" * 70)
print("NUMERICAL SUMMARY")
print("=" * 70)

print(df.describe().T)


# ============================================================
# End
# ============================================================

print("\n" + "=" * 70)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 70)