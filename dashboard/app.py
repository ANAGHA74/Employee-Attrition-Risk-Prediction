"""
Streamlit HR Analytics & Attrition Risk Prediction Dashboard.
Visualizes live employee records from Hadoop HDFS and displays ML attrition risk predictions.
"""

import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="HR Employee Attrition Risk Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Project paths
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
from export_hdfs_data import export_hdfs_data, run_ml_prediction_on_hdfs_data
from predict import load_model, predict_employee, RISK_THRESHOLD

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .high-risk-badge {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def load_dataset() -> pd.DataFrame:
    """Load latest exported HDFS records, falling back to clean data if needed."""
    hdfs_export_file = PROJECT_ROOT / "data" / "processed" / "hdfs_exported_employees.csv"
    clean_data_file = PROJECT_ROOT / "data" / "processed" / "employees_clean.csv"
    
    if hdfs_export_file.exists():
        df = pd.read_csv(hdfs_export_file)
        if not df.empty:
            return df
            
    if clean_data_file.exists():
        return pd.read_csv(clean_data_file)
        
    return pd.DataFrame()


def main():
    st.markdown('<div class="main-header">👥 Employee Attrition Risk Prediction Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Big Data Analytics Pipeline: Apache Kafka → Hadoop HDFS → Machine Learning</div>', unsafe_allow_html=True)

    # Sidebar: Pipeline Status & Controls
    st.sidebar.image("https://img.icons8.com/color/96/hadoop-distributed-file-system.png", width=60)
    st.sidebar.title("HDFS & Pipeline Status")
    
    hdfs_connected = check_hdfs_connection(timeout=3)
    if hdfs_connected:
        st.sidebar.success("🟢 Hadoop HDFS NameNode: Connected (Port 9870)")
        hdfs_files = list_hdfs_directory(HDFS_RAW_DIR)
        batch_count = len([f for f in hdfs_files if f.get("type") == "FILE"])
        st.sidebar.metric("Raw Batches in HDFS", f"{batch_count} files")
    else:
        st.sidebar.error("🔴 Hadoop HDFS: Disconnected / Local Spool")
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Synchronization")
    if st.sidebar.button("🔄 Sync & Export from HDFS", use_container_width=True):
        with st.spinner("Exporting batches from HDFS..."):
            try:
                export_hdfs_data(deduplicate=True)
                st.sidebar.success("Export completed successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Export error: {e}")

    # Load Employee Feature Data
    df = load_dataset()
    if df.empty:
        st.warning("⚠️ No employee records found in HDFS or local storage. Please stream data via Kafka Producer.")
        return

    # Load Model and Predict
    try:
        model = load_model()
        # Drop non-feature columns if present
        clean_df = df.dropna()
        predictions = predict_employee(model, clean_df)
        
        # Merge predictions back with demographic details for display
        display_df = pd.merge(
            predictions,
            clean_df[["EmployeeNumber", "Age", "Department", "JobRole", "MonthlyIncome", "OverTime", "YearsAtCompany", "JobSatisfaction"]],
            on="EmployeeNumber",
            how="left"
        )
    except Exception as e:
        st.error(f"Error running ML inference: {e}")
        return

    # Top KPI Metrics Row
    total_emp = len(display_df)
    high_risk_count = (display_df["RiskLevel"] == "HIGH").sum()
    med_risk_count = (display_df["RiskLevel"] == "MEDIUM").sum()
    low_risk_count = (display_df["RiskLevel"] == "LOW").sum()
    hr_review_count = (display_df["HRReview"] == "YES").sum()
    avg_risk = display_df["AttritionProbability"].mean() * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Employees", f"{total_emp:,}")
    with col2:
        st.metric("🚨 High Risk (>= 0.60)", f"{high_risk_count}", f"{(high_risk_count/total_emp)*100:.1f}%", delta_color="inverse")
    with col3:
        st.metric("⚠️ Medium Risk", f"{med_risk_count}", f"{(med_risk_count/total_emp)*100:.1f}%")
    with col4:
        st.metric("✅ Low Risk", f"{low_risk_count}", f"{(low_risk_count/total_emp)*100:.1f}%")
    with col5:
        st.metric("Avg Attrition Risk", f"{avg_risk:.1f}%")

    st.markdown("---")

    # Analytics Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Risk Analytics & Demographics", "🚨 High-Risk Employees (Action List)", "🧠 Key Attrition Drivers"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Attrition Risk Distribution")
            fig, ax = plt.subplots(figsize=(6, 4))
            palette = {"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#10B981"}
            sns.countplot(data=display_df, x="RiskLevel", order=["LOW", "MEDIUM", "HIGH"], palette=palette, ax=ax)
            ax.set_title("Employee Count by Risk Category")
            ax.set_ylabel("Employees")
            st.pyplot(fig)
            plt.close()

        with c2:
            st.subheader("Risk by Department")
            fig, ax = plt.subplots(figsize=(6, 4))
            dept_risk = display_df.groupby("Department")["AttritionProbability"].mean().reset_index()
            sns.barplot(data=dept_risk, x="Department", y="AttritionProbability", palette="Blues_r", ax=ax)
            ax.set_title("Average Attrition Probability by Department")
            ax.set_ylim(0, 1)
            plt.xticks(rotation=15)
            st.pyplot(fig)
            plt.close()

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("OverTime Impact on Risk")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.boxplot(data=display_df, x="OverTime", y="AttritionProbability", palette="Set2", ax=ax)
            ax.set_title("Attrition Probability by OverTime Status")
            st.pyplot(fig)
            plt.close()

        with c4:
            st.subheader("Monthly Income vs. Attrition Probability")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.scatterplot(data=display_df, x="MonthlyIncome", y="AttritionProbability", hue="RiskLevel", palette=palette, ax=ax, alpha=0.8)
            ax.set_title("Income vs. Risk Level")
            st.pyplot(fig)
            plt.close()

    with tab2:
        st.subheader("Employees Requiring Immediate HR Intervention (Probability >= 0.60)")
        
        # Filter controls
        dept_filter = st.multiselect("Filter by Department:", options=display_df["Department"].unique(), default=display_df["Department"].unique())
        filtered_df = display_df[(display_df["Department"].isin(dept_filter)) & (display_df["RiskLevel"] == "HIGH")].sort_values("AttritionProbability", ascending=False)
        
        st.dataframe(
            filtered_df[[
                "EmployeeNumber", "AttritionProbability", "RiskLevel", "HRReview",
                "Department", "JobRole", "OverTime", "MonthlyIncome", "YearsAtCompany", "JobSatisfaction"
            ]],
            use_container_width=True,
            hide_index=True
        )
        
        # CSV Export button
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download High Risk Action Report (CSV)",
            data=csv_data,
            file_name="high_risk_employees_action_list.csv",
            mime="text/csv"
        )

    with tab3:
        st.subheader("Top Model Features Driving Attrition")
        coeff_file = PROJECT_ROOT / "ml" / "results" / "feature_coefficients.csv"
        if coeff_file.exists():
            coeff_df = pd.read_csv(coeff_file)
            col_pos, col_neg = st.columns(2)
            with col_pos:
                st.markdown("**Top Factors Increasing Attrition Risk (Positive Drivers):**")
                pos_factors = coeff_df[coeff_df["Coefficient"] > 0].head(8)
                st.dataframe(pos_factors[["Feature", "Coefficient"]], hide_index=True)
            with col_neg:
                st.markdown("**Top Factors Reducing Attrition Risk (Retention Drivers):**")
                neg_factors = coeff_df[coeff_df["Coefficient"] < 0].head(8)
                st.dataframe(neg_factors[["Feature", "Coefficient"]], hide_index=True)
        else:
            st.info("Run `python ml/train.py` or `python ml/feature_importance.py` to generate factor coefficients.")


if __name__ == "__main__":
    main()
