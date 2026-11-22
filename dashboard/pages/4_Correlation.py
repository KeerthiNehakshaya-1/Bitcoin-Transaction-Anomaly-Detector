import streamlit as st
import pandas as pd
from pathlib import Path
import re
import ast
import json


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Correlation Analysis",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 Correlation Analysis")

st.write(
    "Investigate relationships between IP addresses, "
    "transactions, and wallet addresses."
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CORRELATION_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ip_txid_wallet_correlation.csv"
)

IP_SUMMARY_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ip_relationship_summary.csv"
)

WALLET_SUMMARY_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "wallet_relationship_summary.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    correlation_df = None
    ip_summary_df = None
    wallet_summary_df = None

    if CORRELATION_FILE.exists():
        correlation_df = pd.read_csv(
            CORRELATION_FILE
        )

    if IP_SUMMARY_FILE.exists():
        ip_summary_df = pd.read_csv(
            IP_SUMMARY_FILE
        )

    if WALLET_SUMMARY_FILE.exists():
        wallet_summary_df = pd.read_csv(
            WALLET_SUMMARY_FILE
        )

    return (
        correlation_df,
        ip_summary_df,
        wallet_summary_df
    )


(
    correlation_df,
    ip_summary_df,
    wallet_summary_df
) = load_data()


# =========================================================
# CHECK CORRELATION FILE
# =========================================================

if correlation_df is None:

    st.error(
        "Correlation data was not found.\n\n"
        "Run the pipeline first."
    )

    st.stop()


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

correlation_df.columns = [
    str(column).strip()
    for column in correlation_df.columns
]


# =========================================================
# DEBUG INFORMATION
# =========================================================

with st.expander("📋 Dataset Columns"):

    st.write(
        list(correlation_df.columns)
    )


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


def parse_list(value):

    """
    Convert list-like values stored in CSV
    into a Python list.
    """

    if pd.isna(value):
        return []

    if isinstance(value, list):
        return [
            str(x).strip()
            for x in value
            if str(x).strip()
        ]

    value = str(value).strip()

    if not value:
        return []

    # JSON list
    try:

        result = json.loads(value)

        if isinstance(result, list):

            return [
                str(x).strip()
                for x in result
                if str(x).strip()
            ]

    except Exception:
        pass

    # Python list
    try:

        result = ast.literal_eval(value)

        if isinstance(result, list):

            return [
                str(x).strip()
                for x in result
                if str(x).strip()
            ]

    except Exception:
        pass

    # Comma separated
    value = (
        value
        .replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace('"', "")
    )

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def transaction_numeric_part(txid):

    match = re.search(
        r"(\d+)$",
        str(txid)
    )

    if match:
        return match.group(1)

    return ""


def format_txid(txid):

    number = transaction_numeric_part(txid)

    if number:

        return f"{txid} | {number}"

    return str(txid)


def collect_values(df, possible_columns):

    """
    Collect unique values from all matching columns.
    Works for both normal strings and list-like columns.
    """

    values = set()

    for column in possible_columns:

        if column not in df.columns:
            continue

        for value in df[column].dropna():

            parsed = parse_list(value)

            if len(parsed) > 0:

                for item in parsed:

                    if item:
                        values.add(str(item).strip())

            else:

                value_string = str(value).strip()

                if value_string:
                    values.add(value_string)

    return sorted(values)


# =========================================================
# IDENTIFY POSSIBLE COLUMNS
# =========================================================

IP_COLUMNS = [
    "src_ip",
    "dst_ip",
    "source_ip",
    "destination_ip",
    "ip_address",
    "ip"
]

TXID_COLUMNS = [
    "txid",
    "transaction_id",
    "transaction",
    "TXID"
]

WALLET_COLUMNS = [
    "wallet",
    "wallet_address",
    "wallet_id",
    "input_wallet",
    "output_wallet",
    "input_address",
    "output_address",
    "input_addresses",
    "output_addresses",
    "input_wallets",
    "output_wallets"
]


# =========================================================
# COLLECT ENTITIES
# =========================================================

ip_values = collect_values(
    correlation_df,
    IP_COLUMNS
)

txid_values = collect_values(
    correlation_df,
    TXID_COLUMNS
)

wallet_values = collect_values(
    correlation_df,
    WALLET_COLUMNS
)


# =========================================================
# SUMMARY
# =========================================================

st.subheader("📊 Correlation Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Correlation Records",
        f"{len(correlation_df):,}"
    )

with c2:

    st.metric(
        "Unique IPs",
        f"{len(ip_values):,}"
    )

with c3:

    st.metric(
        "Unique Transactions",
        f"{len(txid_values):,}"
    )

with c4:

    st.metric(
        "Unique Wallets",
        f"{len(wallet_values):,}"
    )


st.divider()


# =========================================================
# SEARCH
# =========================================================

st.subheader("🔎 Investigate Entity")

