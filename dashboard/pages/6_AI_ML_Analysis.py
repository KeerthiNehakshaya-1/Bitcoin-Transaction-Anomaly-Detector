import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI / ML Analysis",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# OUTPUT FILES
# ============================================================

OUTPUT_FILES = {
    "ML Anomaly Results": "ml_anomaly_results.csv",
    "Wallet Anomaly Scores": "wallet_anomaly_scores.csv",
    "IP Anomaly Scores": "ip_anomaly_scores.csv",
    "Wallet Clusters": "wallet_clusters.csv",
    "Cluster Statistics": "cluster_statistics.csv",
    "Wallet Risk Scores": "wallet_risk_scores.csv",
    "IP Risk Scores": "ip_risk_scores.csv",
    "Transaction Risk Scores": "transaction_risk_scores.csv",
    "Prioritized Alerts": "prioritized_alerts.csv",
}


# ============================================================
# FILE HELPERS
# ============================================================

def find_file(filename):
    """
    Find a file inside the project.
    """

    possible_paths = [
        BASE_DIR / filename,
        BASE_DIR / "ml" / filename,
        BASE_DIR / "data" / "processed" / filename,
        BASE_DIR / "models" / filename,
        BASE_DIR / "dashboard" / filename,
    ]

    for path in possible_paths:

        if path.exists() and path.is_file():
            return path

    try:

        matches = list(
            BASE_DIR.rglob(filename)
        )

        if matches:

            matches.sort(
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            return matches[0]

    except Exception:
        pass

    return None


def load_csv(filename):
    """
    Load CSV automatically.
    """

    path = find_file(filename)

    if path is None:
        return None, None

    try:

        return pd.read_csv(path), path

    except Exception as e:

        st.error(
            f"Could not read {filename}: {e}"
        )

        return None, path


# ============================================================
# COLUMN HELPERS
# ============================================================

def normalize_column_name(column):

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def find_column(df, names):

    if df is None or df.empty:
        return None

    column_map = {
        normalize_column_name(col): col
        for col in df.columns
    }

    for name in names:

        key = normalize_column_name(name)

        if key in column_map:
            return column_map[key]

    return None


def get_score_column(df):

    return find_column(
        df,
        [
            "risk_score",
            "anomaly_score",
            "score",
            "anomaly_strength",
            "decision_score"
        ]
    )


def get_risk_column(df):

    return find_column(
        df,
        [
            "risk_level",
            "risk",
            "severity",
            "alert_level"
        ]
    )


def get_anomaly_column(df):

    return find_column(
        df,
        [
            "anomaly",
            "is_anomaly",
            "anomaly_flag",
            "anomaly_label",
            "prediction",
            "predicted_anomaly",
            "outlier",
            "is_outlier"
        ]
    )


# ============================================================
# ENTITY COLUMN HELPERS
# ============================================================

def get_entity_columns(entity_type):

    if entity_type == "IP":

        return [
            "ip",
            "ip_address",
            "src_ip",
            "source_ip",
            "dst_ip",
            "destination_ip"
        ]

    if entity_type == "WALLET":

        return [
            "wallet",
            "wallet_id",
            "wallet_address",
            "input_wallet",
            "output_wallet",
            "input_address",
            "output_address",
            "input_addresses",
            "output_addresses",
            "input_wallets",
            "output_wallets",
            "address"
        ]

    return [
        "txid",
        "transaction",
        "transaction_id",
        "transaction_hash",
        "hash"
    ]


# ============================================================
# ANOMALY CONVERSION
# ============================================================

def convert_anomaly_values(series):

    def convert(value):

        if pd.isna(value):
            return False

        text = (
            str(value)
            .strip()
            .lower()
        )

        if text in {
            "anomaly",
            "anomalous",
            "true",
            "yes",
            "outlier",
            "attack",
            "1",
            "-1"
        }:

            return True

        if text in {
            "normal",
            "false",
            "no",
            "inlier",
            "0"
        }:

            return False

        try:

            number = float(value)

            if number == -1:
                return True

            if number == 1:
                return True

            return False

        except Exception:

            return False

    return series.apply(convert)


# ============================================================
# FORMAT HELPERS
# ============================================================

def format_number(value):

    try:

        if pd.isna(value):
            return "-"

        value = float(value)

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.2f}"

    except Exception:

        return str(value)


def show_dataframe(df, height=450):

    if df is None:

        st.info(
            "No data available."
        )

        return

    if df.empty:

        st.info(
            "No matching records."
        )

        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height
    )


def download_dataframe(df, filename):

    if df is None or df.empty:
        return

    st.download_button(
        label=f"⬇ Download {filename}",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv"
    )


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_wallet_values(value):

    results = []

    if value is None:
        return results

    try:

        if pd.isna(value):
            return results

    except Exception:
        pass

    if isinstance(value, list):

        for item in value:

            text = str(item).strip()

            if text:
                results.append(text)

        return results

    text = str(value).strip()

    if not text:
        return results

    # JSON list
    if (
        text.startswith("[")
        and text.endswith("]")
    ):

        try:

            parsed = json.loads(text)

            if isinstance(parsed, list):

                for item in parsed:

                    item_text = str(
                        item
                    ).strip()

                    if item_text:
                        results.append(
                            item_text
                        )

                return results

        except Exception:
            pass

    # Comma-separated values
    if "," in text:

        for item in text.split(","):

            item = item.strip()

            if item:
                results.append(item)

        return results

    results.append(text)

    return results


def extract_entities(df, entity_type):

    values = set()

    if df is None or df.empty:
        return []

    possible_columns = get_entity_columns(
        entity_type
    )

    for possible_column in possible_columns:

        actual_column = find_column(
            df,
            [possible_column]
        )

        if actual_column is None:
            continue

        for value in (
            df[actual_column]
            .dropna()
        ):

            if entity_type == "WALLET":

                extracted = extract_wallet_values(
                    value
                )

                for item in extracted:

                    if item:
                        values.add(
                            str(item).strip()
                        )

            else:

                text = str(value).strip()

                if text:
                    values.add(text)

    return sorted(
        values,
        key=lambda x: x.lower()
    )


