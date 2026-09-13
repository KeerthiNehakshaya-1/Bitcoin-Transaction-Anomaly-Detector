from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = (
    BASE_DIR / "data" / "processed"
)


REQUIRED_OUTPUTS = [
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


def test_required_outputs_exist():

    missing = []

    for filename in REQUIRED_OUTPUTS:

        path = PROCESSED_DIR / filename

        if not path.exists():
            missing.append(filename)

    assert not missing, (
        "Missing pipeline outputs: "
        + ", ".join(missing)
    )