import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# =========================================================
# LOAD ALL REQUIRED DATA
# =========================================================

def load_data():

    files = {
        "ml": PROCESSED_DIR / "ml_anomaly_results.csv",
        "wallet": PROCESSED_DIR / "wallet_anomaly_scores.csv",
        "ip": PROCESSED_DIR / "ip_anomaly_scores.csv",
        "graph": PROCESSED_DIR / "graph_entity_features.csv",
        "centrality": PROCESSED_DIR / "graph_centrality.csv",
        "correlation": PROCESSED_DIR / "ip_txid_wallet_correlation.csv",
        "clusters": PROCESSED_DIR / "wallet_clusters.csv"
    }

    print("Loading analysis results...")

    data = {}

    for name, path in files.items():

        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found:\n{path}"
            )

        data[name] = pd.read_csv(path)

    return data


# =========================================================
# NORMALIZE NUMERIC VALUE TO 0-100
# =========================================================

def normalize_series(series):

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    minimum = values.min()
    maximum = values.max()

    if maximum == minimum:

        return pd.Series(
            50.0,
            index=values.index
        )

    normalized = (
        (values - minimum)
        / (maximum - minimum)
    ) * 100

    return normalized.clip(0, 100)


# =========================================================
# TRANSACTION RISK
# =========================================================

def create_transaction_risk(ml_df):

    print("\nCreating transaction risk scores...")

    df = ml_df.copy()

    # -----------------------------------------------------
    # ML anomaly
    # -----------------------------------------------------

    df["ml_signal"] = normalize_series(
        df["anomaly_score"]
    )

    # -----------------------------------------------------
    # Transaction amount
    # -----------------------------------------------------

    df["amount_signal"] = normalize_series(
        df["transaction_amount"]
    )

    # -----------------------------------------------------
    # Fee
    # -----------------------------------------------------

    df["fee_signal"] = normalize_series(
        df["fee"]
    )

    # -----------------------------------------------------
    # Temporal burst signal
    # Smaller gap = stronger signal
    # -----------------------------------------------------

    time_gap = pd.to_numeric(
        df["seconds_since_previous_ip_tx"],
        errors="coerce"
    )

    valid_gap = time_gap.where(
        time_gap >= 0,
        np.nan
    )

    if valid_gap.notna().any():

        temporal_values = 1 / (
            valid_gap + 1
        )

        df["temporal_signal"] = normalize_series(
            temporal_values
        )

    else:

        df["temporal_signal"] = 0.0

    # -----------------------------------------------------
    # Final transaction risk
    # -----------------------------------------------------

    df["risk_score"] = (
        0.55 * df["ml_signal"]
        + 0.20 * df["amount_signal"]
        + 0.10 * df["fee_signal"]
        + 0.15 * df["temporal_signal"]
    )

    df["risk_score"] = df[
        "risk_score"
    ].clip(0, 100)

    return df


# =========================================================
# WALLET NETWORK FEATURES
# =========================================================

def calculate_wallet_network_features(
    correlation_df
):

    print(
        "\nCalculating wallet network statistics..."
    )

    records = []

    for _, row in correlation_df.iterrows():

        input_wallet = str(
            row["input_wallet"]
        )

        output_wallet = str(
            row["output_wallet"]
        )

        src_ip = str(
            row["src_ip"]
        )

        # -------------------------------------------------
        # Input wallet
        # -------------------------------------------------

        records.append({
            "wallet": input_wallet,
            "ip": src_ip,
            "counterparty": output_wallet
        })

        # -------------------------------------------------
        # Output wallet
        # -------------------------------------------------

        records.append({
            "wallet": output_wallet,
            "ip": src_ip,
            "counterparty": input_wallet
        })

    network_df = pd.DataFrame(
        records
    )

    if network_df.empty:

        return pd.DataFrame(
            columns=[
                "wallet",
                "unique_ips",
                "unique_counterparties"
            ]
        )

    wallet_network = (
        network_df
        .groupby("wallet")
        .agg(
            unique_ips=(
                "ip",
                "nunique"
            ),
            unique_counterparties=(
                "counterparty",
                "nunique"
            )
        )
        .reset_index()
    )

    return wallet_network


# =========================================================
# WALLET RISK
# =========================================================