def build_suggestions(
    entity_type,
    datasets
):

    values = set()

    for df in datasets:

        if df is None:
            continue

        extracted = extract_entities(
            df,
            entity_type
        )

        values.update(
            extracted
        )

    return sorted(
        values,
        key=lambda x: x.lower()
    )


# ============================================================
# ENTITY SEARCH
# ============================================================

def search_entity(
    df,
    entity_type,
    entity
):

    if df is None or df.empty:
        return pd.DataFrame()

    if not entity:
        return pd.DataFrame()

    mask = pd.Series(
        False,
        index=df.index
    )

    columns = get_entity_columns(
        entity_type
    )

    entity = str(entity).strip()

    for possible_column in columns:

        actual_column = find_column(
            df,
            [possible_column]
        )

        if actual_column is None:
            continue

        current = (
            df[actual_column]
            .astype(str)
        )

        current_mask = (
            current
            .str.contains(
                entity,
                case=False,
                na=False,
                regex=False
            )
        )

        mask = (
            mask
            | current_mask
        )

    return df.loc[mask].copy()


# ============================================================
# LOAD OUTPUTS
# ============================================================

loaded_data = {}
loaded_paths = {}

for display_name, filename in OUTPUT_FILES.items():

    df, path = load_csv(filename)

    loaded_data[display_name] = df
    loaded_paths[display_name] = path


# ============================================================
# DATASET REFERENCES
# ============================================================

ml_df = loaded_data["ML Anomaly Results"]

wallet_anomaly_df = (
    loaded_data["Wallet Anomaly Scores"]
)

ip_anomaly_df = (
    loaded_data["IP Anomaly Scores"]
)

wallet_clusters_df = (
    loaded_data["Wallet Clusters"]
)

cluster_stats_df = (
    loaded_data["Cluster Statistics"]
)

wallet_risk_df = (
    loaded_data["Wallet Risk Scores"]
)

ip_risk_df = (
    loaded_data["IP Risk Scores"]
)

transaction_risk_df = (
    loaded_data["Transaction Risk Scores"]
)

alerts_df = (
    loaded_data["Prioritized Alerts"]
)


# ============================================================
# ADDITIONAL PROCESSED DATA
# ============================================================

processed_dataframes = []

for filename in [
    "bitcoin_transactions_cleaned.csv",
    "bitcoin_transactions_enriched.csv",
    "bitcoin_transactions_features.csv"
]:

    df, _ = load_csv(filename)

    if df is not None and not df.empty:

        processed_dataframes.append(
            df
        )


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🤖 AI / ML Analysis")

st.markdown(
    """
AI-driven analysis of Bitcoin transaction behavior,
entity activity, behavioral clusters, risk scores,
and explainable investigation alerts.
"""
)

st.divider()


# ============================================================
# FILE STATUS
# ============================================================

