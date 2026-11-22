import streamlit as st
import pandas as pd
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Data Quality",
    page_icon="🧹",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🧹 Data Quality & Validation")

st.write(
    """
    This page shows the quality of the dataset after ingestion,
    validation and cleaning.
    """
)


# =========================================================
# LOAD DATA
# =========================================================

cleaned_file = (
    PROCESSED_DIR
    / "bitcoin_transactions_cleaned.csv"
)


if not cleaned_file.exists():

    st.warning(
        "No cleaned dataset is available yet."
    )

    st.info(
        "Go to Import Data, upload a dataset, "
        "and run the analysis pipeline first."
    )

    st.stop()


df = pd.read_csv(
    cleaned_file
)


# =========================================================
# BASIC INFORMATION
# =========================================================

st.subheader("Dataset Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Records",
    f"{len(df):,}"
)

c2.metric(
    "Columns",
    len(df.columns)
)

c3.metric(
    "Duplicate TXIDs",
    int(
        df["txid"]
        .duplicated()
        .sum()
    )
)

c4.metric(
    "Missing Values",
    int(
        df.isna()
        .sum()
        .sum()
    )
)


# =========================================================
# REQUIRED COLUMN CHECK
# =========================================================

st.subheader(
    "Required Field Validation"
)

required_columns = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "txid",
    "input_addresses",
    "output_addresses",
    "input_amounts",
    "output_amounts",
    "fee",
    "script_type",
    "geo_country",
    "asn"
]

validation_results = []

for column in required_columns:

    exists = column in df.columns

    validation_results.append({
        "Field": column,
        "Status": (
            "PASS"
            if exists
            else "MISSING"
        )
    })


validation_df = pd.DataFrame(
    validation_results
)


st.dataframe(
    validation_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# MISSING VALUES BY COLUMN
# =========================================================

st.subheader(
    "Missing Values by Field"
)

missing_df = pd.DataFrame({
    "Field": df.columns,
    "Missing Values": [
        int(df[column].isna().sum())
        for column in df.columns
    ]
})


missing_df = missing_df.sort_values(
    "Missing Values",
    ascending=False
)


st.dataframe(
    missing_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DUPLICATE TRANSACTIONS
# =========================================================

st.subheader(
    "Duplicate Transaction IDs"
)

duplicate_count = int(
    df["txid"]
    .duplicated()
    .sum()
)


if duplicate_count == 0:

    st.success(
        "No duplicate TXIDs found."
    )

else:

    st.warning(
        f"{duplicate_count} duplicate TXIDs found."
    )

    duplicate_rows = df[
        df["txid"].duplicated(
            keep=False
        )
    ]

    st.dataframe(
        duplicate_rows,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# IP VALIDATION
# =========================================================

st.subheader(
    "IP Address Validation"
)


def validate_ip(value):

    from ipaddress import ip_address

    try:

        ip_address(
            str(value)
        )

        return True

    except ValueError:

        return False


src_invalid = (
    ~df["src_ip"]
    .apply(validate_ip)
).sum()


dst_invalid = (
    ~df["dst_ip"]
    .apply(validate_ip)
).sum()


c1, c2 = st.columns(2)

c1.metric(
    "Invalid Source IPs",
    int(src_invalid)
)

c2.metric(
    "Invalid Destination IPs",
    int(dst_invalid)
)


if src_invalid == 0 and dst_invalid == 0:

    st.success(
        "All source and destination IP addresses are valid."
    )

else:

    st.warning(
        "Invalid IP addresses were detected."
    )


# =========================================================
# PORT VALIDATION
# =========================================================

st.subheader(
    "Port Validation"
)


src_ports = pd.to_numeric(
    df["src_port"],
    errors="coerce"
)

dst_ports = pd.to_numeric(
    df["dst_port"],
    errors="coerce"
)


invalid_src_ports = (
    src_ports.isna()
    |
    (src_ports < 0)
    |
    (src_ports > 65535)
).sum()


invalid_dst_ports = (
    dst_ports.isna()
    |
    (dst_ports < 0)
    |
    (dst_ports > 65535)
).sum()


c1, c2 = st.columns(2)

c1.metric(
    "Invalid Source Ports",
    int(invalid_src_ports)
)

c2.metric(
    "Invalid Destination Ports",
    int(invalid_dst_ports)
)


# =========================================================
# TIMESTAMP VALIDATION
# =========================================================

st.subheader(
    "Timestamp Validation"
)


timestamps = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)


invalid_timestamps = int(
    timestamps.isna().sum()
)


st.metric(
    "Invalid Timestamps",
    invalid_timestamps
)


if invalid_timestamps == 0:

    st.success(
        "All timestamps are valid."
    )

else:

    st.warning(
        "Invalid timestamps were detected."
    )


# =========================================================
# NUMERIC VALIDATION
# =========================================================

st.subheader(
    "Numeric Field Validation"
)


numeric_fields = [
    "fee",
    "src_port",
    "dst_port"
]


numeric_results = []


for column in numeric_fields:

    if column not in df.columns:
        continue

    converted = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid = int(
        converted.isna().sum()
    )

    numeric_results.append({
        "Field": column,
        "Invalid Values": invalid,
        "Status": (
            "PASS"
            if invalid == 0
            else "CHECK"
        )
    })


numeric_df = pd.DataFrame(
    numeric_results
)


st.dataframe(
    numeric_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DATA QUALITY STATUS
# =========================================================

st.divider()

st.subheader(
    "Overall Data Quality"
)


required_ok = (
    validation_df["Status"]
    .eq("PASS")
    .all()
)

ips_ok = (
    src_invalid == 0
    and dst_invalid == 0
)

ports_ok = (
    invalid_src_ports == 0
    and invalid_dst_ports == 0
)

timestamps_ok = (
    invalid_timestamps == 0
)

duplicates_ok = (
    duplicate_count == 0
)


all_checks = (
    required_ok
    and ips_ok
    and ports_ok
    and timestamps_ok
    and duplicates_ok
)


if all_checks:

    st.success(
        "✅ DATASET PASSED QUALITY CHECKS"
    )

else:

    st.warning(
        "⚠️ DATASET REQUIRES ATTENTION"
    )


# =========================================================
# DATA PREVIEW
# =========================================================

st.subheader(
    "Cleaned Dataset Preview"
)

st.dataframe(
    df.head(50),
    use_container_width=True,
    hide_index=True
)