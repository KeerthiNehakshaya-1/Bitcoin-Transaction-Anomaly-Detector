import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = (
    BASE_DIR / "data" / "processed"
)

WALLET_FILE = (
    PROCESSED_DIR / "wallet_risk_scores.csv"
)

DBSCAN_EPS = 1.2
DBSCAN_MIN_SAMPLES = 5


# =========================================================
# LOAD WALLET DATA
# =========================================================

def load_wallet_data():

    if not WALLET_FILE.exists():
        raise FileNotFoundError(
            f"Wallet risk file not found:\n{WALLET_FILE}"
        )

    return pd.read_csv(WALLET_FILE)


# =========================================================
# SELECT BEHAVIORAL FEATURES
# =========================================================

def select_features(df):

    feature_columns = [
        "wallet_transaction_count",
        "average_anomaly_score",
        "maximum_anomaly_score",
        "anomalous_transactions",
        "unique_ips",
        "unique_counterparties",
        "degree",
        "in_degree",
        "out_degree",
        "degree_centrality"
    ]

    available = [
        column
        for column in feature_columns
        if column in df.columns
    ]

    if len(available) < 2:
        raise ValueError(
            "Not enough behavioral features available "
            "for clustering."
        )

    X = df[available].copy()

    for column in available:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)

    return X, available


# =========================================================
# RUN DBSCAN
# =========================================================

def run_dbscan(X):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    model = DBSCAN(
    eps=DBSCAN_EPS,
    min_samples=DBSCAN_MIN_SAMPLES
)

    labels = model.fit_predict(
        X_scaled
    )

    return labels, model


# =========================================================
# CREATE CLUSTER STATISTICS
# =========================================================

def create_cluster_statistics(df):

    stats = (
        df.groupby("cluster_id")
        .agg(
            entity_count=(
                "wallet",
                "nunique"
            ),

            average_risk_score=(
                "risk_score",
                "mean"
            ),

            average_anomaly_score=(
                "average_anomaly_score",
                "mean"
            ),

            average_transactions=(
                "wallet_transaction_count",
                "mean"
            ),

            average_unique_ips=(
                "unique_ips",
                "mean"
            )
        )
        .reset_index()
    )

    return stats


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DBSCAN WALLET ENTITY CLUSTERING")
    print("=" * 60)

    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    df = load_wallet_data()

    print(
        f"\nWallets loaded: {len(df)}"
    )

    # -----------------------------------------------------
    # Features
    # -----------------------------------------------------

    X, feature_names = select_features(
        df
    )

    print(
        f"Features used: {len(feature_names)}"
    )

    print("\nClustering features:")

    for feature in feature_names:
        print(f"  - {feature}")

    # -----------------------------------------------------
    # DBSCAN
    # -----------------------------------------------------

    labels, model = run_dbscan(X)

    df["cluster_id"] = labels

    # -----------------------------------------------------
    # Noise identification
    # -----------------------------------------------------

    df["cluster_type"] = np.where(
        df["cluster_id"] == -1,
        "NOISE",
        "CLUSTER"
    )

    # -----------------------------------------------------
    # Cluster statistics
    # -----------------------------------------------------

    cluster_stats = create_cluster_statistics(
        df
    )

    # -----------------------------------------------------
    # Save entity clusters
    # -----------------------------------------------------

    entity_file = (
        PROCESSED_DIR
        / "wallet_clusters.csv"
    )

    df.to_csv(
        entity_file,
        index=False
    )

    # -----------------------------------------------------
    # Save cluster statistics
    # -----------------------------------------------------

    stats_file = (
        PROCESSED_DIR
        / "cluster_statistics.csv"
    )

    cluster_stats.to_csv(
        stats_file,
        index=False
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    total_clusters = len(
        set(labels)
        - {-1}
    )

    noise_count = (
        labels == -1
    ).sum()

    print("\n" + "=" * 60)
    print("CLUSTERING RESULTS")
    print("=" * 60)

    print(
        f"Clusters discovered: {total_clusters}"
    )

    print(
        f"Noise entities: {noise_count}"
    )

    print(
        f"Clustered entities: "
        f"{len(df) - noise_count}"
    )

    print("\nCluster statistics:")

    print(
        cluster_stats.to_string(
            index=False
        )
    )

    print("\nFiles saved:")

    print(entity_file)
    print(stats_file)

    print("\n" + "=" * 60)
    print("DBSCAN CLUSTERING COMPLETED")
    print("=" * 60)