with st.expander(
    "📁 Detected ML Output Files",
    expanded=False
):

    status_rows = []

    for display_name, filename in OUTPUT_FILES.items():

        path = loaded_paths[
            display_name
        ]

        if path is None:

            status_rows.append({
                "Output": display_name,
                "Filename": filename,
                "Status": "Not Found",
                "Location": "-"
            })

        else:

            try:

                location = str(
                    path.relative_to(
                        BASE_DIR
                    )
                )

            except Exception:

                location = str(path)

            status_rows.append({
                "Output": display_name,
                "Filename": filename,
                "Status": "Found",
                "Location": location
            })

    st.dataframe(
        pd.DataFrame(status_rows),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SUMMARY METRICS
# ============================================================

total_transactions = 0
anomalous_transactions = 0
normal_transactions = 0

if (
    ml_df is not None
    and not ml_df.empty
):

    total_transactions = len(
        ml_df
    )

    anomaly_column = get_anomaly_column(
        ml_df
    )

    if anomaly_column:

        flags = (
            convert_anomaly_values(
                ml_df[
                    anomaly_column
                ]
            )
        )

        anomalous_transactions = int(
            flags.sum()
        )

        normal_transactions = (
            total_transactions
            - anomalous_transactions
        )


wallet_count = (
    len(wallet_anomaly_df)
    if wallet_anomaly_df is not None
    else 0
)

ip_count = (
    len(ip_anomaly_df)
    if ip_anomaly_df is not None
    else 0
)

cluster_count = 0

if (
    wallet_clusters_df is not None
    and not wallet_clusters_df.empty
):

    cluster_column = find_column(
        wallet_clusters_df,
        [
            "cluster",
            "cluster_id",
            "label"
        ]
    )

    if cluster_column:

        values = pd.to_numeric(
            wallet_clusters_df[
                cluster_column
            ],
            errors="coerce"
        )

        cluster_count = len([
            x
            for x in values
            .dropna()
            .astype(int)
            .unique()
            if x != -1
        ])


# ============================================================
# SUMMARY DISPLAY
# ============================================================

st.subheader(
    "📊 ML Pipeline Summary"
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Transactions",
        format_number(
            total_transactions
        )
    )

with c2:

    st.metric(
        "Anomalies",
        format_number(
            anomalous_transactions
        )
    )

with c3:

    st.metric(
        "Wallets",
        format_number(
            wallet_count
        )
    )

with c4:

    st.metric(
        "IP Entities",
        format_number(
            ip_count
        )
    )

with c5:

    st.metric(
        "Clusters",
        format_number(
            cluster_count
        )
    )


st.divider()


# ============================================================
# ENTITY INVESTIGATION SEARCH
# ============================================================

st.subheader(
    "🔎 Entity Investigation Search"
)

st.caption(
    """
Select an entity type and start typing. The dropdown contains
entities detected across the ML, risk, cluster, alert and
processed transaction outputs.
"""
)


# ------------------------------------------------------------
# ENTITY TYPE
# ------------------------------------------------------------

entity_type = st.selectbox(
    "Entity Type",
    [
        "IP",
        "WALLET",
        "TRANSACTION"
    ],
    key="entity_type_search"
)


# ------------------------------------------------------------
# DATASETS FOR SUGGESTIONS
# ------------------------------------------------------------

if entity_type == "IP":

    suggestion_datasets = [
        ip_anomaly_df,
        ip_risk_df,
        alerts_df
    ]

elif entity_type == "WALLET":

    suggestion_datasets = [
        wallet_anomaly_df,
        wallet_risk_df,
        wallet_clusters_df,
        alerts_df
    ]

else:

    suggestion_datasets = [
        ml_df,
        transaction_risk_df,
        alerts_df
    ]


suggestion_datasets.extend(
    processed_dataframes
)


# ------------------------------------------------------------
# BUILD SUGGESTIONS
# ------------------------------------------------------------

suggestions = build_suggestions(
    entity_type,
    suggestion_datasets
)


# ------------------------------------------------------------
# SEARCHABLE DROPDOWN
# ------------------------------------------------------------

selected_entity = None

if suggestions:

    selected_entity = st.selectbox(
        f"Search {entity_type}",
        suggestions,
        index=None,
        placeholder=(
            f"Type to search "
            f"{entity_type.lower()}..."
        ),
        key="selected_entity_search"
    )

else:

    st.warning(
        f"No {entity_type.lower()} values "
        "were detected."
    )


# ============================================================
# SELECTED ENTITY INVESTIGATION
# ============================================================

if selected_entity:

    st.divider()

    st.subheader(
        f"🔍 Investigation: {selected_entity}"
    )

    st.success(
        f"Selected {entity_type}: "
        f"{selected_entity}"
    )


    # --------------------------------------------------------
    # SELECT PRIMARY DATASETS
    # --------------------------------------------------------

    if entity_type == "IP":

        primary_df = ip_anomaly_df
        risk_df = ip_risk_df

    elif entity_type == "WALLET":

        primary_df = wallet_anomaly_df
        risk_df = wallet_risk_df

    else:

        primary_df = ml_df
        risk_df = transaction_risk_df


    # --------------------------------------------------------
    # FIND MATCHES
    # --------------------------------------------------------

    primary_matches = search_entity(
        primary_df,
        entity_type,
        selected_entity
    )

    risk_matches = search_entity(
        risk_df,
        entity_type,
        selected_entity
    )

    alert_matches = search_entity(
        alerts_df,
        entity_type,
        selected_entity
    )

    cluster_matches = (
        search_entity(
            wallet_clusters_df,
            entity_type,
            selected_entity
        )
        if entity_type == "WALLET"
        else pd.DataFrame()
    )


    # --------------------------------------------------------
    # ENTITY SUMMARY
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "ML Records",
            format_number(
                len(primary_matches)
            )
        )

    with c2:

        st.metric(
            "Risk Records",
            format_number(
                len(risk_matches)
            )
        )

    with c3:

        st.metric(
            "Alert Records",
            format_number(
                len(alert_matches)
            )
        )

    with c4:

        st.metric(
            "Cluster Records",
            format_number(
                len(cluster_matches)
            )
            if entity_type == "WALLET"
            else "N/A"
        )


    # ========================================================
    # ENTITY DETAILS TABS
    # ========================================================

    entity_tab1, entity_tab2, entity_tab3, entity_tab4 = (
        st.tabs(
            [
                "🧠 ML Results",
                "⚠️ Risk & Explainability",
                "🔗 Related Records",
                "📋 Alert Details"
            ]
        )
    )


    # ========================================================
    # ML RESULTS
    # ========================================================

    with entity_tab1:

        st.markdown(
            f"### ML Results for `{selected_entity}`"
        )

        if primary_matches.empty:

            st.info(
                "No matching ML records found."
            )

        else:

            show_dataframe(
                primary_matches,
                height=400
            )

            download_dataframe(
                primary_matches,
                "selected_entity_ml_results.csv"
            )


    # ========================================================
    # RISK & EXPLAINABILITY
    # ========================================================

    with entity_tab2:

        st.markdown(
            f"### Risk Analysis for `{selected_entity}`"
        )

        if risk_matches.empty:

            st.info(
                "No matching risk record found."
            )

        else:

            score_column = get_score_column(
                risk_matches
            )

            risk_column = get_risk_column(
                risk_matches
            )


            # ------------------------------------------------
            # SCORE / LEVEL / CONFIDENCE
            # ------------------------------------------------

            score_value = None
            risk_value = "N/A"
            confidence_value = None

            if score_column:

                score_values = pd.to_numeric(
                    risk_matches[
                        score_column
                    ],
                    errors="coerce"
                ).dropna()

                if not score_values.empty:

                    score_value = float(
                        score_values.max()
                    )

            if risk_column:

                risk_values = (
                    risk_matches[
                        risk_column
                    ]
                    .dropna()
                    .astype(str)
                    .tolist()
                )

                if risk_values:

                    risk_value = (
                        risk_values[0]
                    )

            confidence_column = find_column(
                risk_matches,
                [
                    "confidence"
                ]
            )

            if confidence_column:

                confidence_values = pd.to_numeric(
                    risk_matches[
                        confidence_column
                    ],
                    errors="coerce"
                ).dropna()

                if not confidence_values.empty:

                    confidence_value = float(
                        confidence_values.max()
                    )


            a, b, c = st.columns(3)

            with a:

                st.metric(
                    "Risk Score",
                    (
                        f"{score_value:.2f}"
                        if score_value is not None
                        else "N/A"
                    )
                )

            with b:

                st.metric(
                    "Risk Level",
                    risk_value
                )

            with c:

                st.metric(
                    "Confidence",
                    (
                        f"{confidence_value:.2f}"
                        if confidence_value is not None
                        else "N/A"
                    )
                )


            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            explanation_column = find_column(
                risk_matches,
                [
                    "evidence",
                    "explanation",
                    "reason",
                    "risk_explanation",
                    "description"
                ]
            )

            if explanation_column:

                explanation = (
                    risk_matches.iloc[0][
                        explanation_column
                    ]
                )

                st.markdown(
                    "### Why was this entity flagged?"
                )

                st.info(
                    str(explanation)
                )


            # ------------------------------------------------
            # TOP SIGNAL
            # ------------------------------------------------

            top_signal_column = find_column(
                risk_matches,
                [
                    "top_signal"
                ]
            )

            if top_signal_column:

                top_signal = (
                    risk_matches.iloc[0][
                        top_signal_column
                    ]
                )

                st.markdown(
                    "### 🎯 Top Contributing Signal"
                )

                st.success(
                    str(top_signal)
                )


            # ------------------------------------------------
            # SIGNAL CONTRIBUTION BREAKDOWN
            # ------------------------------------------------

            contribution_columns = [
                column
                for column in risk_matches.columns
                if str(column)
                .lower()
                .startswith(
                    "contribution_"
                )
            ]


            if contribution_columns:

                st.markdown(
                    "### 📊 Signal Contribution Breakdown"
                )

                row = risk_matches.iloc[0]

                contribution_rows = []

                for column in contribution_columns:

                    value = pd.to_numeric(
                        row[column],
                        errors="coerce"
                    )

                    if pd.isna(value):
                        value = 0.0

                    readable_name = (
                        str(column)
                        .replace(
                            "contribution_",
                            ""
                        )
                        .replace(
                            "_",
                            " "
                        )
                        .title()
                    )

                    contribution_rows.append({

                        "Signal":
                            readable_name,

                        "Contribution":
                            round(
                                float(value),
                                2
                            )
                    })


                contribution_df = (
                    pd.DataFrame(
                        contribution_rows
                    )
                    .sort_values(
                        "Contribution",
                        ascending=False
                    )
                    .reset_index(
                        drop=True
                    )
                )


                st.dataframe(
                    contribution_df,
                    use_container_width=True,
                    hide_index=True
                )


                # --------------------------------------------
                # CONTRIBUTION CHART
                # --------------------------------------------

                chart_df = (
                    contribution_df
                    .set_index(
                        "Signal"
                    )
                )

                st.bar_chart(
                    chart_df[
                        "Contribution"
                    ]
                )


            # ------------------------------------------------
            # RAW RISK DATA
            # ------------------------------------------------

            with st.expander(
                "View complete risk record"
            ):

                show_dataframe(
                    risk_matches,
                    height=350
                )

            download_dataframe(
                risk_matches,
                "selected_entity_risk_results.csv"
            )


    # ========================================================
    # RELATED RECORDS
    # ========================================================

    with entity_tab3:

        st.markdown(
            "### 🔗 Related Records"
        )

        related_datasets = [

            (
                "Transaction ML Results",
                ml_df
            ),

            (
                "Wallet Analysis",
                wallet_anomaly_df
            ),

            (
                "IP Analysis",
                ip_anomaly_df
            ),

            (
                "Transaction Risk",
                transaction_risk_df
            ),

            (
                "Wallet Risk",
                wallet_risk_df
            ),

            (
                "IP Risk",
                ip_risk_df
            ),

            (
                "Prioritized Alerts",
                alerts_df
            ),

            (
                "Wallet Clusters",
                wallet_clusters_df
            )
        ]


        found_related = False


        for dataset_name, dataset in (
            related_datasets
        ):

            if dataset is None:
                continue

            if dataset.empty:
                continue

            matches = search_entity(
                dataset,
                entity_type,
                selected_entity
            )

            if not matches.empty:

                found_related = True

                st.markdown(
                    f"#### {dataset_name}"
                )

                show_dataframe(
                    matches,
                    height=300
                )


        if not found_related:

            st.info(
                "No related records were found."
            )


    # ========================================================
    # ALERT DETAILS
    # ========================================================

    with entity_tab4:

        st.markdown(
            "### 📋 Alert Details"
        )

        if alert_matches.empty:

            st.info(
                "This entity does not have a prioritized alert."
            )

        else:

            # ------------------------------------------------
            # SHOW ALERT TABLE
            # ------------------------------------------------

            show_dataframe(
                alert_matches,
                height=350
            )


            # ------------------------------------------------
            # SELECT ALERT
            # ------------------------------------------------

            selected_alert_index = st.selectbox(
                "Select Alert Record",
                alert_matches.index.tolist(),
                key="selected_alert_record"
            )

            selected_alert = (
                alert_matches.loc[
                    selected_alert_index
                ]
            )


            # ------------------------------------------------
            # BASIC ALERT DETAILS
            # ------------------------------------------------

            st.markdown(
                "### Alert Summary"
            )

            alert_score_column = get_score_column(
                alert_matches
            )

            alert_risk_column = get_risk_column(
                alert_matches
            )

            alert_confidence_column = (
                find_column(
                    alert_matches,
                    ["confidence"]
                )
            )

            alert_top_signal_column = (
                find_column(
                    alert_matches,
                    ["top_signal"]
                )
            )


            a, b, c, d = st.columns(4)

            with a:

                if alert_score_column:

                    st.metric(
                        "Risk Score",
                        format_number(
                            selected_alert[
                                alert_score_column
                            ]
                        )
                    )

            with b:

                if alert_risk_column:

                    st.metric(
                        "Risk Level",
                        str(
                            selected_alert[
                                alert_risk_column
                            ]
                        )
                    )

            with c:

                if alert_confidence_column:

                    st.metric(
                        "Confidence",
                        format_number(
                            selected_alert[
                                alert_confidence_column
                            ]
                        )
                    )

            with d:

                if alert_top_signal_column:

                    st.metric(
                        "Top Signal",
                        str(
                            selected_alert[
                                alert_top_signal_column
                            ]
                        )
                    )


            # ------------------------------------------------
            # EVIDENCE
            # ------------------------------------------------

            evidence_column = find_column(
                alert_matches,
                [
                    "evidence",
                    "explanation",
                    "reason"
                ]
            )

            if evidence_column:

                st.markdown(
                    "### 🧠 Explainable Evidence"
                )

                st.info(
                    str(
                        selected_alert[
                            evidence_column
                        ]
                    )
                )


            # ------------------------------------------------
            # SIGNAL CONTRIBUTIONS FROM ALERT
            # ------------------------------------------------

            contribution_text_column = (
                find_column(
                    alert_matches,
                    [
                        "signal_contributions"
                    ]
                )
            )

            if contribution_text_column:

                st.markdown(
                    "### 📊 Signal Contributions"
                )

                st.code(
                    str(
                        selected_alert[
                            contribution_text_column
                        ]
                    ),
                    language="text"
                )


            # ------------------------------------------------
            # COMPLETE RECORD
            # ------------------------------------------------

            with st.expander(
                "View complete alert record"
            ):

                detail_rows = []

                for column, value in (
                    selected_alert.items()
                ):

                    detail_rows.append({
                        "Field": column,
                        "Value": value
                    })

                st.dataframe(
                    pd.DataFrame(
                        detail_rows
                    ),
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# MAIN ANALYSIS TABS
# ============================================================

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🚨 Transaction Anomalies",
        "👛 Wallet Analysis",
        "🌐 IP Analysis",
        "🧩 Clustering",
        "📈 Model Evaluation",
        "⚠️ Prioritized Alerts"
    ]
)


