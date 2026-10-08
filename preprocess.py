"""
Preprocess the raw IBM HR Employee Attrition dataset.
Drops constant columns, checks data quality, and saves cleaned data.
"""

import pandas as pd
from pathlib import Path
import sys

# Build absolute paths from this script's location
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "employees_clean.csv"


def preprocess_data():
    """Load, clean, and save the employee dataset."""
    
    # Read the raw CSV
    print(f"Loading data from: {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Original shape: {df.shape}")
    
    # Drop constant columns (same value for all rows)
    constant_columns = ['EmployeeCount', 'StandardHours', 'Over18']
    print(f"Dropping constant columns: {constant_columns}")
    df = df.drop(columns=constant_columns)
    
    # Check for null values
    null_counts = df.isnull().sum()
    null_summary = null_counts[null_counts > 0]
    if len(null_summary) > 0:
        print("\nNull values found:")
        print(null_summary)
    else:
        print("\nNo null values found in the dataset.")
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    print(f"\nDuplicate rows: {duplicate_count}")
    
    # Report Attrition class balance
    attrition_counts = df['Attrition'].value_counts()
    print("\nAttrition class distribution:")
    print(attrition_counts)
    attrition_percent = df['Attrition'].value_counts(normalize=True) * 100
    print("\nAttrition class percentages:")
    print(attrition_percent)
    
    # Ensure processed directory exists
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned data
    print(f"\nSaving cleaned data to: {PROCESSED_DATA_PATH}")
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Cleaned shape: {df.shape}")
    print("Preprocessing complete!")


if __name__ == "__main__":
    try:
        preprocess_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure the raw data file exists at: {RAW_DATA_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
