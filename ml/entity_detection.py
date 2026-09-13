import pandas as pd  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path


# ---------------------------------------------------------
# Load ML results
# ---------------------------------------------------------

def load_ml_results():

    base_dir = Path(__file__).resolve().parent.parent

    file_path = (
        base_dir
        / "data"
        / "processed"
        / "ml_anomaly_results.csv"
    )

    print("Loading ML anomaly results:")
    print(file_path)

    return pd.read_csv(file_path)


# ---------------------------------------------------------
# Evaluate transaction-level predictions
# ---------------------------------------------------------

def evaluate_model(df):

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    # Convert our synthetic scenario labels into
    # binary ground truth.

    df["actual_anomaly"] = (
        df["synthetic_scenario"]
        .fillna("normal")
        .str.lower()
        .ne("normal")
        .astype(int)
    )

    # Convert ML prediction:
    # -1 = anomaly
    #  1 = normal

    df["predicted_anomaly"] = (
        df["ml_prediction"] == -1
    ).astype(int)

    # -----------------------------------------------------
    # Confusion matrix values
    # -----------------------------------------------------

    true_positive = (
        (
            (df["actual_anomaly"] == 1) &
            (df["predicted_anomaly"] == 1)
        )
        .sum()
    )

    true_negative = (
        (
            (df["actual_anomaly"] == 0) &
            (df["predicted_anomaly"] == 0)
        )
        .sum()
    )

    false_positive = (
        (
            (df["actual_anomaly"] == 0) &
            (df["predicted_anomaly"] == 1)
        )
        .sum()
    )

    false_negative = (
        (
            (df["actual_anomaly"] == 1) &
            (df["predicted_anomaly"] == 0)
        )
        .sum()
    )

    print("\nConfusion Matrix:")

    print(
        f"True Positive : {true_positive}"
    )

    print(
        f"True Negative : {true_negative}"
    )

    print(
        f"False Positive: {false_positive}"
    )

    print(
        f"False Negative: {false_negative}"
    )

    # -----------------------------------------------------
    # Precision
    # -----------------------------------------------------

    if true_positive + false_positive > 0:

        precision = (
            true_positive
            / (true_positive + false_positive)
        )

    else:
        precision = 0

    # -----------------------------------------------------
    # Recall
    # -----------------------------------------------------

    if true_positive + false_negative > 0:

        recall = (
            true_positive
            / (true_positive + false_negative)
        )

    else:
        recall = 0

    # -----------------------------------------------------
    # F1 score
    # -----------------------------------------------------

    if precision + recall > 0:

        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
        )

    else:
        f1 = 0

    print(
        f"\nPrecision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1-score:  {f1:.4f}"
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ---------------------------------------------------------
# Create wallet-level anomaly scores
# ---------------------------------------------------------

def create_wallet_scores(df):

    print("\nCreating wallet-level anomaly scores...")

    # Combine input and output wallets.

    records = []

    for _, row in df.iterrows():

        wallets = []

        try:
            import json

            wallets.extend(
                json.loads(row["input_addresses"])
            )

        except Exception:
            pass

        try:

            wallets.extend(
                json.loads(row["output_addresses"])
            )

        except Exception:
            pass

        # Remove duplicates
        wallets = set(wallets)

        for wallet in wallets:

            records.append({
                "wallet": wallet,
                "anomaly_score": row["anomaly_score"],
                "ml_prediction": row["ml_prediction"],
                "txid": row["txid"]
            })

    wallet_df = pd.DataFrame(records)

    if wallet_df.empty:

        return pd.DataFrame()

    wallet_scores = (
        wallet_df
        .groupby("wallet")
        .agg(
            wallet_transaction_count=(
                "txid",
                "nunique"
            ),

            average_anomaly_score=(
                "anomaly_score",
                "mean"
            ),

            maximum_anomaly_score=(
                "anomaly_score",
                "max"
            ),

            anomalous_transactions=(
                "ml_prediction",
                lambda x: (x == -1).sum()
            )
        )
        .reset_index()
    )

    # A simple initial entity score.
    #
    # Later we will combine this with graph and
    # behavioral risk signals.

    wallet_scores["wallet_anomaly_score"] = (
        0.6
        * wallet_scores["average_anomaly_score"]
        +
        0.4
        * wallet_scores["maximum_anomaly_score"]
    )

    wallet_scores = wallet_scores.sort_values(
        "wallet_anomaly_score",
        ascending=False
    )

    return wallet_scores


# ---------------------------------------------------------
# Create IP-level anomaly scores
# ---------------------------------------------------------

def create_ip_scores(df):

    print("\nCreating IP-level anomaly scores...")

    ip_scores = (
        df.groupby("src_ip")
        .agg(
            ip_transaction_count=(
                "txid",
                "nunique"
            ),

            average_anomaly_score=(
                "anomaly_score",
                "mean"
            ),

            maximum_anomaly_score=(
                "anomaly_score",
                "max"
            ),

            anomalous_transactions=(
                "ml_prediction",
                lambda x: (x == -1).sum()
            ),

            unique_wallets=(
                "primary_wallet",
                "nunique"
            )
        )
        .reset_index()
    )

    ip_scores["ip_anomaly_score"] = (
        0.6
        * ip_scores["average_anomaly_score"]
        +
        0.4
        * ip_scores["maximum_anomaly_score"]
    )

    ip_scores = ip_scores.sort_values(
        "ip_anomaly_score",
        ascending=False
    )

    return ip_scores


# ---------------------------------------------------------
# Save entity results
# ---------------------------------------------------------

def save_entity_results(
    wallet_scores,
    ip_scores
):

    base_dir = Path(__file__).resolve().parent.parent

    output_dir = (
        base_dir
        / "data"
        / "processed"
    )

    wallet_file = (
        output_dir
        / "wallet_anomaly_scores.csv"
    )

    ip_file = (
        output_dir
        / "ip_anomaly_scores.csv"
    )

    wallet_scores.to_csv(
        wallet_file,
        index=False
    )

    ip_scores.to_csv(
        ip_file,
        index=False
    )

    print("\nResults saved:")

    print(wallet_file)
    print(ip_file)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("ENTITY-LEVEL ANOMALY DETECTION")
    print("=" * 60)

    # Load transaction ML results

    df = load_ml_results()

    print(
        f"\nTransactions loaded: {len(df)}"
    )

    # Evaluate transaction detector

    metrics = evaluate_model(df)

    # Create wallet scores

    wallet_scores = create_wallet_scores(df)

    # Create IP scores

    ip_scores = create_ip_scores(df)

    # Save

    save_entity_results(
        wallet_scores,
        ip_scores
    )

    # -----------------------------------------------------
    # Display top wallets
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("TOP SUSPICIOUS WALLETS")
    print("=" * 60)

    print(
        wallet_scores.head(15).to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # Display top IPs
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("TOP SUSPICIOUS IPs")
    print("=" * 60)

    print(
        ip_scores.head(15).to_string(
            index=False
        )
    )