# ============================================================
# TAB 1
# TRANSACTION ANOMALIES
# ============================================================

with tab1:

    st.subheader(
        "🚨 Transaction Anomaly Detection"
    )

    if ml_df is None:

        st.warning(
            "ml_anomaly_results.csv was not found."
        )

    elif ml_df.empty:

        st.info(
            "No transaction anomaly records available."
        )

    else:

        display_df = ml_df.copy()

        anomaly_column = get_anomaly_column(
            display_df
        )

        st.markdown(
            "### Detection Results"
        )

        show_dataframe(
            display_df
        )

        download_dataframe(
            display_df,
            "transaction_anomaly_results.csv"
        )


        # ----------------------------------------------------
        # ANOMALY SCORE
        # ----------------------------------------------------

        score_column = find_column(
            ml_df,
            [
                "anomaly_score",
                "score"
            ]
        )

        if score_column:

            scores = pd.to_numeric(
                ml_df[
                    score_column
                ],
                errors="coerce"
            ).dropna()

            if not scores.empty:

                st.markdown(
                    "### Anomaly Score Distribution"
                )

                chart_df = pd.DataFrame({
                    "Anomaly Score": scores
                })

                st.bar_chart(
                    chart_df
                )


# ============================================================
# TAB 2
# WALLET ANALYSIS
# ============================================================

