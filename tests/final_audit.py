import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def check_file(filename):
    path = PROCESSED_DIR / filename

    if not path.exists():
        print(f"❌ Missing: {filename}")
        return False

    print(f"✅ Found: {filename}")
    return True


def check_scores(filename, column):
    path = PROCESSED_DIR / filename

    df = pd.read_csv(path)

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid = (
        values.isna()
        | (values < 0)
        | (values > 100)
    ).sum()

    if invalid == 0:
        print(
            f"✅ {filename}: {column} within 0-100"
        )
        return True

    print(
        f"❌ {filename}: {invalid} invalid scores"
    )
    return False


def check_alerts():

    path = (
        PROCESSED_DIR /
        "prioritized_alerts.csv"
    )

    df = pd.read_csv(path)

    required = [
        "priority_rank",
        "entity_type",
        "entity",
        "risk_score",
        "risk_level",
        "confidence",
        "evidence"
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        print(
            "❌ Missing alert columns:",
            missing
        )
        return False

    empty_evidence = (
        df["evidence"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    if empty_evidence:
        print(
            f"❌ {empty_evidence} alerts have no evidence"
        )
        return False

    print("✅ Alert structure and evidence verified")
    return True


if __name__ == "__main__":

    print("=" * 60)
    print("FINAL PROJECT AUDIT")
    print("=" * 60)

    required_files = [
        "bitcoin_transactions_cleaned.csv",
        "bitcoin_transactions_enriched.csv",
        "bitcoin_transactions_features.csv",
        "ip_txid_wallet_correlation.csv",
        "bitcoin_entity_graph.graphml",
        "graph_entity_features.csv",
        "graph_centrality.csv",
        "ml_anomaly_results.csv",
        "wallet_anomaly_scores.csv",
        "ip_anomaly_scores.csv",
        "wallet_clusters.csv",
        "cluster_statistics.csv",
        "wallet_risk_scores.csv",
        "ip_risk_scores.csv",
        "transaction_risk_scores.csv",
        "prioritized_alerts.csv",
        "ml_evaluation_metrics.csv"
    ]

    results = []

    for filename in required_files:
        results.append(
            check_file(filename)
        )

    results.append(
        check_scores(
            "wallet_risk_scores.csv",
            "risk_score"
        )
    )

    results.append(
        check_scores(
            "ip_risk_scores.csv",
            "risk_score"
        )
    )

    results.append(
        check_scores(
            "transaction_risk_scores.csv",
            "risk_score"
        )
    )

    results.append(
        check_alerts()
    )

    print("\n" + "=" * 60)

    if all(results):
        print("✅ FINAL AUDIT PASSED")
    else:
        print("❌ FINAL AUDIT FAILED")

    print("=" * 60)