entity_type = st.radio(
    "Select Entity Type",
    [
        "IP Address",
        "Transaction ID",
        "Wallet Address"
    ],
    horizontal=True
)


# =========================================================
# IP SEARCH
# =========================================================

if entity_type == "IP Address":

    if not ip_values:

        st.warning(
            "No IP addresses found in the correlation dataset."
        )

        st.stop()

    selected_entity = st.selectbox(
        "Search IP Address",
        options=[""] + ip_values,
        index=0,
        help="Type part of the IP address to filter the suggestions."
    )

    selected_type = "IP"


# =========================================================
# TRANSACTION SEARCH
# =========================================================

elif entity_type == "Transaction ID":

    if not txid_values:

        st.warning(
            "No transaction IDs found in the correlation dataset."
        )

        st.stop()

    selected_entity = st.selectbox(
        "Search Transaction ID",
        options=[""] + txid_values,
        index=0,
        format_func=lambda x: (
            "Select Transaction ID..."
            if x == ""
            else format_txid(x)
        ),
        help="Type the TXID or its numeric portion to filter suggestions."
    )

    selected_type = "TRANSACTION"


# =========================================================
# WALLET SEARCH
# =========================================================

else:

    if not wallet_values:

        st.error(
            "No wallet addresses were detected in the "
            "correlation dataset."
        )

        st.info(
            "Check the Dataset Columns section above. "
            "The correlation file may be using a different "
            "wallet column name."
        )

        st.stop()

    selected_entity = st.selectbox(
        "Search Wallet Address",
        options=[""] + wallet_values,
        index=0,
        help="Type part of the wallet address to filter the suggestions."
    )

    selected_type = "WALLET"


# =========================================================
# INVESTIGATION
# =========================================================

