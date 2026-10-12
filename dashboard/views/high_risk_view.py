"""
Page 4: High-Risk Employees (Action List) Page.
Searchable, sortable employee action list table with department and risk filters,
styled risk badges, interactive Employee Details panel, CSV export,
and neutral HR follow-up recommendations.
"""

import textwrap
from html import escape
from typing import Dict, Any
import pandas as pd
import streamlit as st

from dashboard.components.top_header import render_top_header

RISK_ORDER = ["HIGH", "MEDIUM", "LOW"]


def style_risk_cells(val):
    """Style risk values with clean badge colors."""
    if val == "HIGH":
        return "background-color: #FEE2E2; color: #DC2626; font-weight: 700;"
    elif val == "MEDIUM":
        return "background-color: #FEF3C7; color: #D97706; font-weight: 700;"
    elif val == "LOW":
        return "background-color: #DCFCE7; color: #16A34A; font-weight: 700;"
    elif val == "YES":
        return "background-color: #FEE2E2; color: #DC2626; font-weight: 700;"
    elif val == "NO":
        return "background-color: #F1F5F9; color: #64748B; font-weight: 600;"
    return ""


def render_high_risk_page(display_df: pd.DataFrame, meta: Dict[str, Any]):
    """Render High-Risk Employees Action List matching Panel 4 of the UI reference."""
    st.markdown('<div class="high-risk-page-marker"></div>', unsafe_allow_html=True)

    render_top_header(
        title="High-Risk Employees",
        subtitle=f"Employees with predicted attrition probability >= {meta.get('threshold', 0.60):.2f} who may require immediate HR attention.",
        last_updated=meta.get("last_updated", "Live")
    )

    if display_df.empty:
        st.warning("⚠️ No employee records available.")
        return

    # Filter Toolbar
    st.markdown('<div class="high-risk-filter-marker"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        t1, t2, t3, t4 = st.columns([1.10, 1.50, 0.85, 1.25], gap="small")

        with t1:
            search_query = st.text_input(
                "Search Employee",
                placeholder="Search by employee ID, department, or job role...",
                label_visibility="collapsed"
            )

        with t2:
            all_depts = sorted(display_df["Department"].dropna().unique().tolist())
            selected_depts = st.multiselect(
                "Department",
                options=all_depts,
                default=all_depts,
                placeholder="Select department...",
                label_visibility="collapsed"
            )

        with t3:
            risk_filter = st.multiselect(
                "Risk Level",
                options=RISK_ORDER,
                default=["HIGH"],
                placeholder="Risk Level",
                label_visibility="collapsed"
            )

        with t4:
            sort_choice = st.selectbox(
                    "Sort by",
                [
                    "Risk: High to Low",
                    "Risk: Low to High",
                    "Monthly Income: High to Low",
                    "Years at Company: High to Low",
                    "Employee ID"
                ],
                label_visibility="collapsed"
            )

    # Filter logic
    filtered = display_df.copy()

    if selected_depts:
        filtered = filtered[filtered["Department"].isin(selected_depts)]

    if risk_filter:
        filtered = filtered[filtered["RiskLevel"].isin(risk_filter)]

    if search_query:
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["EmployeeNumber"].astype(str).str.contains(q, case=False, na=False) |
            filtered["JobRole"].astype(str).str.lower().str.contains(q, na=False) |
            filtered["Department"].astype(str).str.lower().str.contains(q, na=False)
        ]

    # Sort logic
    sort_map = {
        "Risk: High to Low": ("AttritionProbability", False),
        "Risk: Low to High": ("AttritionProbability", True),
        "Monthly Income: High to Low": ("MonthlyIncome", False),
        "Years at Company: High to Low": ("YearsAtCompany", False),
        "Employee ID": ("EmployeeNumber", True)
    }
    col_name, asc = sort_map[sort_choice]
    if col_name in filtered.columns:
        filtered = filtered.sort_values(col_name, ascending=asc)

    # Split Layout: Table (65%) + Employee Details Panel (35%)
    col_table, col_details = st.columns([1.18, 0.95], gap="medium")

    with col_table:
        with st.container(border=True):
            st.markdown('<div class="high-risk-table-card-marker"></div>', unsafe_allow_html=True)
            # Table action bar
            sub1, sub2 = st.columns([1.25, 0.75])
            with sub1:
                st.markdown(
                    textwrap.dedent(f"""
                    <div style="font-size: 0.88rem; font-weight: 600; color: #475569; display: flex; align-items: center; min-height: 38px;">
                        Showing&nbsp;<strong>{len(filtered)}</strong>&nbsp;matching employee records
                    </div>
                    """),
                    unsafe_allow_html=True
                )
            with sub2:
                csv_export = filtered.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_export,
                    file_name="high_risk_employees_action_list.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )

            table_cols = [
                "EmployeeNumber", "RiskPercent", "RiskLevel", "HRReview",
                "Department", "JobRole", "OverTime", "MonthlyIncome",
                "YearsAtCompany", "JobSatisfaction"
            ]
            available_cols = [c for c in table_cols if c in filtered.columns]

            clean_table = filtered[available_cols].rename(columns={
                "EmployeeNumber": "ID",
                "RiskPercent": "Risk %",
                "RiskLevel": "Risk Level",
                "HRReview": "HR Review",
                "MonthlyIncome": "Monthly Income",
                "YearsAtCompany": "Years",
                "JobSatisfaction": "Job Satisfaction"
            })

            table_headers = "".join([f"<th>{escape(str(col))}</th>" for col in clean_table.columns])
            table_rows = []
            for _, row in clean_table.iterrows():
                cells = []
                for col in clean_table.columns:
                    value = row[col]
                    cell_class = ""
                    if col == "Risk %":
                        value = f"{float(value):.1f}%"
                        cell_class = "cell-number"
                    elif col == "Monthly Income":
                        value = f"${float(value):,.0f}"
                        cell_class = "cell-number"
                    elif col in ("Risk Level", "HR Review"):
                        risk_value = str(value).upper()
                        cell_class = f"cell-status cell-{risk_value.lower()}"
                    elif isinstance(value, float):
                        value = f"{value:.1f}"
                        cell_class = "cell-number"
                    cells.append(f"<td class='{cell_class}'>{escape(str(value))}</td>")
                table_rows.append(f"<tr>{''.join(cells)}</tr>")

            st.markdown(
                textwrap.dedent(f"""
                <div class="high-risk-table-marker"></div>
                <div class="high-risk-table-scroll">
                    <table class="high-risk-employee-table">
                        <thead><tr>{table_headers}</tr></thead>
                        <tbody>{''.join(table_rows)}</tbody>
                    </table>
                </div>
                """),
                unsafe_allow_html=True
            )

    # Right side: Interactive Employee Details Drawer / Card
    with col_details:
        with st.container(border=True):
            st.markdown('<div class="high-risk-details-marker"></div>', unsafe_allow_html=True)
            if not filtered.empty:
                employee_list = filtered["EmployeeNumber"].tolist()
                selected_emp_id = st.selectbox(
                    "Select Employee to Inspect:",
                    options=employee_list,
                    format_func=lambda x: f"Employee #{x} ({filtered[filtered['EmployeeNumber'] == x]['JobRole'].iloc[0]})",
                    index=0
                )

                emp = filtered[filtered["EmployeeNumber"] == selected_emp_id].iloc[0]
                risk_pct = emp.get("RiskPercent", emp.get("AttritionProbability", 0) * 100)
                risk_tier = emp.get("RiskLevel", "HIGH")
                tier_class = "badge-high" if risk_tier == "HIGH" else ("badge-medium" if risk_tier == "MEDIUM" else "badge-low")

                header_html = textwrap.dedent(f"""
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 0.85rem; margin-bottom: 0.85rem; padding-bottom: 0.75rem; border-bottom: 1px solid #F1F5F9;">
                    <div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #3B82F6, #1D4ED8); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0;">👤</div>
                    <div style="flex: 1;">
                        <div style="font-size: 1.05rem; font-weight: 750; color: #0F172A; display: flex; align-items: center; gap: 8px;">
                            <span>Employee #{emp.get('EmployeeNumber')}</span>
                            <span class="badge {tier_class}">{risk_tier} RISK</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #64748B;">{emp.get('JobRole', 'N/A')} • {emp.get('Department', 'N/A')}</div>
                    </div>
                </div>

                <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <span style="font-size: 0.84rem; font-weight: 600; color: #991B1B;">Predicted Attrition Risk</span>
                    <span style="font-size: 1.35rem; font-weight: 800; color: #DC2626;">{risk_pct:.1f}%</span>
                </div>
                """)
                st.markdown(header_html, unsafe_allow_html=True)

                tab_prof, tab_factors, tab_rec = st.tabs(["👤 Profile", "🔍 Key Factors", "📋 HR Recommendations"])

                with tab_prof:
                    grid_html = textwrap.dedent(f"""
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 0.75rem;">
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Department</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{emp.get('Department', 'N/A')}</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Job Role</div>
                            <div style="font-size: 0.78rem; font-weight: 700; color: #0F172A;">{emp.get('JobRole', 'N/A')}</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">OverTime</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{emp.get('OverTime', 'N/A')}</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Monthly Income</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">${emp.get('MonthlyIncome', 0):,}</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Years at Company</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{emp.get('YearsAtCompany', 'N/A')} yrs</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Job Satisfaction</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{emp.get('JobSatisfaction', 'N/A')} / 4</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Education Field</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{emp.get('EducationField', 'N/A')}</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px;">
                            <div style="font-size: 0.70rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Marital Status</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{emp.get('MaritalStatus', 'N/A')}</div>
                        </div>
                    </div>
                    """)
                    st.markdown(grid_html, unsafe_allow_html=True)

                with tab_factors:
                    factors = []
                    if emp.get("OverTime") == "Yes":
                        factors.append(("OverTime = Yes", "High positive coefficient with attrition risk"))
                    if emp.get("BusinessTravel") == "Travel_Frequently":
                        factors.append(("Frequent Business Travel", "Correlated with employee travel fatigue"))
                    if emp.get("JobSatisfaction", 4) <= 2:
                        factors.append(("Low Job Satisfaction", f"Rating {emp.get('JobSatisfaction')} out of 4"))
                    if emp.get("YearsSinceLastPromotion", 0) >= 3:
                        factors.append(("Years Since Promotion", f"{emp.get('YearsSinceLastPromotion')} years without promotion"))
                    if emp.get("MaritalStatus") == "Single":
                        factors.append(("Marital Status Single", "Statistically higher mobility in trained pipeline"))

                    if factors:
                        for f_title, f_desc in factors:
                            factor_html = textwrap.dedent(f"""
                            <div style="background: #F8FAFC; border-left: 3px solid #EF4444; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px;">
                                <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">{f_title}</div>
                                <div style="font-size: 0.74rem; color: #64748B;">{f_desc}</div>
                            </div>
                            """)
                            st.markdown(factor_html, unsafe_allow_html=True)
                    else:
                        st.caption("Standard feature distributions observed.")

                with tab_rec:
                    rec_html = textwrap.dedent("""
                    <div style="background-color: #FEF2F2; border: 1px solid #FCA5A5; border-left: 4px solid #DC2626; border-radius: 8px; padding: 10px 12px; margin-bottom: 10px;">
                        <div style="font-size: 0.84rem; font-weight: 750; color: #991B1B; display: flex; align-items: center; gap: 6px; margin-bottom: 3px;">
                            <span>⚠️</span>
                            <span>Recommendation for HR</span>
                        </div>
                        <div style="font-size: 0.80rem; color: #7F1D1D; line-height: 1.45;">
                            This employee has a high predicted attrition risk. Consider scheduling a confidential one-on-one conversation to understand workload, engagement, and career development concerns.
                        </div>
                    </div>
                    """)
                    st.markdown(rec_html, unsafe_allow_html=True)

                    st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px;'>Suggested Action Prompts:</div>", unsafe_allow_html=True)
                    actions = ["Conduct an open, non-judgmental stay interview focusing on career goals."]
                    if emp.get("OverTime") == "Yes":
                        actions.append("Review workload distribution, overtime schedule, and team capacity support.")
                    if emp.get("JobSatisfaction", 4) <= 2:
                        actions.append("Explore specific workplace pain points affecting daily job satisfaction.")
                    if emp.get("YearsSinceLastPromotion", 0) >= 3:
                        actions.append("Evaluate internal promotion pathways, skill expansion, or new responsibilities.")

                    for act in actions:
                        st.markdown(f"<div style='font-size: 0.78rem; color: #475569; margin-bottom: 3px;'>• {act}</div>", unsafe_allow_html=True)
            else:
                st.info("No employee record selected.")
