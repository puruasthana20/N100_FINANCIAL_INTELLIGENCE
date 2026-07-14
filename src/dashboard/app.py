"""
============================================================
NIFTY 100 FINANCIAL INTELLIGENCE DASHBOARD

Sprint 4
Day 22 - Streamlit Application Entry Point
============================================================
"""

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📈 Nifty 100 Analytics")

st.sidebar.markdown(
    """
Welcome to the Nifty 100 Financial Intelligence Dashboard.

Use the navigation menu below to switch between dashboard pages.
"""
)

st.sidebar.info(
    "Sprint 4 • Dashboard & Valuation"
)


# ============================================================
# MAIN HEADER
# ============================================================

st.title("📈 Nifty 100 Financial Intelligence Dashboard")

st.caption(
    "Comprehensive Financial Analytics Platform for Nifty 100 Companies"
)


# ============================================================
# OVERVIEW
# ============================================================

st.markdown("---")

st.subheader("Dashboard Modules")

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        """
### 📊 Analytics

- Company Financial Profile
- Financial Screener
- Peer Comparison
- Trend Analysis
"""
    )

with col2:

    st.markdown(
        """
### 📁 Reports

- Sector Analysis
- Capital Allocation
- Annual Reports
- Valuation Summary
"""
    )


st.markdown("---")


# ============================================================
# PROJECT SUMMARY
# ============================================================

st.subheader("Project Overview")

st.write(
    """
This dashboard provides an interactive interface for analysing
financial performance of Nifty 100 companies.

The application includes:

• Financial ratio analysis

• Company profiling

• Rule-based stock screener

• Peer percentile comparison

• Sector analytics

• Capital allocation analysis

• Annual report explorer

• Valuation analysis
"""
)


# ============================================================
# SPRINT STATUS
# ============================================================

st.subheader("Current Project Status")

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:

    st.metric(
        "Companies",
        "100"
    )

with status_col2:

    st.metric(
        "Financial Ratios",
        "20+ KPIs"
    )

with status_col3:

    st.metric(
        "Peer Groups",
        "11"
    )

with status_col4:

    st.metric(
        "Sprint",
        "Sprint 4"
    )


st.markdown("---")


# ============================================================
# AVAILABLE PAGES
# ============================================================

st.subheader("Available Screens")

pages = [

    "🏠 Home",

    "🏢 Company Profile",

    "🔍 Screener",

    "👥 Peer Comparison",

    "📈 Trend Analysis",

    "🏭 Sector Analysis",

    "🌳 Capital Allocation",

    "📄 Annual Reports"

]

for page in pages:

    st.write(f"• {page}")


st.success(
    "Application initialized successfully."
)


st.info(
    "Use the Streamlit sidebar on the left to open any dashboard page."
)