"""
Dedicated Pipeline & Data Section.
Keeps technical Hadoop HDFS health, raw batch statistics, Kafka consumer
state, and HDFS sync triggers cleanly separated from daily HR-facing workspaces.
"""

import textwrap
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import streamlit as st

from dashboard.components.top_header import render_top_header
from dashboard.data_loader import get_file_last_modified, EXPORT_FILE, PREDICTION_FILE

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# HDFS integration imports
try:
    from hdfs_utils import (
        check_hdfs_connection,
        list_hdfs_directory,
        HDFS_RAW_DIR
    )
    from export_hdfs_data import export_hdfs_data, run_ml_prediction_on_hdfs_data
    HDFS_IMPORTS_AVAILABLE = True
except Exception:
    HDFS_IMPORTS_AVAILABLE = False


def render_pipeline_page(display_df: pd.DataFrame, meta: Dict[str, Any]):
    """Render the technical Pipeline & Data workspace."""
    st.markdown('<div class="pipeline-page-marker"></div>', unsafe_allow_html=True)

    render_top_header(
        title="Pipeline & Data Synchronization",
        subtitle="Technical infrastructure health, HDFS distributed batch metrics, and pipeline sync controls.",
        last_updated=meta.get("last_updated", "Live")
    )

    # Check live HDFS connection
    hdfs_connected = False
    batch_count = 0
    raw_files = []

    if HDFS_IMPORTS_AVAILABLE:
        try:
            hdfs_connected = check_hdfs_connection(timeout=3)
            if hdfs_connected:
                raw_files = list_hdfs_directory(HDFS_RAW_DIR)
                batch_count = len([f for f in raw_files if f.get("type") == "FILE"])
        except Exception:
            hdfs_connected = False

    # Status Cards Row
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        status_color = "#10B981" if hdfs_connected else "#DC2626"
        status_text = "CONNECTED" if hdfs_connected else "DISCONNECTED"
        status_icon = "🟢" if hdfs_connected else "🔴"
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card" style="border-left: 3px solid {status_color};">
                <div class="kpi-card-header">
                    <span class="kpi-label">Hadoop HDFS Status</span>
                    <span style="font-size: 1.1rem;">{status_icon}</span>
                </div>
                <div class="kpi-value" style="font-size: 1.7rem; color: {status_color};">{status_text}</div>
                <div class="kpi-subtext">WebHDFS port 9870</div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-label">Raw HDFS Batches</span>
                    <div class="kpi-icon-wrap kpi-icon-blue">📦</div>
                </div>
                <div class="kpi-value">{batch_count}</div>
                <div class="kpi-subtext">Persisted JSONL files</div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-label">Exported Records</span>
                    <div class="kpi-icon-wrap kpi-icon-teal">📊</div>
                </div>
                <div class="kpi-value">{len(display_df):,}</div>
                <div class="kpi-subtext">Deduplicated active cohort</div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-label">ML Scored Records</span>
                    <div class="kpi-icon-wrap kpi-icon-purple">🧠</div>
                </div>
                <div class="kpi-value">{meta.get('total_analyzed', 0):,}</div>
                <div class="kpi-subtext">Probabilities computed</div>
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Sync Controls
    with st.container(border=True):
        st.markdown(
            textwrap.dedent("""
            <div class="card-title">HDFS Synchronization Controls</div>
            <div class="card-subtitle">Export persisted streaming batches and regenerate inference probabilities</div>
            """),
            unsafe_allow_html=True
        )

        st.caption(f"Last HDFS Export: **{get_file_last_modified(EXPORT_FILE)}**")
        st.caption(f"Last ML Predictions: **{get_file_last_modified(PREDICTION_FILE)}**")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if st.button("🔄 Sync & Export from HDFS", key="hdfs_sync_action_btn", type="primary", use_container_width=True):
            if not hdfs_connected:
                st.error("❌ Cannot sync: Hadoop HDFS is currently disconnected. Please verify that your Docker HDFS container is running (`docker compose up -d`).")
            else:
                with st.spinner("Extracting batches from HDFS, sanitizing payloads, and running ML inference..."):
                    try:
                        prod_df, test_df = export_hdfs_data(deduplicate=True)
                        if prod_df.empty:
                            st.warning("⚠️ Export completed, but zero production employee records were found in HDFS.")
                        else:
                            predictions = run_ml_prediction_on_hdfs_data(prod_df)
                            if predictions.empty:
                                st.error("❌ Prediction generation returned empty results.")
                            else:
                                st.cache_data.clear()
                                st.success(f"✅ Successfully synchronized and scored {len(predictions):,} records from HDFS!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Synchronization pipeline error: {e}")

    # Detailed HDFS File List if connected
    if hdfs_connected and raw_files:
        with st.expander(f"📁 Browse Raw HDFS Batches ({len(raw_files)} files)"):
            file_records = []
            for item in raw_files:
                file_records.append({
                    "Filename": item.get("pathSuffix", "Unknown"),
                    "Type": item.get("type", "FILE"),
                    "Length (Bytes)": item.get("length", 0),
                    "Replication": item.get("replication", 1),
                    "Modified": pd.Timestamp(item.get("modificationTime", 0), unit="ms").strftime("%Y-%m-%d %H:%M:%S")
                })
            st.dataframe(pd.DataFrame(file_records), use_container_width=True, hide_index=True)