with tab2:

    st.subheader(
        "👛 Wallet Behavioral Analysis"
    )

    if wallet_anomaly_df is None:

        st.info(
            "wallet_anomaly_scores.csv was not found."
        )

    elif wallet_anomaly_df.empty:

        st.info(
            "No wallet analysis records available."
        )

    else:

        display_df = (
            wallet_anomaly_df.copy()
        )

        risk_column = get_risk_column(
            display_df
        )

        score_column = get_score_column(
            display_df
        )


        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        if risk_column:

            levels = sorted(
                display_df[
                    risk_column
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_levels = st.multiselect(
                "Risk Level",
                levels,
                default=levels,
                key="wallet_risk_filter"
            )

            if selected_levels:

                display_df = display_df[
                    display_df[
                        risk_column
                    ]
                    .astype(str)
                    .isin(
                        selected_levels
                    )
                ]


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Total Wallets",
                format_number(
                    len(wallet_anomaly_df)
                )
            )

        with c2:

            st.metric(
                "Displayed",
                format_number(
                    len(display_df)
                )
            )

        with c3:

            high_count = 0

            if risk_column:

                high_count = int(
                    wallet_anomaly_df[
                        risk_column
                    ]
                    .astype(str)
                    .str.upper()
                    .isin(
                        [
                            "HIGH",
                            "CRITICAL"
                        ]
                    )
                    .sum()
                )

            st.metric(
                "High / Critical",
                format_number(
                    high_count
                )
            )


        st.markdown(
            "### Wallet Results"
        )

        show_dataframe(
            display_df
        )

        download_dataframe(
            display_df,
            "wallet_analysis.csv"
        )


        # ----------------------------------------------------
        # TOP WALLET SCORES
        # ----------------------------------------------------

        wallet_column = find_column(
            wallet_anomaly_df,
            [
                "wallet",
                "wallet_id",
                "wallet_address"
            ]
        )

        if (
            score_column
            and wallet_column
        ):

            chart_df = (
                wallet_anomaly_df.copy()
            )

            chart_df[
                score_column
            ] = pd.to_numeric(
                chart_df[
                    score_column
                ],
                errors="coerce"
            )

            chart_df = (
                chart_df
                .dropna(
                    subset=[
                        score_column
                    ]
                )
                .sort_values(
                    score_column,
                    ascending=False
                )
                .head(15)
            )

            if not chart_df.empty:

                st.markdown(
                    "### Highest Scoring Wallets"
                )

                st.bar_chart(
                    chart_df.set_index(
                        wallet_column
                    )[score_column]
                )


# ============================================================
# TAB 3
# IP ANALYSIS
# ============================================================

with tab3:

    st.subheader(
        "🌐 IP Behavioral Analysis"
    )

    if ip_anomaly_df is None:

        st.info(
            "ip_anomaly_scores.csv was not found."
        )

    elif ip_anomaly_df.empty:

        st.info(
            "No IP analysis records available."
        )

    else:

        display_df = (
            ip_anomaly_df.copy()
        )

        risk_column = get_risk_column(
            display_df
        )

        score_column = get_score_column(
            display_df
        )


        # ----------------------------------------------------
        # RISK FILTER
        # ----------------------------------------------------

        if risk_column:

            levels = sorted(
                display_df[
                    risk_column
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_levels = st.multiselect(
                "Risk Level",
                levels,
                default=levels,
                key="ip_risk_filter"
            )

            if selected_levels:

                display_df = display_df[
                    display_df[
                        risk_column
                    ]
                    .astype(str)
                    .isin(
                        selected_levels
                    )
                ]


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Total IP Entities",
                format_number(
                    len(ip_anomaly_df)
                )
            )

        with c2:

            st.metric(
                "Displayed",
                format_number(
                    len(display_df)
                )
            )


        st.markdown(
            "### IP Results"
        )

        show_dataframe(
            display_df
        )

        download_dataframe(
            display_df,
            "ip_analysis.csv"
        )


        # ----------------------------------------------------
        # TOP IP SCORES
        # ----------------------------------------------------

        ip_column = find_column(
            ip_anomaly_df,
            [
                "src_ip",
                "ip",
                "ip_address",
                "source_ip"
            ]
        )

        if (
            score_column
            and ip_column
        ):

            chart_df = (
                ip_anomaly_df.copy()
            )

            chart_df[
                score_column
            ] = pd.to_numeric(
                chart_df[
                    score_column
                ],
                errors="coerce"
            )

            chart_df = (
                chart_df
                .dropna(
                    subset=[
                        score_column
                    ]
                )
                .sort_values(
                    score_column,
                    ascending=False
                )
                .head(15)
            )

            if not chart_df.empty:

                st.markdown(
                    "### Highest Scoring IP Entities"
                )

                st.bar_chart(
                    chart_df.set_index(
                        ip_column
                    )[score_column]
                )


# ============================================================
# TAB 4
# CLUSTERING
# ============================================================

with tab4:

    st.subheader(
        "🧩 Wallet Behavioral Clustering"
    )

    if wallet_clusters_df is None:

        st.info(
            "wallet_clusters.csv was not found."
        )

    elif wallet_clusters_df.empty:

        st.info(
            "No clustering records available."
        )

    else:

        cluster_column = find_column(
            wallet_clusters_df,
            [
                "cluster_id",
                "cluster",
                "label"
            ]
        )


        if cluster_column:

            cluster_values = pd.to_numeric(
                wallet_clusters_df[
                    cluster_column
                ],
                errors="coerce"
            )

            unique_clusters = sorted(
                cluster_values
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )

            actual_clusters = [
                x
                for x in unique_clusters
                if x != -1
            ]

            noise_count = int(
                (
                    cluster_values
                    == -1
                ).sum()
            )


            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Clusters",
                    format_number(
                        len(actual_clusters)
                    )
                )

            with c2:

                st.metric(
                    "Wallet Records",
                    format_number(
                        len(wallet_clusters_df)
                    )
                )

            with c3:

                st.metric(
                    "Noise",
                    format_number(
                        noise_count
                    )
                )


            # ------------------------------------------------
            # CLUSTER SELECT
            # ------------------------------------------------

            cluster_options = [
                "All"
            ] + [
                str(x)
                for x in unique_clusters
            ]

            selected_cluster = st.selectbox(
                "Select Cluster",
                cluster_options,
                key="cluster_selection"
            )


            display_df = (
                wallet_clusters_df.copy()
            )


            if selected_cluster != "All":

                selected_number = int(
                    selected_cluster
                )

                display_df = (
                    display_df[
                        pd.to_numeric(
                            display_df[
                                cluster_column
                            ],
                            errors="coerce"
                        )
                        == selected_number
                    ]
                )


            st.markdown(
                "### Cluster Assignments"
            )

            show_dataframe(
                display_df
            )

            download_dataframe(
                display_df,
                "wallet_clusters_filtered.csv"
            )


            # ------------------------------------------------
            # DISTRIBUTION
            # ------------------------------------------------

            distribution = (
                wallet_clusters_df[
                    cluster_column
                ]
                .astype(str)
                .value_counts()
                .sort_index()
            )

            st.markdown(
                "### Cluster Distribution"
            )

            st.bar_chart(
                distribution
            )


        # ----------------------------------------------------
        # CLUSTER STATISTICS
        # ----------------------------------------------------

        if (
            cluster_stats_df is not None
            and not cluster_stats_df.empty
        ):

            st.markdown(
                "### Cluster Statistics"
            )

            show_dataframe(
                cluster_stats_df
            )

            download_dataframe(
                cluster_stats_df,
                "cluster_statistics.csv"
            )


        st.info(
            """
Cluster `-1` represents DBSCAN noise. It is an algorithmic
clustering result and does not by itself establish malicious activity.
"""
        )


# ============================================================
# TAB 5
# MODEL EVALUATION
# ============================================================

with tab5:

    st.subheader(
        "📈 Model Evaluation"
    )


    # --------------------------------------------------------
    # SEARCH SAVED EVALUATION
    # --------------------------------------------------------

    evaluation_df = None

    evaluation_path = None

    for filename in [
        "model_evaluation.csv",
        "evaluation_results.csv",
        "ml_evaluation.csv",
        "model_metrics.csv",
        "evaluation.csv"
    ]:

        df, path = load_csv(
            filename
        )

        if df is not None:

            evaluation_df = df
            evaluation_path = path

            break


    # --------------------------------------------------------
    # SAVED EVALUATION
    # --------------------------------------------------------

    if evaluation_df is not None:

        st.success(
            "Saved evaluation results detected."
        )

        show_dataframe(
            evaluation_df
        )

        download_dataframe(
            evaluation_df,
            "model_evaluation.csv"
        )


    # --------------------------------------------------------
    # CALCULATE EVALUATION
    # --------------------------------------------------------

    elif (
        ml_df is not None
        and not ml_df.empty
    ):

        scenario_column = find_column(
            ml_df,
            [
                "synthetic_scenario",
                "scenario",
                "ground_truth",
                "label"
            ]
        )

        anomaly_column = get_anomaly_column(
            ml_df
        )


        if (
            scenario_column
            and anomaly_column
        ):

            st.info(
                """
No saved evaluation CSV was found.
Metrics are calculated using the synthetic ground-truth
scenario available in the ML result data.
"""
            )


            truth = (
                ml_df[
                    scenario_column
                ]
                .astype(str)
                .str.strip()
                .str.lower()
            )


            y_true = (
                truth
                .str.contains(
                    "anomal",
                    na=False
                )
            )


            y_pred = (
                convert_anomaly_values(
                    ml_df[
                        anomaly_column
                    ]
                )
            )


            tp = int(
                (
                    y_true
                    & y_pred
                ).sum()
            )

            tn = int(
                (
                    ~y_true
                    & ~y_pred
                ).sum()
            )

            fp = int(
                (
                    ~y_true
                    & y_pred
                ).sum()
            )

            fn = int(
                (
                    y_true
                    & ~y_pred
                ).sum()
            )


            precision = (
                tp / (tp + fp)
                if tp + fp > 0
                else 0
            )

            recall = (
                tp / (tp + fn)
                if tp + fn > 0
                else 0
            )

            f1 = (
                2 * precision * recall
                / (precision + recall)
                if precision + recall > 0
                else 0
            )

            accuracy = (
                (tp + tn)
                / (
                    tp + tn + fp + fn
                )
                if tp + tn + fp + fn > 0
                else 0
            )


            # ------------------------------------------------
            # METRICS
            # ------------------------------------------------

            a, b, c, d = st.columns(4)

            with a:

                st.metric(
                    "Precision",
                    f"{precision * 100:.2f}%"
                )

            with b:

                st.metric(
                    "Recall",
                    f"{recall * 100:.2f}%"
                )

            with c:

                st.metric(
                    "F1 Score",
                    f"{f1 * 100:.2f}%"
                )

            with d:

                st.metric(
                    "Accuracy",
                    f"{accuracy * 100:.2f}%"
                )


            # ------------------------------------------------
            # CONFUSION MATRIX
            # ------------------------------------------------

            st.markdown(
                "### Confusion Matrix"
            )

            confusion_df = pd.DataFrame(
                [
                    {
                        "Actual": "Anomalous",
                        "Predicted Anomalous": tp,
                        "Predicted Normal": fn
                    },
                    {
                        "Actual": "Normal",
                        "Predicted Anomalous": fp,
                        "Predicted Normal": tn
                    }
                ]
            )

            st.dataframe(
                confusion_df,
                use_container_width=True,
                hide_index=True
            )


            # ------------------------------------------------
            # DETAILED METRICS
            # ------------------------------------------------

            metrics_df = pd.DataFrame(
                [
                    {
                        "Metric": "Accuracy",
                        "Value": accuracy
                    },
                    {
                        "Metric": "Precision",
                        "Value": precision
                    },
                    {
                        "Metric": "Recall",
                        "Value": recall
                    },
                    {
                        "Metric": "F1 Score",
                        "Value": f1
                    },
                    {
                        "Metric": "True Positives",
                        "Value": tp
                    },
                    {
                        "Metric": "True Negatives",
                        "Value": tn
                    },
                    {
                        "Metric": "False Positives",
                        "Value": fp
                    },
                    {
                        "Metric": "False Negatives",
                        "Value": fn
                    }
                ]
            )

            st.markdown(
                "### Detailed Metrics"
            )

            st.dataframe(
                metrics_df,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.warning(
                """
The required ground-truth or anomaly columns
could not be detected.
"""
            )

    else:

        st.warning(
            """
No ML output is available for evaluation.

Run:

python run_pipeline.py
"""
        )


# ============================================================
# TAB 6
# PRIORITIZED ALERTS
# ============================================================

with tab6:

    st.subheader(
        "⚠️ Prioritized Investigation Alerts"
    )


    if alerts_df is None:

        st.info(
            "prioritized_alerts.csv was not found."
        )

    elif alerts_df.empty:

        st.info(
            "No prioritized alerts available."
        )

    else:

        display_df = (
            alerts_df.copy()
        )


        score_column = get_score_column(
            display_df
        )

        risk_column = get_risk_column(
            display_df
        )

        entity_type_column = find_column(
            display_df,
            [
                "entity_type",
                "type"
            ]
        )


        # ----------------------------------------------------
        # RISK FILTER
        # ----------------------------------------------------

        if risk_column:

            risk_levels = sorted(
                display_df[
                    risk_column
                ]
                .dropna()
                .astype(str)
                .str.upper()
                .unique()
                .tolist()
            )

            selected_risk = st.multiselect(
                "Risk Level",
                risk_levels,
                default=risk_levels,
                key="alert_risk_filter"
            )

            if selected_risk:

                display_df = display_df[
                    display_df[
                        risk_column
                    ]
                    .astype(str)
                    .str.upper()
                    .isin(
                        selected_risk
                    )
                ]


        # ----------------------------------------------------
        # ENTITY TYPE
        # ----------------------------------------------------

        if entity_type_column:

            entity_types = sorted(
                display_df[
                    entity_type_column
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_type = st.selectbox(
                "Entity Type",
                ["All"] + entity_types,
                key="alert_entity_type_filter"
            )

            if selected_type != "All":

                display_df = display_df[
                    display_df[
                        entity_type_column
                    ]
                    .astype(str)
                    == selected_type
                ]


        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search_text = st.text_input(
            "🔎 Search Alert",
            placeholder="IP, wallet, TXID or evidence..."
        )


        if search_text.strip():

            search_value = (
                search_text
                .strip()
                .lower()
            )

            mask = pd.Series(
                False,
                index=display_df.index
            )

            for column in display_df.columns:

                mask = (
                    mask
                    |
                    display_df[column]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False,
                        regex=False
                    )
                )

            display_df = display_df[
                mask
            ]


        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        if score_column:

            display_df[
                score_column
            ] = pd.to_numeric(
                display_df[
                    score_column
                ],
                errors="coerce"
            )

            display_df = (
                display_df
                .sort_values(
                    score_column,
                    ascending=False
                )
            )


        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        critical_count = 0
        high_count = 0

        if risk_column:

            levels = (
                alerts_df[
                    risk_column
                ]
                .astype(str)
                .str.upper()
            )

            critical_count = int(
                (
                    levels
                    == "CRITICAL"
                ).sum()
            )

            high_count = int(
                (
                    levels
                    == "HIGH"
                ).sum()
            )


        a, b, c, d = st.columns(4)

        with a:

            st.metric(
                "Total Alerts",
                format_number(
                    len(alerts_df)
                )
            )

        with b:

            st.metric(
                "Displayed",
                format_number(
                    len(display_df)
                )
            )

        with c:

            st.metric(
                "Critical",
                format_number(
                    critical_count
                )
            )

        with d:

            st.metric(
                "High",
                format_number(
                    high_count
                )
            )


        # ----------------------------------------------------
        # ALERT TABLE
        # ----------------------------------------------------

        st.markdown(
            "### Ranked Alerts"
        )

        show_dataframe(
            display_df
        )

        download_dataframe(
            display_df,
            "prioritized_alerts_filtered.csv"
        )


        # ----------------------------------------------------
        # SELECT ALERT
        # ----------------------------------------------------

        if not display_df.empty:

            st.markdown(
                "### 🔍 Alert Investigation"
            )

            selected_index = st.selectbox(
                "Select Alert",
                display_df.index.tolist(),
                key="alert_detail_selector"
            )

            selected_alert = (
                display_df.loc[
                    selected_index
                ]
            )


            alert_score_column = get_score_column(
                display_df
            )

            alert_risk_column = get_risk_column(
                display_df
            )

            confidence_column = find_column(
                display_df,
                ["confidence"]
            )

            top_signal_column = find_column(
                display_df,
                ["top_signal"]
            )


            a, b, c, d = st.columns(4)

            with a:

                if alert_score_column:

                    st.metric(
                        "Risk Score",
                        format_number(
                            selected_alert[
                                alert_score_column
                            ]
                        )
                    )

            with b:

                if alert_risk_column:

                    st.metric(
                        "Risk Level",
                        str(
                            selected_alert[
                                alert_risk_column
                            ]
                        )
                    )

            with c:

                if confidence_column:

                    st.metric(
                        "Confidence",
                        format_number(
                            selected_alert[
                                confidence_column
                            ]
                        )
                    )

            with d:

                if top_signal_column:

                    st.metric(
                        "Top Signal",
                        str(
                            selected_alert[
                                top_signal_column
                            ]
                        )
                    )


            # ------------------------------------------------
            # EVIDENCE
            # ------------------------------------------------

            evidence_column = find_column(
                display_df,
                [
                    "evidence",
                    "explanation",
                    "reason"
                ]
            )

            if evidence_column:

                st.markdown(
                    "### 🧠 Why This Alert Was Prioritized"
                )

                st.info(
                    str(
                        selected_alert[
                            evidence_column
                        ]
                    )
                )


            # ------------------------------------------------
            # SIGNAL CONTRIBUTIONS
            # ------------------------------------------------

            contribution_column = find_column(
                display_df,
                [
                    "signal_contributions"
                ]
            )

            if contribution_column:

                st.markdown(
                    "### 📊 Signal Contributions"
                )

                contribution_text = str(
                    selected_alert[
                        contribution_column
                    ]
                )

                # Parse:
                #
                # Activity: 20.32 | ML Anomaly: 17.82 | ...
                #
                contribution_rows = []

                for part in contribution_text.split(
                    " | "
                ):

                    if ":" not in part:
                        continue

                    signal, value = (
                        part.split(
                            ":",
                            1
                        )
                    )

                    try:

                        numeric_value = float(
                            value.strip()
                        )

                    except Exception:

                        numeric_value = 0.0

                    contribution_rows.append({
                        "Signal":
                            signal.strip(),

                        "Contribution":
                            numeric_value
                    })


                if contribution_rows:

                    contribution_df = (
                        pd.DataFrame(
                            contribution_rows
                        )
                        .sort_values(
                            "Contribution",
                            ascending=False
                        )
                        .reset_index(
                            drop=True
                        )
                    )

                    st.dataframe(
                        contribution_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.bar_chart(
                        contribution_df.set_index(
                            "Signal"
                        )[
                            "Contribution"
                        ]
                    )

                else:

                    st.code(
                        contribution_text,
                        language="text"
                    )


            # ------------------------------------------------
            # COMPLETE ALERT RECORD
            # ------------------------------------------------

            with st.expander(
                "View Complete Alert Record"
            ):

                details = []

                for column, value in (
                    selected_alert.items()
                ):

                    details.append({
                        "Field": column,
                        "Value": value
                    })

                st.dataframe(
                    pd.DataFrame(details),
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    """
AI/ML outputs support investigation prioritization.
An anomaly or risk score is an analytical result and does not
by itself establish malicious or criminal activity.
"""
)