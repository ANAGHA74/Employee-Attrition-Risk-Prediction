"""
Unified Data Loader and Model Scoring Utility for HR SaaS Dashboard.
Loads genuine HDFS exported data or local dataset, runs Scikit-learn
inference, and caches computed metrics for consistent display across all pages.
"""

import sys
import warnings
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import pandas as pd
import streamlit as st

# Suppress sklearn unpickle version warnings for clean output
warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "hdfs"))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from predict import load_model, predict_employee, RISK_THRESHOLD

EXPORT_FILE = PROJECT_ROOT / "data" / "processed" / "hdfs_exported_employees.csv"
CLEAN_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "employees_clean.csv"
PREDICTION_FILE = PROJECT_ROOT / "ml" / "results" / "hdfs_employee_risk_predictions.csv"
COEFF_FILE = PROJECT_ROOT / "ml" / "results" / "feature_coefficients.csv"


def get_file_last_modified(path: Path) -> str:
    """Return human-readable timestamp of file modification."""
    if not path.exists():
        return "Not available"
    return pd.Timestamp(path.stat().st_mtime, unit="s").strftime("%d %b %Y, %I:%M %p")


def format_feature_name(feature: str) -> str:
    """Transform pipeline encoded feature names into clean HR labels."""
    readable = feature.replace("categorical__", "").replace("numerical__", "")
    readable = readable.replace("_", " ")
    if " " in readable:
        parts = readable.split(" ")
        if len(parts) > 1 and parts[-1] in {"Yes", "No"}:
            return f"{' '.join(parts[:-1])} ({parts[-1]})"
    return readable


@st.cache_data(ttl=60, show_spinner=False)
def load_and_score_data() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load employee records, run scikit-learn model inference,
    and calculate core HR metrics.
    """
    data_source_name = "None"
    data_file_used = None

    if EXPORT_FILE.exists() and EXPORT_FILE.stat().st_size > 0:
        raw_df = pd.read_csv(EXPORT_FILE)
        if not raw_df.empty:
            data_source_name = "HDFS Exported Records"
            data_file_used = EXPORT_FILE
    elif CLEAN_DATA_FILE.exists() and CLEAN_DATA_FILE.stat().st_size > 0:
        raw_df = pd.read_csv(CLEAN_DATA_FILE)
        data_source_name = "Local Cleaned Dataset"
        data_file_used = CLEAN_DATA_FILE
    else:
        raw_df = pd.DataFrame()

    if raw_df.empty:
        return pd.DataFrame(), {
            "source": "None",
            "total_analyzed": 0,
            "hr_review_count": 0,
            "hr_review_pct": 0.0,
            "avg_predicted_risk": 0.0,
            "last_updated": "Not available",
            "departments": []
        }

    # Load model and run inference
    try:
        model = load_model()
        clean_df = raw_df.dropna()
        predictions = predict_employee(model, clean_df)

        detail_columns = [
            "EmployeeNumber", "Age", "Department", "JobRole", "MonthlyIncome",
            "OverTime", "YearsAtCompany", "JobSatisfaction", "BusinessTravel",
            "DistanceFromHome", "EnvironmentSatisfaction", "JobInvolvement",
            "WorkLifeBalance", "YearsSinceLastPromotion", "YearsWithCurrManager",
            "Gender", "Education", "EducationField", "MaritalStatus", "Attrition",
            "TotalWorkingYears", "NumCompaniesWorked", "StockOptionLevel"
        ]
        available_detail = [col for col in detail_columns if col in clean_df.columns]
        display_df = pd.merge(
            predictions,
            clean_df[available_detail],
            on="EmployeeNumber",
            how="left"
        )
        display_df["RiskPercent"] = display_df["AttritionProbability"] * 100

    except Exception as e:
        st.error(f"Error executing ML inference pipeline: {e}")
        return pd.DataFrame(), {"error": str(e)}

    # Compute genuine summary metrics
    total_analyzed = len(display_df)
    hr_review_count = int((display_df["HRReview"] == "YES").sum())
    hr_review_pct = (hr_review_count / total_analyzed * 100) if total_analyzed else 0.0
    avg_predicted_risk = float(display_df["AttritionProbability"].mean() * 100) if total_analyzed else 0.0

    high_count = int((display_df["RiskLevel"] == "HIGH").sum())
    med_count = int((display_df["RiskLevel"] == "MEDIUM").sum())
    low_count = int((display_df["RiskLevel"] == "LOW").sum())

    high_pct = (high_count / total_analyzed * 100) if total_analyzed else 0.0
    med_pct = (med_count / total_analyzed * 100) if total_analyzed else 0.0
    low_pct = (low_count / total_analyzed * 100) if total_analyzed else 0.0

    departments = sorted(display_df["Department"].dropna().unique().tolist()) if "Department" in display_df.columns else []

    timestamp_str = get_file_last_modified(data_file_used) if data_file_used else "Not available"

    # Top 5 highest risk
    top_5 = display_df.sort_values("AttritionProbability", ascending=False).head(5).copy()

    meta = {
        "source": data_source_name,
        "total_analyzed": total_analyzed,
        "hr_review_count": hr_review_count,
        "hr_review_pct": hr_review_pct,
        "avg_predicted_risk": avg_predicted_risk,
        "high_count": high_count,
        "high_pct": high_pct,
        "med_count": med_count,
        "med_pct": med_pct,
        "low_count": low_count,
        "low_pct": low_pct,
        "departments": departments,
        "last_updated": timestamp_str,
        "top_5": top_5,
        "threshold": RISK_THRESHOLD,
        "data_file_path": str(data_file_used) if data_file_used else "None"
    }

    return display_df, meta


def load_model_coefficients() -> pd.DataFrame:
    """Load model feature coefficients from ml/results."""
    if not COEFF_FILE.exists():
        return pd.DataFrame()
    df = pd.read_csv(COEFF_FILE)
    df["ReadableFeature"] = df["Feature"].apply(format_feature_name)
    return df
