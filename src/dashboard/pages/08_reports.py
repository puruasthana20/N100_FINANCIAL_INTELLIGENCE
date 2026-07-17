import streamlit as st
import pandas as pd
import requests

from src.dashboard.utils.db import (
    get_companies,
    _read_sql,
)

st.set_page_config(
    page_title="Annual Reports",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Annual Reports")
st.caption(
    "Browse historical annual reports available from BSE."
)

# ==========================================================
# Load Companies
# ==========================================================

companies = get_companies()

company_map = dict(
    zip(
        companies["company_name"],
        companies["company_id"],
    )
)

selected_company = st.selectbox(
    "Select Company",
    companies["company_name"].tolist(),
)

ticker = company_map[selected_company]

# ==========================================================
# Load Reports
# ==========================================================

reports = _read_sql(
    """
    SELECT
        company_id,
        year,
        annual_report
    FROM documents
    WHERE company_id=?
    ORDER BY year DESC
    """,
    [ticker],
)

if reports.empty:
    st.warning("No annual reports available.")
    st.stop()

st.success(
    f"{len(reports)} reports found."
)

st.divider()

# ==========================================================
# Report Availability
# ==========================================================

st.subheader("Available Reports")

status = []

with st.spinner("Checking report availability..."):

    for _, row in reports.iterrows():

        url = row["annual_report"]

        available = False

        try:

            response = requests.head(
                url,
                allow_redirects=True,
                timeout=5,
            )

            if response.status_code == 200:
                available = True

        except Exception:
            available = False

        status.append(available)

reports["available"] = status

# ==========================================================
# Display Reports
# ==========================================================

for _, row in reports.iterrows():

    c1, c2, c3 = st.columns([2, 2, 2])

    c1.write(f"**{row['year']}**")

    if row["available"]:

        c2.success("Available")

        c3.markdown(
            f"[📥 Open Report]({row['annual_report']})"
        )

    else:

        c2.error("Report Unavailable")

        c3.write("-")

st.divider()

# ==========================================================
# Report Table
# ==========================================================

table = reports.copy()

table = table.rename(
    columns={
        "year": "Year",
        "annual_report": "Report URL",
        "available": "Available",
    }
)

st.subheader("Report Database")

st.dataframe(
    table[
        [
            "Year",
            "Available",
            "Report URL",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

# ==========================================================
# Download
# ==========================================================

st.download_button(
    "📥 Download Report List",
    table.to_csv(index=False),
    file_name=f"{ticker}_annual_reports.csv",
    mime="text/csv",
)

st.divider()

st.caption(
    "Annual Reports Dashboard • BSE Report Repository"
)