def create_wallet_risk(
    wallet_df,
    graph_df,
    centrality_df,
    correlation_df,
    cluster_df
):

    print("\nCreating wallet risk scores...")

    df = wallet_df.copy()

    # -----------------------------------------------------
    # Wallet network statistics
    # -----------------------------------------------------

    wallet_network = (
        calculate_wallet_network_features(
            correlation_df
        )
    )

    df = df.merge(
        wallet_network,
        on="wallet",
        how="left"
    )

    # -----------------------------------------------------
    # Graph features
    # -----------------------------------------------------

    graph_wallets = graph_df[
        graph_df["node_type"] == "WALLET"
    ].copy()

    graph_wallets = graph_wallets[
        [
            "entity",
            "degree",
            "in_degree",
            "out_degree"
        ]
    ].rename(
        columns={
            "entity": "wallet"
        }
    )

    df = df.merge(
        graph_wallets,
        on="wallet",
        how="left"
    )

    # -----------------------------------------------------
    # Centrality
    # -----------------------------------------------------

    wallet_centrality = centrality_df[
        centrality_df["entity"].isin(
            graph_wallets["wallet"]
        )
    ][
        [
            "entity",
            "degree_centrality"
        ]
    ].rename(
        columns={
            "entity": "wallet"
        }
    )

    df = df.merge(
        wallet_centrality,
        on="wallet",
        how="left"
    )

    # -----------------------------------------------------
    # DBSCAN cluster information
    # -----------------------------------------------------

    cluster_info = cluster_df[
        [
            "wallet",
            "cluster_id",
            "cluster_type"
        ]
    ].copy()

    df = df.merge(
        cluster_info,
        on="wallet",
        how="left"
    )

    df["cluster_id"] = (
        pd.to_numeric(
            df["cluster_id"],
            errors="coerce"
        )
        .fillna(-1)
    )

    df["cluster_type"] = (
        df["cluster_type"]
        .fillna("NOISE")
    )

    # -----------------------------------------------------
    # Fill numeric missing values
    # -----------------------------------------------------

    numeric_columns = [
        "unique_ips",
        "unique_counterparties",
        "degree",
        "in_degree",
        "out_degree",
        "degree_centrality",
        "wallet_transaction_count",
        "maximum_anomaly_score",
        "average_anomaly_score",
        "anomalous_transactions"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

        else:

            df[column] = 0.0

    # -----------------------------------------------------
    # Component signals
    # -----------------------------------------------------

    # ML anomaly signal
    df["ml_signal"] = normalize_series(
        df["maximum_anomaly_score"]
    )

    # Transaction activity
    df["activity_signal"] = normalize_series(
        df["wallet_transaction_count"]
    )

    # Number of connected IPs
    df["network_signal"] = normalize_series(
        df["unique_ips"]
    )

    # Number of counterparties
    df["counterparty_signal"] = normalize_series(
        df["unique_counterparties"]
    )

    # Graph degree
    df["graph_signal"] = normalize_series(
        df["degree"]
    )

    # Centrality
    df["centrality_signal"] = normalize_series(
        df["degree_centrality"]
    )

    # -----------------------------------------------------
    # DBSCAN cluster behavior signal
    # -----------------------------------------------------

    base_behavior_score = (
        0.40 * df["ml_signal"]
        + 0.25 * df["activity_signal"]
        + 0.20 * df["network_signal"]
        + 0.15 * df["counterparty_signal"]
    )

    df["base_behavior_score"] = (
        base_behavior_score
    )

    # -----------------------------------------------------
    # Average behavior of each actual cluster
    # -----------------------------------------------------

    cluster_behavior = (
        df[
            df["cluster_id"] != -1
        ]
        .groupby("cluster_id")[
            "base_behavior_score"
        ]
        .mean()
    )

    # -----------------------------------------------------
    # Assign cluster average to wallets
    # -----------------------------------------------------

    df["cluster_signal"] = (
        df["cluster_id"]
        .map(cluster_behavior)
    )

    # -----------------------------------------------------
    # DBSCAN noise
    #
    # Noise does not belong to a dense cluster.
    # Use the wallet's own behavior as its signal.
    # -----------------------------------------------------

    df["cluster_signal"] = (
        df["cluster_signal"]
        .fillna(
            df["base_behavior_score"]
        )
    )

    # Normalize cluster signal
    df["cluster_signal"] = normalize_series(
        df["cluster_signal"]
    )

    # -----------------------------------------------------
    # Final wallet risk
    # -----------------------------------------------------

    df["risk_score"] = (
        0.30 * df["ml_signal"]
        + 0.18 * df["graph_signal"]
        + 0.18 * df["activity_signal"]
        + 0.10 * df["network_signal"]
        + 0.09 * df["counterparty_signal"]
        + 0.05 * df["centrality_signal"]
        + 0.10 * df["cluster_signal"]
    )

    df["risk_score"] = df[
        "risk_score"
    ].clip(0, 100)

    return df


# =========================================================
# IP NETWORK FEATURES
# =========================================================

def calculate_ip_network_features(
    correlation_df
):

    print(
        "\nCalculating IP network statistics..."
    )

    if correlation_df.empty:

        return pd.DataFrame(
            columns=[
                "src_ip",
                "unique_destinations"
            ]
        )

    records = []

    for _, row in correlation_df.iterrows():

        records.append({
            "src_ip": str(
                row["src_ip"]
            ),
            "destination": str(
                row["dst_ip"]
            )
        })

    network_df = pd.DataFrame(
        records
    )

    ip_network = (
        network_df
        .groupby("src_ip")
        .agg(
            unique_destinations=(
                "destination",
                "nunique"
            )
        )
        .reset_index()
    )

    return ip_network


# =========================================================
# IP RISK
# =========================================================

def create_ip_risk(
    ip_df,
    graph_df,
    centrality_df,
    correlation_df
):

    print("\nCreating IP risk scores...")

    df = ip_df.copy()

    # -----------------------------------------------------
    # Network statistics
    # -----------------------------------------------------

    ip_network = (
        calculate_ip_network_features(
            correlation_df
        )
    )

    df = df.merge(
        ip_network,
        on="src_ip",
        how="left"
    )

    # -----------------------------------------------------
    # Graph features
    # -----------------------------------------------------

    graph_ips = graph_df[
        graph_df["node_type"] == "IP"
    ].copy()

    graph_ips = graph_ips[
        [
            "entity",
            "degree",
            "in_degree",
            "out_degree"
        ]
    ].rename(
        columns={
            "entity": "src_ip"
        }
    )

    df = df.merge(
        graph_ips,
        on="src_ip",
        how="left"
    )

    # -----------------------------------------------------
    # Centrality
    # -----------------------------------------------------

    ip_centrality = centrality_df[
        centrality_df["entity"].isin(
            graph_ips["src_ip"]
        )
    ][
        [
            "entity",
            "degree_centrality"
        ]
    ].rename(
        columns={
            "entity": "src_ip"
        }
    )

    df = df.merge(
        ip_centrality,
        on="src_ip",
        how="left"
    )

    # -----------------------------------------------------
    # Fill missing values
    # -----------------------------------------------------

    numeric_columns = [
        "unique_wallets",
        "unique_destinations",
        "degree",
        "in_degree",
        "out_degree",
        "degree_centrality",
        "ip_transaction_count",
        "maximum_anomaly_score",
        "average_anomaly_score",
        "anomalous_transactions"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

        else:

            df[column] = 0.0

    # -----------------------------------------------------
    # Component signals
    # -----------------------------------------------------

    df["ml_signal"] = normalize_series(
        df["maximum_anomaly_score"]
    )

    df["activity_signal"] = normalize_series(
        df["ip_transaction_count"]
    )

    df["wallet_signal"] = normalize_series(
        df["unique_wallets"]
    )

    df["destination_signal"] = normalize_series(
        df["unique_destinations"]
    )

    df["graph_signal"] = normalize_series(
        df["degree"]
    )

    # -----------------------------------------------------
    # Final IP risk
    # -----------------------------------------------------

    df["risk_score"] = (
        0.35 * df["ml_signal"]
        + 0.20 * df["graph_signal"]
        + 0.20 * df["activity_signal"]
        + 0.15 * df["wallet_signal"]
        + 0.10 * df["destination_signal"]
    )

    df["risk_score"] = df[
        "risk_score"
    ].clip(0, 100)

    return df


# =========================================================
# RISK LEVEL
# =========================================================

def assign_risk_level(score):

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


# =========================================================
# CONFIDENCE INDICATOR
# =========================================================

def calculate_confidence(score):

    confidence = (
        0.50
        + (
            abs(score - 50)
            / 100
        )
    )

    return round(
        min(
            confidence,
            0.99
        ),
        2
    )


# =========================================================
# WALLET EXPLANATION
# =========================================================

def generate_wallet_explanation(row):

    reasons = []

    # -----------------------------------------------------
    # ML anomaly
    # -----------------------------------------------------

    if row["ml_signal"] >= 70:

        reasons.append(
            "High ML anomaly score"
        )

    # -----------------------------------------------------
    # Transaction activity
    # -----------------------------------------------------

    if row["activity_signal"] >= 70:

        reasons.append(
            "Unusually high transaction activity"
        )

    # -----------------------------------------------------
    # Network connections
    # -----------------------------------------------------

    if row["network_signal"] >= 70:

        reasons.append(
            "Connected to many IP addresses"
        )

    # -----------------------------------------------------
    # Counterparties
    # -----------------------------------------------------

    if row["counterparty_signal"] >= 70:

        reasons.append(
            "Connected to many counterparties"
        )

    # -----------------------------------------------------
    # Graph connectivity
    # -----------------------------------------------------

    if row["graph_signal"] >= 70:

        reasons.append(
            "High graph connectivity"
        )

    # -----------------------------------------------------
    # Graph centrality
    # -----------------------------------------------------

    if row["centrality_signal"] >= 70:

        reasons.append(
            "High graph centrality"
        )

    # -----------------------------------------------------
    # DBSCAN cluster behavior
    # -----------------------------------------------------

    if (
        "cluster_signal" in row.index
        and row["cluster_signal"] >= 70
    ):

        reasons.append(
            "Behavior belongs to a high-scoring "
            "behavioral cluster"
        )

    # -----------------------------------------------------
    # DBSCAN noise
    # -----------------------------------------------------

    if (
        "cluster_type" in row.index
        and str(
            row["cluster_type"]
        ).upper() == "NOISE"
    ):

        reasons.append(
            "Behavior does not fit a dense "
            "DBSCAN cluster"
        )

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    if not reasons:

        reasons.append(
            "No dominant anomalous signal"
        )

    return "; ".join(
        reasons
    )


# =========================================================
# IP EXPLANATION
# =========================================================

def generate_ip_explanation(row):

    reasons = []

    if row["ml_signal"] >= 70:

        reasons.append(
            "High ML anomaly score"
        )

    if row["activity_signal"] >= 70:

        reasons.append(
            "High transaction activity"
        )

    if row["wallet_signal"] >= 70:

        reasons.append(
            "Associated with many wallets"
        )

    if row["destination_signal"] >= 70:

        reasons.append(
            "Connected to many destination IPs"
        )

    if row["graph_signal"] >= 70:

        reasons.append(
            "High graph connectivity"
        )

    if not reasons:

        reasons.append(
            "No dominant anomalous signal"
        )

    return "; ".join(
        reasons
    )


# =========================================================
# TRANSACTION EXPLANATION
# =========================================================

def generate_transaction_explanation(row):

    reasons = []

    if row["ml_signal"] >= 70:

        reasons.append(
            "High ML anomaly score"
        )

    if row["amount_signal"] >= 70:

        reasons.append(
            "Unusually large transaction amount"
        )

    if row["fee_signal"] >= 70:

        reasons.append(
            "Unusually high transaction fee"
        )

    if row["temporal_signal"] >= 70:

        reasons.append(
            "Unusual temporal or burst behavior"
        )

    if not reasons:

        reasons.append(
            "No dominant anomalous signal"
        )

    return "; ".join(
        reasons
    )


# =========================================================
# SIGNAL CONTRIBUTIONS
# =========================================================

def get_wallet_signal_contributions(row):
    """
    Calculate the weighted contribution of each
    wallet signal to the final risk score.
    """

    return {

        "ML Anomaly":
            0.30 * float(
                row.get(
                    "ml_signal",
                    0
                )
            ),

        "Graph":
            0.18 * float(
                row.get(
                    "graph_signal",
                    0
                )
            ),

        "Activity":
            0.18 * float(
                row.get(
                    "activity_signal",
                    0
                )
            ),

        "Network":
            0.10 * float(
                row.get(
                    "network_signal",
                    0
                )
            ),

        "Counterparty":
            0.09 * float(
                row.get(
                    "counterparty_signal",
                    0
                )
            ),

        "Centrality":
            0.05 * float(
                row.get(
                    "centrality_signal",
                    0
                )
            ),

        "Cluster":
            0.10 * float(
                row.get(
                    "cluster_signal",
                    0
                )
            )
    }


def get_ip_signal_contributions(row):
    """
    Calculate the weighted contribution of each
    IP signal to the final risk score.
    """

    return {

        "ML Anomaly":
            0.35 * float(
                row.get(
                    "ml_signal",
                    0
                )
            ),

        "Graph":
            0.20 * float(
                row.get(
                    "graph_signal",
                    0
                )
            ),

        "Activity":
            0.20 * float(
                row.get(
                    "activity_signal",
                    0
                )
            ),

        "Wallet Connections":
            0.15 * float(
                row.get(
                    "wallet_signal",
                    0
                )
            ),

        "Destination Connections":
            0.10 * float(
                row.get(
                    "destination_signal",
                    0
                )
            )
    }


def get_transaction_signal_contributions(row):
    """
    Calculate the weighted contribution of each
    transaction signal to the final risk score.
    """

    return {

        "ML Anomaly":
            0.55 * float(
                row.get(
                    "ml_signal",
                    0
                )
            ),

        "Transaction Amount":
            0.20 * float(
                row.get(
                    "amount_signal",
                    0
                )
            ),

        "Transaction Fee":
            0.10 * float(
                row.get(
                    "fee_signal",
                    0
                )
            ),

        "Temporal Burst":
            0.15 * float(
                row.get(
                    "temporal_signal",
                    0
                )
            )
    }


# =========================================================
# GET TOP CONTRIBUTING SIGNAL
# =========================================================

def get_top_contributing_signal(
    contributions
):

    if not contributions:
        return "None"

    return max(
        contributions,
        key=contributions.get
    )


# =========================================================
# FORMAT CONTRIBUTIONS
# =========================================================

def format_signal_contributions(
    contributions
):

    if not contributions:

        return (
            "No signal contributions available."
        )

    sorted_contributions = sorted(
        contributions.items(),
        key=lambda item: item[1],
        reverse=True
    )

    lines = []

    for signal, contribution in (
        sorted_contributions
    ):

        lines.append(
            f"{signal}: {contribution:.2f}"
        )

    return " | ".join(
        lines
    )


# =========================================================
# CREATE SIGNAL CONTRIBUTION COLUMNS
# =========================================================

def add_wallet_contribution_columns(
    df
):

    for index, row in df.iterrows():

        contributions = (
            get_wallet_signal_contributions(
                row
            )
        )

        df.loc[
            index,
            "contribution_ml"
        ] = contributions[
            "ML Anomaly"
        ]

        df.loc[
            index,
            "contribution_graph"
        ] = contributions[
            "Graph"
        ]

        df.loc[
            index,
            "contribution_activity"
        ] = contributions[
            "Activity"
        ]

        df.loc[
            index,
            "contribution_network"
        ] = contributions[
            "Network"
        ]

        df.loc[
            index,
            "contribution_counterparty"
        ] = contributions[
            "Counterparty"
        ]

        df.loc[
            index,
            "contribution_centrality"
        ] = contributions[
            "Centrality"
        ]

        df.loc[
            index,
            "contribution_cluster"
        ] = contributions[
            "Cluster"
        ]

    return df


def add_ip_contribution_columns(
    df
):

    for index, row in df.iterrows():

        contributions = (
            get_ip_signal_contributions(
                row
            )
        )

        df.loc[
            index,
            "contribution_ml"
        ] = contributions[
            "ML Anomaly"
        ]

        df.loc[
            index,
            "contribution_graph"
        ] = contributions[
            "Graph"
        ]

        df.loc[
            index,
            "contribution_activity"
        ] = contributions[
            "Activity"
        ]

        df.loc[
            index,
            "contribution_wallets"
        ] = contributions[
            "Wallet Connections"
        ]

        df.loc[
            index,
            "contribution_destinations"
        ] = contributions[
            "Destination Connections"
        ]

    return df


def add_transaction_contribution_columns(
    df
):

    for index, row in df.iterrows():

        contributions = (
            get_transaction_signal_contributions(
                row
            )
        )

        df.loc[
            index,
            "contribution_ml"
        ] = contributions[
            "ML Anomaly"
        ]

        df.loc[
            index,
            "contribution_amount"
        ] = contributions[
            "Transaction Amount"
        ]

        df.loc[
            index,
            "contribution_fee"
        ] = contributions[
            "Transaction Fee"
        ]

        df.loc[
            index,
            "contribution_temporal"
        ] = contributions[
            "Temporal Burst"
        ]

    return df


# =========================================================
# CREATE ALERTS
# =========================================================

def create_alerts(
    wallet_risk,
    ip_risk,
    transaction_risk
):

    alerts = []

    # -----------------------------------------------------
    # Wallet alerts
    # -----------------------------------------------------

    for _, row in wallet_risk.iterrows():

        score = float(
            row["risk_score"]
        )

        contributions = (
            get_wallet_signal_contributions(
                row
            )
        )

        top_signal = (
            get_top_contributing_signal(
                contributions
            )
        )

        alerts.append({

            "entity_type":
                "WALLET",

            "entity":
                row["wallet"],

            "risk_score":
                round(
                    score,
                    2
                ),

            "risk_level":
                assign_risk_level(
                    score
                ),

            "confidence":
                calculate_confidence(
                    score
                ),

            "top_signal":
                top_signal,

            "evidence":
                generate_wallet_explanation(
                    row
                ),

            "signal_contributions":
                format_signal_contributions(
                    contributions
                )
        })


    # -----------------------------------------------------
    # IP alerts
    # -----------------------------------------------------

    for _, row in ip_risk.iterrows():

        score = float(
            row["risk_score"]
        )

        contributions = (
            get_ip_signal_contributions(
                row
            )
        )

        top_signal = (
            get_top_contributing_signal(
                contributions
            )
        )

        alerts.append({

            "entity_type":
                "IP",

            "entity":
                row["src_ip"],

            "risk_score":
                round(
                    score,
                    2
                ),

            "risk_level":
                assign_risk_level(
                    score
                ),

            "confidence":
                calculate_confidence(
                    score
                ),

            "top_signal":
                top_signal,

            "evidence":
                generate_ip_explanation(
                    row
                ),

            "signal_contributions":
                format_signal_contributions(
                    contributions
                )
        })


    # -----------------------------------------------------
    # Transaction alerts
    # -----------------------------------------------------

    for _, row in transaction_risk.iterrows():

        score = float(
            row["risk_score"]
        )

        contributions = (
            get_transaction_signal_contributions(
                row
            )
        )

        top_signal = (
            get_top_contributing_signal(
                contributions
            )
        )

        alerts.append({

            "entity_type":
                "TRANSACTION",

            "entity":
                row["txid"],

            "risk_score":
                round(
                    score,
                    2
                ),

            "risk_level":
                assign_risk_level(
                    score
                ),

            "confidence":
                calculate_confidence(
                    score
                ),

            "top_signal":
                top_signal,

            "evidence":
                generate_transaction_explanation(
                    row
                ),

            "signal_contributions":
                format_signal_contributions(
                    contributions
                )
        })


    # -----------------------------------------------------
    # Create dataframe
    # -----------------------------------------------------

    alerts_df = pd.DataFrame(
        alerts
    )

    # -----------------------------------------------------
    # Sort by risk score
    # -----------------------------------------------------

    if not alerts_df.empty:

        alerts_df = (
            alerts_df
            .sort_values(
                "risk_score",
                ascending=False
            )
            .reset_index(
                drop=True
            )
        )

        # -------------------------------------------------
        # Priority rank
        # -------------------------------------------------

        alerts_df["priority_rank"] = (
            alerts_df.index + 1
        )

    return alerts_df


# =========================================================
# SAVE OUTPUTS
# =========================================================

def save_outputs(
    wallet_risk,
    ip_risk,
    transaction_risk,
    alerts
):

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    wallet_file = (
        PROCESSED_DIR
        / "wallet_risk_scores.csv"
    )

    ip_file = (
        PROCESSED_DIR
        / "ip_risk_scores.csv"
    )

    transaction_file = (
        PROCESSED_DIR
        / "transaction_risk_scores.csv"
    )

    alert_file = (
        PROCESSED_DIR
        / "prioritized_alerts.csv"
    )

    # -----------------------------------------------------
    # Add contribution columns
    # -----------------------------------------------------

    wallet_risk = (
        add_wallet_contribution_columns(
            wallet_risk
        )
    )

    ip_risk = (
        add_ip_contribution_columns(
            ip_risk
        )
    )

    transaction_risk = (
        add_transaction_contribution_columns(
            transaction_risk
        )
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    wallet_risk.to_csv(
        wallet_file,
        index=False
    )

    ip_risk.to_csv(
        ip_file,
        index=False
    )

    transaction_risk.to_csv(
        transaction_file,
        index=False
    )

    alerts.to_csv(
        alert_file,
        index=False
    )

    print("\nResults saved successfully:")

    print(
        f"  {wallet_file}"
    )

    print(
        f"  {ip_file}"
    )

    print(
        f"  {transaction_file}"
    )

    print(
        f"  {alert_file}"
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("EXPLAINABLE RISK SCORING ENGINE")
    print("=" * 60)

    # -----------------------------------------------------
    # Load all data
    # -----------------------------------------------------

    data = load_data()

    ml_df = data["ml"]
    wallet_df = data["wallet"]
    ip_df = data["ip"]
    graph_df = data["graph"]
    centrality_df = data["centrality"]
    correlation_df = data["correlation"]
    cluster_df = data["clusters"]

    print("\nFiles loaded successfully.")

    print(
        f"ML records           : {len(ml_df)}"
    )

    print(
        f"Wallet records       : {len(wallet_df)}"
    )

    print(
        f"IP records            : {len(ip_df)}"
    )

    print(
        f"Graph entities       : {len(graph_df)}"
    )

    print(
        f"Correlation records  : {len(correlation_df)}"
    )

    # -----------------------------------------------------
    # Transaction risk
    # -----------------------------------------------------

    transaction_risk = (
        create_transaction_risk(
            ml_df
        )
    )

    # -----------------------------------------------------
    # Wallet risk
    # -----------------------------------------------------

    wallet_risk = (
        create_wallet_risk(
            wallet_df,
            graph_df,
            centrality_df,
            correlation_df,
            cluster_df
        )
    )

    # -----------------------------------------------------
    # IP risk
    # -----------------------------------------------------

    ip_risk = (
        create_ip_risk(
            ip_df,
            graph_df,
            centrality_df,
            correlation_df
        )
    )

    # -----------------------------------------------------
    # Create prioritized alerts
    # -----------------------------------------------------

    alerts = create_alerts(
        wallet_risk,
        ip_risk,
        transaction_risk
    )

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    save_outputs(
        wallet_risk,
        ip_risk,
        transaction_risk,
        alerts
    )

    # -----------------------------------------------------
    # Display top alerts
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("TOP PRIORITIZED INVESTIGATIVE LEADS")
    print("=" * 60)

    if not alerts.empty:

        print(
            alerts[
                [
                    "priority_rank",
                    "entity_type",
                    "entity",
                    "risk_score",
                    "risk_level",
                    "confidence",
                    "top_signal"
                ]
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

    else:

        print(
            "No alerts generated."
        )

    # -----------------------------------------------------
    # Display explanations
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("TOP ALERT EXPLANATIONS")
    print("=" * 60)

    for _, row in (
        alerts.head(10).iterrows()
    ):

        print(
            f"\n#{row['priority_rank']} "
            f"{row['entity_type']}: "
            f"{row['entity']}"
        )

        print(
            f"Risk Score : "
            f"{row['risk_score']}/100"
        )

        print(
            f"Risk Level : "
            f"{row['risk_level']}"
        )

        print(
            f"Confidence : "
            f"{row['confidence']}"
        )

        print(
            f"Top Signal : "
            f"{row['top_signal']}"
        )

        print(
            f"Evidence   : "
            f"{row['evidence']}"
        )

        print(
            f"Contributions: "
            f"{row['signal_contributions']}"
        )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("RISK SCORING COMPLETED")
    print("=" * 60)

    print(
        f"Total alerts generated: "
        f"{len(alerts)}"
    )

    if not alerts.empty:

        print(
            f"Critical alerts: "
            f"{(
                alerts['risk_level']
                == 'CRITICAL'
            ).sum()}"
        )

        print(
            f"High alerts: "
            f"{(
                alerts['risk_level']
                == 'HIGH'
            ).sum()}"
        )

        print(
            f"Medium alerts: "
            f"{(
                alerts['risk_level']
                == 'MEDIUM'
            ).sum()}"
        )

        print(
            f"Low alerts: "
            f"{(
                alerts['risk_level']
                == 'LOW'
            ).sum()}"
        )

    print("=" * 60)