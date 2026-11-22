import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bitcoin Traffic Monitor",
    page_icon="₿",
    layout="wide"
)


# =========================================================
# HOME PAGE
# =========================================================

st.title("₿ Bitcoin Traffic Analytics")

st.subheader(
    "AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic"
)

st.write(
    """
    Offline blockchain and network analytics platform for
    transaction analysis, entity correlation, anomaly detection,
    behavioral clustering, risk scoring and explainable
    investigative leads.
    """
)

st.divider()

st.info(
    "Use the navigation panel on the left to import data, "
    "inspect the analysis, investigate entities and generate reports."
)

st.markdown(
    """
    ### Workflow

    **Import Data → Data Quality → Correlation → Entity Graph
    → AI/ML Analysis → Alerts & Risk → Reports**
    """
)