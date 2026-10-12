"""
Page 3: Risk Analytics & Demographics Page.
Interactive workforce factor analytics with dynamic multi-dimensional filters,
Risk Distribution, Risk by Department, OverTime boxplot, Income vs Risk,
and Years at Company vs Risk.
"""

import textwrap
from typing import Dict, Any
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from dashboard.components.top_header import render_top_header

RISK_PALETTE = {"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#EF4444"}
RISK_ORDER = ["LOW", "MEDIUM", "HIGH"]


def render_risk_analytics_page(display_df: pd.DataFrame, meta: Dict[str, Any]):
    """Render Risk Analytics & Demographics dashboard matching Panel 3 of the UI reference."""
    st.markdown('<div class="risk-analytics-page-marker"></div>', unsafe_allow_html=True)

    render_top_header(
        title="Risk Analytics & Demographics",
        subtitle="Explore employee attrition risk across departments, job roles, and key workforce factors.",
        last_updated=meta.get("last_updated", "Live")
    )

    if display_df.empty:
        st.warning("⚠️ No data available for analytics.")
        return

    # Filters Toolbar inside a clean container
    with st.container(border=True):
        f_col1, f_col2, f_col3 = st.columns([1.2, 1.4, 1.1])

        with f_col1:
            dept_options = ["All"] + sorted(display_df["Department"].dropna().unique().tolist())
            sel_dept = st.selectbox("Department", dept_options, index=0)

        with f_col2:
            roles_avail = display_df["JobRole"].dropna().unique().tolist()
            if sel_dept != "All":
                roles_avail = display_df[display_df["Department"] == sel_dept]["JobRole"].dropna().unique().tolist()
            role_options = ["All"] + sorted(roles_avail)
            sel_role = st.selectbox("Job Role", role_options, index=0)

        with f_col3:
            risk_options = ["All", "HIGH", "MEDIUM", "LOW"]
            sel_risk = st.selectbox("Risk Level", risk_options, index=0)

    # Filter Dataset
    filtered = display_df.copy()
    if sel_dept != "All":
        filtered = filtered[filtered["Department"] == sel_dept]
    if sel_role != "All":
        filtered = filtered[filtered["JobRole"] == sel_role]
    if sel_risk != "All":
        filtered = filtered[filtered["RiskLevel"] == sel_risk]

    if filtered.empty:
        st.info("ℹ️ No records match the selected filter combination. Displaying full workforce cohort below.")
        filtered = display_df.copy()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Row 1: Risk Distribution & Risk by Department
    r1_left, r1_right = st.columns(2, gap="medium")

    with r1_left:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Risk Distribution</div>
                <div class="card-subtitle">Headcount distribution by model-assigned risk category</div>
                """),
                unsafe_allow_html=True
            )

            fig, ax = plt.subplots(figsize=(6.0, 3.4), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            risk_counts = filtered["RiskLevel"].value_counts().reindex(RISK_ORDER).fillna(0)
            bars = ax.bar(risk_counts.index, risk_counts.values, color=[RISK_PALETTE[r] for r in RISK_ORDER], width=0.50, zorder=3)

            ax.set_ylabel("Employees", fontsize=8.8, color="#64748B")
            ax.tick_params(colors="#1E293B", labelsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")

            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + (max(risk_counts.values) * 0.03 + 0.5),
                    f"{int(height)}",
                    ha="center", va="bottom",
                    fontsize=9.2, fontweight="700", color="#0F172A"
                )

            if max(risk_counts.values) > 0:
                ax.set_ylim(0, max(risk_counts.values) * 1.18)

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

    with r1_right:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Risk by Department</div>
                <div class="card-subtitle">Average predicted attrition probability across business units</div>
                """),
                unsafe_allow_html=True
            )

            dept_avg = filtered.groupby("Department", as_index=False)["AttritionProbability"].mean()
            dept_avg["RiskPct"] = dept_avg["AttritionProbability"] * 100
            dept_avg = dept_avg.sort_values("RiskPct", ascending=False)

            fig, ax = plt.subplots(figsize=(6.0, 3.4), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            bars = ax.bar(dept_avg["Department"], dept_avg["RiskPct"], color="#2563EB", width=0.46, zorder=3)

            ax.set_ylabel("Avg predicted probability", fontsize=8.8, color="#64748B")
            ax.set_ylim(0, 100)
            ax.yaxis.set_major_formatter(lambda y, _: f"{int(y)}%")
            ax.tick_params(colors="#1E293B", labelsize=8.6)
            ax.grid(axis="y", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")

            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 2.5,
                    f"{height:.1f}%",
                    ha="center", va="bottom",
                    fontsize=9.0, fontweight="700", color="#0F172A"
                )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Row 2: OverTime vs Risk, Monthly Income vs Risk, Years at Company vs Risk
    r2_1, r2_2, r2_3 = st.columns(3, gap="medium")

    with r2_1:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">OverTime vs Risk</div>
                <div class="card-subtitle">Attrition probability comparison by overtime status</div>
                """),
                unsafe_allow_html=True
            )

            if "OverTime" in filtered.columns:
                fig, ax = plt.subplots(figsize=(4.5, 3.4), dpi=140)
                fig.patch.set_facecolor("#FFFFFF")
                ax.set_facecolor("#FFFFFF")

                sns.boxplot(
                    data=filtered,
                    x="OverTime",
                    y="AttritionProbability",
                    order=["No", "Yes"],
                    palette={"No": "#60A5FA", "Yes": "#F87171"},
                    ax=ax,
                    width=0.40,
                    boxprops=dict(alpha=0.85)
                )

                ax.set_xlabel("OverTime Status", fontsize=8.5, color="#64748B")
                ax.set_ylabel("Predicted probability", fontsize=8.5, color="#64748B")
                ax.set_ylim(0, 1.05)
                ax.yaxis.set_major_formatter(lambda y, _: f"{int(y*100)}%")
                ax.tick_params(colors="#1E293B", labelsize=8.5)
                ax.grid(axis="y", linestyle="--", alpha=0.35, color="#CBD5E1")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close()
            else:
                st.caption("OverTime feature not available in active slice.")

    with r2_2:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Monthly Income vs Risk</div>
                <div class="card-subtitle">Compensation correlation with model attrition risk</div>
                """),
                unsafe_allow_html=True
            )

            if "MonthlyIncome" in filtered.columns:
                fig, ax = plt.subplots(figsize=(4.5, 3.4), dpi=140)
                fig.patch.set_facecolor("#FFFFFF")
                ax.set_facecolor("#FFFFFF")

                for risk_cat in RISK_ORDER:
                    sub = filtered[filtered["RiskLevel"] == risk_cat]
                    if not sub.empty:
                        ax.scatter(
                            sub["MonthlyIncome"],
                            sub["AttritionProbability"],
                            label=risk_cat,
                            color=RISK_PALETTE[risk_cat],
                            alpha=0.75,
                            edgecolor="none",
                            s=30
                        )

                ax.set_xlabel("Monthly Income ($)", fontsize=8.5, color="#64748B")
                ax.set_ylabel("Predicted probability", fontsize=8.5, color="#64748B")
                ax.set_ylim(0, 1.05)
                ax.yaxis.set_major_formatter(lambda y, _: f"{int(y*100)}%")
                ax.xaxis.set_major_formatter(lambda x, _: f"{int(x/1000)}k")
                ax.tick_params(colors="#1E293B", labelsize=8.2)
                ax.grid(True, linestyle="--", alpha=0.35, color="#CBD5E1")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.legend(title="Risk", fontsize=7.2, title_fontsize=7.8, frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0")

                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close()
            else:
                st.caption("MonthlyIncome feature not available.")

    with r2_3:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Years at Company vs Risk</div>
                <div class="card-subtitle">Tenure distribution against attrition probability</div>
                """),
                unsafe_allow_html=True
            )

            if "YearsAtCompany" in filtered.columns:
                fig, ax = plt.subplots(figsize=(4.5, 3.4), dpi=140)
                fig.patch.set_facecolor("#FFFFFF")
                ax.set_facecolor("#FFFFFF")

                for risk_cat in RISK_ORDER:
                    sub = filtered[filtered["RiskLevel"] == risk_cat]
                    if not sub.empty:
                        ax.scatter(
                            sub["YearsAtCompany"],
                            sub["AttritionProbability"],
                            label=risk_cat,
                            color=RISK_PALETTE[risk_cat],
                            alpha=0.75,
                            edgecolor="none",
                            s=30
                        )

                ax.set_xlabel("Years at Company", fontsize=8.5, color="#64748B")
                ax.set_ylabel("Predicted probability", fontsize=8.5, color="#64748B")
                ax.set_ylim(0, 1.05)
                ax.yaxis.set_major_formatter(lambda y, _: f"{int(y*100)}%")
                ax.tick_params(colors="#1E293B", labelsize=8.2)
                ax.grid(True, linestyle="--", alpha=0.35, color="#CBD5E1")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.legend(title="Risk", fontsize=7.2, title_fontsize=7.8, frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0")

                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close()
            else:
                st.caption("YearsAtCompany feature not available.")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Job Role comparison and Survey Scores
    c_role, c_survey = st.columns([1.3, 1.0], gap="medium")

    with c_role:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Job Role Risk Comparison</div>
                <div class="card-subtitle">Roles sorted by mean model attrition probability</div>
                """),
                unsafe_allow_html=True
            )

            role_risk = filtered.groupby("JobRole", as_index=False).agg(
                AvgRisk=("AttritionProbability", "mean"),
                Headcount=("EmployeeNumber", "count")
            ).sort_values("AvgRisk", ascending=True)

            fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            y_pos = range(len(role_risk))
            bars = ax.barh(y_pos, role_risk["AvgRisk"] * 100, color="#0EA5E9", height=0.50, zorder=3)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(role_risk["JobRole"], fontsize=8.2, fontweight="500", color="#1E293B")
            ax.set_xlim(0, 100)
            ax.xaxis.set_major_formatter(lambda x, _: f"{int(x)}%")
            ax.tick_params(colors="#64748B", labelsize=8.2)
            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            for bar, val in zip(bars, role_risk["AvgRisk"] * 100):
                ax.text(
                    val + 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    va="center", ha="left",
                    fontsize=8.2, fontweight="700", color="#0F172A"
                )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

    with c_survey:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Survey Sentiment Summary</div>
                <div class="card-subtitle">Mean sentiment ratings across risk categories (Scale 1-4)</div>
                """),
                unsafe_allow_html=True
            )

            survey_cols = ["JobSatisfaction", "EnvironmentSatisfaction", "JobInvolvement", "WorkLifeBalance"]
            available_survey = [c for c in survey_cols if c in filtered.columns]
            if available_survey:
                survey_summary = filtered.groupby("RiskLevel")[available_survey].mean().reindex(RISK_ORDER).dropna(how="all")
                survey_html = (
                    survey_summary
                    .style
                    .format("{:.2f}")
                    .background_gradient(cmap="Blues", axis=None)
                    .set_table_attributes('class="survey-sentiment-table"')
                    .to_html()
                )
                st.markdown(
                    f'<div class="survey-sentiment-scroll-marker"><div class="survey-sentiment-scroll">{survey_html}</div></div>',
                    unsafe_allow_html=True
                )
                st.caption("Scores range from 1 (Low) to 4 (Very High). Lower scores typically indicate elevated risk.")
            else:
                st.info("Survey metrics not found in active dataset.")