if selected_entity:

    st.divider()

    st.subheader(
        f"📌 Selected {entity_type}"
    )

    st.code(
        selected_entity
    )

    investigate = st.button(
        "🔍 Investigate",
        type="primary"
    )

    if investigate:

        result_df = pd.DataFrame()

        # =================================================
        # IP INVESTIGATION
        # =================================================

        if selected_type == "IP":

            conditions = []

            for column in IP_COLUMNS:

                if column in correlation_df.columns:

                    conditions.append(
                        correlation_df[column]
                        .astype(str)
                        .str.strip()
                        .eq(selected_entity)
                    )

            if conditions:

                mask = conditions[0]

                for condition in conditions[1:]:

                    mask = mask | condition

                result_df = correlation_df[
                    mask
                ].copy()


        # =================================================
        # TRANSACTION INVESTIGATION
        # =================================================

        elif selected_type == "TRANSACTION":

            for column in TXID_COLUMNS:

                if column in correlation_df.columns:

                    mask = (
                        correlation_df[column]
                        .astype(str)
                        .str.strip()
                        .eq(selected_entity)
                    )

                    result_df = correlation_df[
                        mask
                    ].copy()

                    if not result_df.empty:
                        break


        # =================================================
        # WALLET INVESTIGATION
        # =================================================

        elif selected_type == "WALLET":

            matching_rows = []

            for index, row in correlation_df.iterrows():

                found = False

                for column in WALLET_COLUMNS:

                    if column not in correlation_df.columns:
                        continue

                    wallets = parse_list(
                        row[column]
                    )

                    if selected_entity in wallets:

                        found = True
                        break

                    # Direct string comparison
                    if (
                        str(row[column]).strip()
                        == selected_entity
                    ):

                        found = True
                        break

                if found:

                    matching_rows.append(index)

            if matching_rows:

                result_df = correlation_df.loc[
                    matching_rows
                ].copy()


        # =================================================
        # NO RESULT
        # =================================================

        if result_df.empty:

            st.warning(
                "No matching relationship records were found."
            )

        else:

            # =================================================
            # SUMMARY
            # =================================================

            st.subheader("📈 Relationship Summary")

            s1, s2, s3, s4 = st.columns(4)

            tx_column = get_column(
                result_df,
                TXID_COLUMNS
            )

            if tx_column:

                transaction_count = (
                    result_df[tx_column]
                    .astype(str)
                    .nunique()
                )

            else:

                transaction_count = 0


            related_ips = set()

            for column in IP_COLUMNS:

                if column in result_df.columns:

                    related_ips.update(
                        result_df[column]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .tolist()
                    )


            related_wallets = set()

            for column in WALLET_COLUMNS:

                if column not in result_df.columns:
                    continue

                for value in result_df[column].dropna():

                    wallets = parse_list(value)

                    for wallet in wallets:

                        related_wallets.add(wallet)


            with s1:

                st.metric(
                    "Matching Records",
                    f"{len(result_df):,}"
                )

            with s2:

                st.metric(
                    "Transactions",
                    f"{transaction_count:,}"
                )

            with s3:

                st.metric(
                    "Related IPs",
                    f"{len(related_ips):,}"
                )

            with s4:

                st.metric(
                    "Related Wallets",
                    f"{len(related_wallets):,}"
                )


            # =================================================
            # RELATED IPs
            # =================================================

            if related_ips:

                st.subheader("🌐 Related IP Addresses")

                ip_table = pd.DataFrame(
                    {
                        "IP Address": sorted(
                            related_ips
                        )
                    }
                )

                st.dataframe(
                    ip_table,
                    use_container_width=True,
                    hide_index=True
                )


            # =================================================
            # RELATED TRANSACTIONS
            # =================================================

            if tx_column:

                st.subheader("₿ Related Transactions")

                tx_table = (
                    result_df[
                        [tx_column]
                    ]
                    .drop_duplicates()
                    .rename(
                        columns={
                            tx_column: "Transaction ID"
                        }
                    )
                )

                st.dataframe(
                    tx_table,
                    use_container_width=True,
                    hide_index=True
                )


            # =================================================
            # RELATED WALLETS
            # =================================================

            if related_wallets:

                st.subheader("👛 Related Wallet Addresses")

                wallet_table = pd.DataFrame(
                    {
                        "Wallet Address": sorted(
                            related_wallets
                        )
                    }
                )

                st.dataframe(
                    wallet_table,
                    use_container_width=True,
                    hide_index=True
                )


            # =================================================
            # RAW CORRELATION DATA
            # =================================================

            st.subheader("🔗 Correlation Records")

            st.dataframe(
                result_df,
                use_container_width=True,
                height=400
            )


            # =================================================
            # NETWORK INFORMATION
            # =================================================

            st.subheader("🌐 Network Information")

            network_columns = [
                "src_ip",
                "dst_ip",
                "source_ip",
                "destination_ip",
                "src_port",
                "dst_port",
                "source_port",
                "destination_port"
            ]

            available_network = [
                column
                for column in network_columns
                if column in result_df.columns
            ]

            if available_network:

                st.dataframe(
                    result_df[
                        available_network
                    ].drop_duplicates(),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "Network information is not available."
                )


            # =================================================
            # BLOCKCHAIN INFORMATION
            # =================================================

            st.subheader("₿ Blockchain Information")

            blockchain_columns = [
                "txid",
                "transaction_id",
                "input_addresses",
                "output_addresses",
                "input_amounts",
                "output_amounts",
                "transaction_amount",
                "total_input",
                "total_output",
                "fee",
                "script_type"
            ]

            available_blockchain = [
                column
                for column in blockchain_columns
                if column in result_df.columns
            ]

            if available_blockchain:

                st.dataframe(
                    result_df[
                        available_blockchain
                    ],
                    use_container_width=True,
                    hide_index=True
                )


            # =================================================
            # TIMELINE
            # =================================================

            st.subheader("🕒 Transaction Timeline")

            timestamp_column = get_column(
                result_df,
                [
                    "timestamp",
                    "time",
                    "datetime"
                ]
            )

            if timestamp_column:

                timeline_df = result_df.copy()

                timeline_df[timestamp_column] = pd.to_datetime(
                    timeline_df[timestamp_column],
                    errors="coerce"
                )

                timeline_df = (
                    timeline_df
                    .sort_values(
                        timestamp_column
                    )
                    .dropna(
                        subset=[
                            timestamp_column
                        ]
                    )
                )

                st.dataframe(
                    timeline_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "Timestamp information is not available."
                )


            # =================================================
            # CONNECTED ENTITIES
            # =================================================

            st.subheader("🕸️ Connected Entities")

            connected_entities = []

            for ip in sorted(related_ips):

                if ip != selected_entity:

                    connected_entities.append(
                        {
                            "Entity Type": "IP",
                            "Entity": ip
                        }
                    )


            if tx_column:

                for txid in sorted(
                    result_df[
                        tx_column
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                ):

                    if txid != selected_entity:

                        connected_entities.append(
                            {
                                "Entity Type": "TRANSACTION",
                                "Entity": txid
                            }
                        )


            for wallet in sorted(related_wallets):

                if wallet != selected_entity:

                    connected_entities.append(
                        {
                            "Entity Type": "WALLET",
                            "Entity": wallet
                        }
                    )


            if connected_entities:

                connected_df = pd.DataFrame(
                    connected_entities
                )

                st.dataframe(
                    connected_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No connected entities found."
                )


            # =================================================
            # DOWNLOAD
            # =================================================

            st.subheader("⬇️ Export Results")

            csv_data = result_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Investigation CSV",
                data=csv_data,
                file_name=(
                    f"{selected_type.lower()}_"
                    "investigation.csv"
                ),
                mime="text/csv"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Correlation analysis represents relationships observed "
    "in the processed dataset. Analytical relationships do not "
    "independently establish malicious or unlawful activity."
)