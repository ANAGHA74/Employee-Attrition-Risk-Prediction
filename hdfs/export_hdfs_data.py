"""
HDFS Data Export, Sanitization, and ML Integration Utility
for HR Employee Attrition Risk Prediction.

Exports persisted employee batches from Hadoop HDFS, isolates test/synthetic payloads,
deduplicates production records, and interfaces with Person 3's trained Machine
Learning model for employee attrition risk prediction.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Setup project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "hdfs"))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from hdfs_utils import (
    check_hdfs_connection,
    list_hdfs_directory,
    read_all_records_from_hdfs,
    HDFS_RAW_DIR
)

# Import Person 3's ML prediction module
try:
    from predict import load_model, predict_employee, RISK_THRESHOLD
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("ExportHDFSData")

DEFAULT_EXPORT_PATH = PROJECT_ROOT / "data" / "processed" / "hdfs_exported_employees.csv"
DEFAULT_TEST_EXPORT_PATH = PROJECT_ROOT / "data" / "processed" / "hdfs_isolated_test_records.csv"
DEFAULT_PREDICTION_OUTPUT = PROJECT_ROOT / "ml" / "results" / "hdfs_employee_risk_predictions.csv"

# The 32 canonical columns in the standard IBM HR Attrition dataset (30 features + EmployeeNumber + Attrition)
CANONICAL_COLUMNS = [
    "Age", "Attrition", "BusinessTravel", "DailyRate", "Department",
    "DistanceFromHome", "Education", "EducationField", "EmployeeNumber",
    "EnvironmentSatisfaction", "Gender", "HourlyRate", "JobInvolvement",
    "JobLevel", "JobRole", "JobSatisfaction", "MaritalStatus",
    "MonthlyIncome", "MonthlyRate", "NumCompaniesWorked", "OverTime",
    "PercentSalaryHike", "PerformanceRating", "RelationshipSatisfaction",
    "StockOptionLevel", "TotalWorkingYears", "TrainingTimesLastYear",
    "WorkLifeBalance", "YearsAtCompany", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "YearsWithCurrManager"
]


def separate_production_and_test_records(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Distinguish legitimate production employee records from synthetic/test payloads.
    
    A record is classified as a test/synthetic record if:
      1. It has an explicit test marker ('record_type' == 'test_synthetic' or 'is_test' == True), OR
      2. It lacks any of the 32 mandatory canonical employee fields, OR
      3. Any canonical feature value is null/NaN.
      
    Returns:
        Tuple[production_df, test_df]
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    records = df.copy()
    
    # Check for explicit test tags
    is_test_marker = pd.Series(False, index=records.index)
    if "record_type" in records.columns:
        is_test_marker = is_test_marker | (records["record_type"] == "test_synthetic")
    if "is_test" in records.columns:
        is_test_marker = is_test_marker | (records["is_test"] == True)
        
    # Check for missing canonical columns or null values
    existing_canonical = [col for col in CANONICAL_COLUMNS if col in records.columns]
    missing_cols = set(CANONICAL_COLUMNS) - set(existing_canonical)
    
    if missing_cols:
        # If the entire dataframe is missing columns, all are incomplete
        has_nulls_or_missing = pd.Series(True, index=records.index)
    else:
        has_nulls_or_missing = records[CANONICAL_COLUMNS].isna().any(axis=1)
        
    test_mask = is_test_marker | has_nulls_or_missing
    
    prod_df = records[~test_mask].copy()
    test_df = records[test_mask].copy()
    
    # Add audit reason to test records
    reasons = []
    for idx, row in test_df.iterrows():
        r = []
        if is_test_marker.get(idx, False):
            r.append("Explicit test payload tag")
        missing_fields = [c for c in CANONICAL_COLUMNS if c not in row or pd.isna(row[c])]
        if missing_fields:
            r.append(f"Missing {len(missing_fields)} canonical feature(s): {missing_fields[:3]}...")
        reasons.append("; ".join(r) if r else "Incomplete record")
        
    test_df["isolation_reason"] = reasons
    
    return prod_df, test_df


def export_hdfs_data(
    source_dir: str = HDFS_RAW_DIR,
    output_path: Path = DEFAULT_EXPORT_PATH,
    test_output_path: Path = DEFAULT_TEST_EXPORT_PATH,
    deduplicate: bool = True,
    isolate_tests: bool = True,
    limit: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch all employee records stored in HDFS, deduplicate, isolate test records,
    and export clean business dataset to local CSV.
    
    Args:
        source_dir: HDFS directory containing raw batch files.
        output_path: Local filesystem destination path for clean production CSV.
        test_output_path: Local path for isolated test records CSV.
        deduplicate: If True, keeps the latest record per EmployeeNumber based on event_timestamp.
        isolate_tests: If True, separates test/synthetic records from production data.
        limit: Max production records to export.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (production_df, test_df)
    """
    logger.info("=" * 65)
    logger.info("EXPORTING EMPLOYEE RECORDS FROM HDFS")
    logger.info("=" * 65)
    logger.info("Source HDFS Directory : %s", source_dir)
    logger.info("Destination Clean CSV : %s", output_path)
    logger.info("Destination Test CSV  : %s", test_output_path)
    
    # 1. Verify HDFS connectivity
    if not check_hdfs_connection():
        logger.error("HDFS NameNode is not accessible. Cannot export records.")
        raise ConnectionError("Unable to reach Hadoop HDFS NameNode.")
        
    # 2. List batch files in HDFS
    files = list_hdfs_directory(source_dir)
    file_list = [f.get("pathSuffix") for f in files if f.get("type") == "FILE"]
    logger.info("Found %d batch file(s) in HDFS directory %s", len(file_list), source_dir)
    
    if not file_list:
        logger.warning("No batch files found in %s.", source_dir)
        return pd.DataFrame(), pd.DataFrame()
        
    # 3. Read records from all batch files
    records = read_all_records_from_hdfs(source_dir)
    raw_count = len(records)
    logger.info("Read %d total raw record(s) across all batches from HDFS.", raw_count)
    
    if not records:
        logger.warning("No records parsed from HDFS files.")
        return pd.DataFrame(), pd.DataFrame()
        
    df = pd.DataFrame(records)
    logger.info("Initial raw DataFrame shape: %s", df.shape)
    
    # 4. Deduplication
    if deduplicate and "EmployeeNumber" in df.columns:
        if "event_timestamp" in df.columns:
            # Sort by timestamp ascending, keep last record
            df = df.sort_values("event_timestamp").groupby("EmployeeNumber", as_index=False).last()
        else:
            df = df.drop_duplicates(subset=["EmployeeNumber"], keep="last")
        logger.info("Shape after deduplication: %s (%d unique employee IDs)", df.shape, df["EmployeeNumber"].nunique())
        
    # 5. Isolate Test Records vs Production Records
    if isolate_tests:
        prod_df, test_df = separate_production_and_test_records(df)
        logger.info("Separated %d clean production record(s) and %d isolated test record(s).", len(prod_df), len(test_df))
    else:
        prod_df = df
        test_df = pd.DataFrame()
        
    if limit and len(prod_df) > limit:
        prod_df = prod_df.head(limit)
        logger.info("Applied production record limit: %d rows", limit)
        
    # 6. Format clean production DataFrame: ensure canonical columns and sort by EmployeeNumber
    clean_cols = [c for c in CANONICAL_COLUMNS if c in prod_df.columns]
    # Retain event_timestamp if present for auditability
    if "event_timestamp" in prod_df.columns:
        export_df = prod_df[clean_cols + ["event_timestamp"]].copy()
    else:
        export_df = prod_df[clean_cols].copy()
        
    export_df = export_df.sort_values("EmployeeNumber").reset_index(drop=True)
    
    # 7. Save to local CSVs
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_csv(output_path, index=False)
    logger.info("Successfully exported %d clean production records to: %s", len(export_df), output_path)
    
    if not test_df.empty:
        test_output_path = Path(test_output_path)
        test_output_path.parent.mkdir(parents=True, exist_ok=True)
        test_df.to_csv(test_output_path, index=False)
        logger.info("Successfully exported %d isolated test records to: %s", len(test_df), test_output_path)
        
    logger.info("=" * 65)
    return export_df, test_df


