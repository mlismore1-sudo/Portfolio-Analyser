import io
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.file_parser import parse_uploaded_holdings
from utils.identifier_resolution import resolve_identifiers
from utils.analytics import (
    calculate_asset_allocation,
    calculate_region_allocation,
    calculate_portfolio_trailing_returns,
)
from utils.exports import dataframe_to_csv_bytes

st.set_page_config(page_title="Investment Portfolio Analysis Tool", layout="wide")

st.title("Investment Portfolio Analysis Tool")
st.caption("Upload holdings, confirm extraction, then generate allocation, return, and geographic insights.")

uploaded_file = st.file_uploader(
    "Upload holdings CSV",
    type=["csv"],
    help="Upload a CSV containing Ticker / ISIN / SEDOL, Description, and GBP value."
)

if "parsed_df" not in st.session_state:
    st.session_state.parsed_df = None
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

if uploaded_file is not None:
    try:
        parsed_df = parse_uploaded_holdings(uploaded_file)
        st.session_state.parsed_df = parsed_df
        st.subheader("Step 1: Confirm extracted holdings")
        st.dataframe(parsed_df, use_container_width=True)

        if st.button("Confirm extraction"):
            st.session_state.confirmed = True

    except Exception as e:
        st.error(f"Could not parse file: {e}")

if st.session_state.confirmed and st.session_state.parsed_df is not None:
    st.subheader("Step 2: Resolve identifiers and enrich holdings")

    enriched_df = resolve_identifiers(st.session_state.parsed_df)

    st.dataframe(enriched_df, use_container_width=True)

    unresolved = enriched_df[enriched_df["match_status"] != "Matched"]
    if not unresolved.empty:
        st.warning(
            f"{len(unresolved)} holding(s) are unresolved or ambiguous. "
            "They will be excluded from return calculations unless manually mapped."
        )

    st.subheader("Step 3: Portfolio insights")

    asset_alloc_df = calculate_asset_allocation(enriched_df)
    region_alloc_df = calculate_region_allocation(enriched_df)
    returns_df = calculate_portfolio_trailing_returns(enriched_df)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Asset allocation")
        fig_asset = px.pie(
            asset_alloc_df,
            names="asset_class",
            values="gbp_value",
            hole=0.45
        )
        st.plotly_chart(fig_asset, use_container_width=True)
        st.dataframe(asset_alloc_df, use_container_width=True)

    with col2:
        st.markdown("### Geographic allocation")
        fig_region = px.bar(
            region_alloc_df,
            x="region",
            y="gbp_value",
            text="weight_pct"
        )
        fig_region.update_traces(texttemplate="%{text:.2f}%")
        st.plotly_chart(fig_region, use_container_width=True)
        st.dataframe(region_alloc_df, use_container_width=True)

    st.markdown("### Trailing returns")
    st.dataframe(returns_df, use_container_width=True)

    st.download_button(
        label="Download enriched holdings CSV",
        data=dataframe_to_csv_bytes(enriched_df),
        file_name="enriched_holdings.csv",
        mime="text/csv",
    )

    st.download_button(
        label="Download asset allocation CSV",
        data=dataframe_to_csv_bytes(asset_alloc_df),
        file_name="asset_allocation.csv",
        mime="text/csv",
    )

    st.download_button(
        label="Download geographic allocation CSV",
        data=dataframe_to_csv_bytes(region_alloc_df),
        file_name="geographic_allocation.csv",
        mime="text/csv",
    )

    st.download_button(
        label="Download trailing returns CSV",
        data=dataframe_to_csv_bytes(returns_df),
        file_name="trailing_returns.csv",
        mime="text/csv",
    )
