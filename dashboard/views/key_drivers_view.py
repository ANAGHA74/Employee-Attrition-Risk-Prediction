"""
Page 5: Key Attrition Drivers Page.
Visualizes top model features increasing and reducing predicted attrition risk
with side-by-side horizontal coefficient charts, interpretation guidance,
and model metadata matching Panel 5 of the UI reference.
"""

import textwrap
from typing import Dict, Any
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from dashboard.components.top_header import render_top_header
from dashboard.data_loader import load_model_coefficients


def render_key_drivers_page(meta: Dict[str, Any]):
    """Render Key Attrition Drivers dashboard matching Panel 5 of the UI reference."""
    st.markdown('<div class="key-drivers-page-marker"></div>', unsafe_allow_html=True)

    render_top_header(
        title="Key Attrition Drivers",
        subtitle="Top model features associated with higher or lower predicted attrition risk.",
        last_updated=meta.get("last_updated", "Live")
    )

    coeff_df = load_model_coefficients()

    if coeff_df.empty:
        st.warning("⚠️ Feature coefficients file not found at `ml/results/feature_coefficients.csv`. Please train the model to generate feature coefficients.")
        return

    # Filter into positive (risk increasing) and negative (risk reducing)
    pos_factors = coeff_df[coeff_df["Coefficient"] > 0].sort_values("Coefficient", ascending=False).head(5)
    neg_factors = coeff_df[coeff_df["Coefficient"] < 0].sort_values("Coefficient", ascending=True).head(5)

    c_pos, c_neg = st.columns(2, gap="large")

    # Chart 1: Top Factors Increasing Attrition Risk
    with c_pos:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Top Factors Increasing Attrition Risk</div>
                <div class="card-subtitle">Features with strongest positive association with departure</div>
                """),
                unsafe_allow_html=True
            )

            fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            pos_plot = pos_factors.sort_values("Coefficient", ascending=True)
            y_pos = range(len(pos_plot))
            bars = ax.barh(y_pos, pos_plot["Coefficient"], color="#F87171", height=0.48, zorder=3)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(pos_plot["ReadableFeature"], fontsize=8.6, fontweight="600", color="#1E293B")
            ax.set_xlabel("Model Coefficient (Higher = Greater Risk)", fontsize=8.2, color="#64748B", labelpad=6)
            max_pos = pos_factors["Coefficient"].max()
            ax.set_xlim(0, max_pos * 1.25)
            ax.tick_params(colors="#64748B", labelsize=8.2)
            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")

            for bar, val in zip(bars, pos_plot["Coefficient"]):
                ax.text(
                    val + 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.4f}",
                    va="center", ha="left",
                    fontsize=8.5, fontweight="700", color="#991B1B"
                )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

    # Chart 2: Top Factors Reducing Attrition Risk
    with c_neg:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent("""
                <div class="card-title">Top Factors Reducing Attrition Risk</div>
                <div class="card-subtitle">Features with strongest negative association with departure</div>
                """),
                unsafe_allow_html=True
            )

            fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=140)
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#FFFFFF")

            neg_plot = neg_factors.sort_values("Coefficient", ascending=False)
            y_pos = range(len(neg_plot))
            bars = ax.barh(y_pos, neg_plot["Coefficient"], color="#34D399", height=0.48, zorder=3)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(neg_plot["ReadableFeature"], fontsize=8.6, fontweight="600", color="#1E293B")
            ax.set_xlabel("Model Coefficient (More Negative = Lower Risk)", fontsize=8.2, color="#64748B", labelpad=6)
            min_neg = neg_factors["Coefficient"].min()
            ax.set_xlim(min_neg * 1.25, 0)
            ax.tick_params(colors="#64748B", labelsize=8.2)
            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
            ax.spines["top"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["right"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")

            for bar, val in zip(bars, neg_plot["Coefficient"]):
                ax.text(
                    val - 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.4f}",
                    va="center", ha="right",
                    fontsize=8.5, fontweight="700", color="#065F46"
                )

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Full Feature Coefficients Table Expander
    with st.expander("🔍 View Complete Feature Coefficients Table"):
        display_coeffs = coeff_df[["ReadableFeature", "Coefficient", "AbsoluteCoefficient"]].sort_values(
            "AbsoluteCoefficient", ascending=False
        ).rename(columns={
            "ReadableFeature": "Feature Name",
            "AbsoluteCoefficient": "Impact Magnitude"
        })
        st.dataframe(
            display_coeffs.style.format({
                "Coefficient": "{:.4f}",
                "Impact Magnitude": "{:.4f}"
            }),
            use_container_width=True,
            hide_index=True
        )