def run_ml_prediction_on_hdfs_data(
    exported_df: pd.DataFrame,
    output_prediction_path: Path = DEFAULT_PREDICTION_OUTPUT
) -> pd.DataFrame:
    """
    Pass the cleaned exported HDFS dataset directly to Person 3's ML prediction model.
    Does NOT retrain or alter Person 3's model architecture or weights.
    
    Args:
        exported_df: Clean production DataFrame containing employee features.
        output_prediction_path: Destination path for risk predictions CSV.
        
    Returns:
        pd.DataFrame: Prediction results with EmployeeNumber, AttritionProbability, RiskLevel, HRReview.
    """
    if not ML_AVAILABLE:
        logger.error("Person 3's ML modules (predict.py) could not be loaded.")
        return pd.DataFrame()
        
    logger.info("=" * 65)
    logger.info("RUNNING PERSON 3's ML ATTRITION PREDICTION ON HDFS DATA")
    logger.info("=" * 65)
    
    model = load_model()
    logger.info("Loaded pre-trained model: %s", model)
    
    initial_count = len(exported_df)
    eval_df = exported_df.copy()
    
    # Generate predictions using Person 3's pipeline
    predictions = predict_employee(model, eval_df)
    
    # Display risk summary
    print("\n" + "=" * 60)
    print("HDFS EMPLOYEE ATTRITION RISK SUMMARY")
    print("=" * 60)
    print(predictions["RiskLevel"].value_counts().to_string())
    print("\nHR Review Required (Score >= 0.60):")
    print(predictions["HRReview"].value_counts().to_string())
    
    high_risk = predictions[predictions["RiskLevel"] == "HIGH"].sort_values(
        "AttritionProbability", ascending=False
    )
    print("\nTop High Risk Employees from HDFS Stream:")
    print(high_risk.head(10).to_string(index=False))
    print("=" * 60 + "\n")
    
    # Save predictions
    output_prediction_path = Path(output_prediction_path)
    output_prediction_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_prediction_path, index=False)
    logger.info("Saved ML predictions on HDFS data to: %s", output_prediction_path)
    
    # Also save a copy to ml/results/employee_risk_predictions.csv for compatibility
    legacy_output = PROJECT_ROOT / "ml" / "results" / "employee_risk_predictions.csv"
    legacy_output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(legacy_output, index=False)
    logger.info("Saved ML predictions copy to: %s", legacy_output)
    
    return predictions


def main():
    parser = argparse.ArgumentParser(description="Export HDFS employee data and run ML predictions")
    parser.add_argument("--source-dir", type=str, default=HDFS_RAW_DIR, help="HDFS source directory")
    parser.add_argument("--output", type=str, default=str(DEFAULT_EXPORT_PATH), help="Local clean CSV destination")
    parser.add_argument("--test-output", type=str, default=str(DEFAULT_TEST_EXPORT_PATH), help="Local test CSV destination")
    parser.add_argument("--predict", action="store_true", help="Run Person 3's ML model inference on exported data")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of exported records")
    parser.add_argument("--no-dedup", action="store_true", help="Disable deduplication by EmployeeNumber")
    parser.add_argument("--no-isolate-tests", action="store_true", help="Disable test record isolation")
    
    args = parser.parse_args()
    
    prod_df, test_df = export_hdfs_data(
        source_dir=args.source_dir,
        output_path=Path(args.output),
        test_output_path=Path(args.test_output),
        deduplicate=not args.no_dedup,
        isolate_tests=not args.no_isolate_tests,
        limit=args.limit
    )
    
    if args.predict and not prod_df.empty:
        run_ml_prediction_on_hdfs_data(prod_df)


if __name__ == "__main__":
    main()
