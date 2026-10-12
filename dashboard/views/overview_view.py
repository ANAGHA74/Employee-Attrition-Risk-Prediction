"""
Page 2: Overview Page.
Displays executive summary of employee attrition risk with KPI cards,
Department Risk comparison bar chart, Risk Distribution donut chart,
and Top 5 Highest-Risk employees table.
"""

import textwrap
from typing import Dict, Any
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from dashboard.components.top_header import render_top_header


def render_overview_page(display_df: pd.DataFrame, meta: Dict[str, Any]):
    """Render executive overview dashboard matching Panel 2 of the UI reference."""
    st.markdown('<div class="overview-page-marker"></div>', unsafe_allow_html=True)

    render_top_header(
        title="Overview",
        subtitle="Executive summary of employee attrition risk based on latest data and model predictions.",
        last_updated=meta.get("last_updated", "Live")
    )

    if display_df.empty:
        st.warning("⚠️ No employee records available. Please ensure data is loaded from HDFS or clean records.")
        return

    # Extract metrics
    total_analyzed = meta.get("total_analyzed", len(display_df))
    hr_review_count = meta.get("hr_review_count", 0)
    hr_review_pct = meta.get("hr_review_pct", 0.0)
    avg_predicted_risk = meta.get("avg_predicted_risk", 0.0)
    departments = meta.get("departments", [])
    dept_str = ", ".join(departments) if departments else "3 Departments"

    # KPI Row (4 Cards)
    k1, k2, k3, k4 = st.columns(4, gap="medium")

    with k1:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-label">Employees analyzed</span>
                    <div class="kpi-icon-wrap kpi-icon-blue">👤</div>
                </div>
                <div class="kpi-value">{total_analyzed:,}</div>
                <div class="kpi-subtext">Unique employee records</div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with k2:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card" style="border-left: 3px solid #DC2626;">
                <div class="kpi-card-header">
                    <span class="kpi-label">HR review required</span>
                    <div class="kpi-icon-wrap kpi-icon-red">⚠️</div>
                </div>
                <div class="kpi-value kpi-value-red">{hr_review_count:,}</div>
                <div class="kpi-subtext">
                    <span style="font-weight: 700; color: #DC2626;">({hr_review_pct:.1f}%)</span> of analyzed employees
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with k3:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-label">Average predicted risk</span>
                    <div class="kpi-icon-wrap kpi-icon-amber">📈</div>
                </div>
                <div class="kpi-value">{avg_predicted_risk:.1f}%</div>
                <div class="kpi-subtext">Mean model probability</div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with k4:
        st.markdown(
            textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-label">Departments analyzed</span>
                    <div class="kpi-icon-wrap kpi-icon-purple">🏢</div>
                </div>
                <div class="kpi-value">{len(departments)}</div>
                <div class="kpi-subtext" style="font-size: 0.76rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{dept_str}">
                    {dept_str}
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3 Column Visual Layout matching Panel 2
    c_left, c_mid, c_right = st.columns([1.15, 1.15, 1.25], gap="medium")

    # Card 1: Department Risk Comparison
    with c_left:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Department Risk Comparison</div>
                <div class="card-subtitle">Average predicted attrition probability per department</div>
                """),
                unsafe_allow_html=True
            )
            dept_risk = display_df.groupby("Department", as_index=False)["AttritionProbability"].mean()
            dept_risk["RiskPercent"] = dept_risk["AttritionProbability"] * 100
            dept_risk = dept_risk.sort_values("RiskPercent", ascending=True)

            fig, ax = plt.subplots(figsize=(4.8, 3.0), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            y_pos = range(len(dept_risk))
            bars = ax.barh(y_pos, dept_risk["RiskPercent"], color="#2563EB", height=0.48, edgecolor="none", zorder=3)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(dept_risk["Department"], fontsize=9.2, fontweight="600", color="#1E293B")
            ax.set_xlim(0, 100)
            ax.set_xlabel("Average predicted probability", fontsize=8.2, color="#64748B", labelpad=6)
            ax.xaxis.set_major_formatter(lambda x, _: f"{int(x)}%")
            ax.tick_params(colors="#64748B", labelsize=8.2)

            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")

            for bar, val in zip(bars, dept_risk["RiskPercent"]):
                ax.text(
                    val + 2.5,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    va="center", ha="left",
                    fontsize=8.8, fontweight="700", color="#1E293B"
                )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()
    # Card 2: Risk Distribution Donut Chart
    with c_mid:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Risk Distribution</div>
                <div class="card-subtitle">Headcount categorized by predictive risk tier</div>
                """),
                unsafe_allow_html=True
            )

            low_c = meta.get("low_count", 0)
            med_c = meta.get("med_count", 0)
            high_c = meta.get("high_count", 0)

            counts = [low_c, med_c, high_c]
            colors = ["#10B981", "#F59E0B", "#EF4444"]

            fig, ax = plt.subplots(figsize=(4.7, 2.65), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            wedges, _ = ax.pie(
                counts,
                colors=colors,
                startangle=90,
                wedgeprops=dict(width=0.38, edgecolor="#FFFFFF", linewidth=3)
            )

            ax.text(
                0, 0.08,
                f"{total_analyzed}",
                ha="center", va="center",
                fontsize=18, fontweight="800", color="#0F172A"
            )
            ax.text(
                0, -0.16,
                "Employees",
                ha="center", va="center",
                fontsize=8.2, fontweight="600", color="#64748B"
            )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

            legend_html = textwrap.dedent(f"""
            <div class="overview-risk-legend" style="margin-bottom: 10px;">
                <div>
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
                    <span style="font-weight: 600; color: #1E293B;">Low: {low_c} ({meta.get('low_pct', 0):.1f}%)</span>
                </div>
                <div>
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #F59E0B; display: inline-block;"></span>
                    <span style="font-weight: 600; color: #1E293B;">Med: {med_c} ({meta.get('med_pct', 0):.1f}%)</span>
                </div>
                <div>
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #EF4444; display: inline-block;"></span>
                    <span style="font-weight: 600; color: #1E293B;">High: {high_c} ({meta.get('high_pct', 0):.1f}%)</span>
                </div>
            </div>
            """)
            st.markdown(legend_html, unsafe_allow_html=True)
    # Card 3: Top 5 Highest-Risk Employees
    with c_right:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Top 5 Highest-Risk Employees</div>
                <div class="card-subtitle">Urgent candidate cohort requiring immediate retention dialogue</div>
                """),
                unsafe_allow_html=True
            )

            top_5_df = meta.get("top_5", pd.DataFrame())
            if not top_5_df.empty:
                rows_html = "".join([
                    f"<tr style='border-bottom: 1px solid #F1F5F9;'>"
                    f"<td style='padding: 8px 6px; font-weight: 700; color: #0F172A;'>{r.get('EmployeeNumber')}</td>"
                    f"<td style='padding: 8px 6px; color: #334155; font-size: 0.8rem;'>{r.get('Department')}</td>"
                    f"<td style='padding: 8px 6px; color: #475569; font-size: 0.8rem;'>{r.get('JobRole')}</td>"
                    f"<td style='padding: 8px 6px; text-align: right;'><span class='badge badge-high'>{r.get('RiskPercent', 0.0):.1f}%</span></td>"
                    f"</tr>"
                    for _, r in top_5_df.iterrows()
                ])
                table_html = (
                    f"<div class='overview-table-scroll'>"
                    f"<table style='width: 100%; border-collapse: collapse; font-size: 0.83rem; text-align: left;'>"
                    f"<thead><tr style='border-bottom: 2px solid #E2E8F0; color: #64748B; font-size: 0.74rem; text-transform: uppercase;'>"
                    f"<th style='padding: 6px 6px;'>ID</th>"
                    f"<th style='padding: 6px 6px;'>Department</th>"
                    f"<th style='padding: 6px 6px;'>Job Role</th>"
                    f"<th style='padding: 6px 6px; text-align: right;'>Risk %</th>"
                    f"</tr></thead>"
                    f"<tbody>{rows_html}</tbody>"
                    f"</table></div>"
                )
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.info("No high-risk records detected.")

            st.markdown(
                textwrap.dedent(f"""
                <div style="margin-top: 1.15rem; font-size: 0.78rem; color: #64748B; border-top: 1px solid #F1F5F9; padding-top: 8px;">
                    💡 Threshold for HR Review is <strong>>= {meta.get('threshold', 0.60):.2f}</strong>.
                </div>
                """),
                unsafe_allow_html=True
            )
