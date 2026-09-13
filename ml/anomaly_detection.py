import pandas as pd # pyright: ignore[reportMissingModuleSource]
from pathlib import Path

try:
    from sklearn.ensemble import IsolationForest # pyright: ignore[reportMissingModuleSource]
    from sklearn.preprocessing import StandardScaler  # pyright: ignore[reportMissingModuleSource]
except ImportError as exc:
    raise ImportError(
        "scikit-learn is required to run anomaly detection. "
        "Install it with: pip install scikit-learn"
    ) from exc


# ---------------------------------------------------------
# Load feature dataset
# ---------------------------------------------------------

def load_feature_data():

    base_dir = Path(__file__).resolve().parent.parent

    file_path = (
        base_dir
        / "data"
        / "processed"
        / "bitcoin_transactions_features.csv"
    )

    print("Loading feature dataset:")
    print(file_path)

    return pd.read_csv(file_path)


# ---------------------------------------------------------
# Select ML features
# ---------------------------------------------------------

def select_features(df):

    feature_columns = [
        "transaction_amount",
        "fee",
        "input_count",
        "output_count",
        "total_input",
        "total_output",
        "input_output_difference",
        "fee_ratio",
        "average_output_amount",
        "average_input_amount",

        "wallet_transaction_count",
        "wallet_unique_ips",
        "wallet_unique_txids",
        "wallet_unique_counterparties",

        "ip_transaction_count",
        "ip_unique_wallets",
        "ip_unique_txids",
        "ip_unique_destinations",

        "transaction_hour",
        "transaction_day_of_week",

        "seconds_since_previous_ip_tx",
        "seconds_since_previous_wallet_tx",

        "cross_country_transaction",
        "cross_asn_transaction",
        "ip_unique_countries",
        "ip_unique_asns"
    ]

    # Only use columns that actually exist
    available_features = [
        column
        for column in feature_columns
        if column in df.columns
    ]

    X = df[available_features].copy()

    return X, available_features


# ---------------------------------------------------------
# Clean ML feature values
# ---------------------------------------------------------

def prepare_features(X):

    X = X.copy()

    # Convert everything to numeric
    for column in X.columns:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    # Replace infinity values
    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    # Fill missing values
    X = X.fillna(0)

    return X


# ---------------------------------------------------------
# Scale features
# ---------------------------------------------------------

def scale_features(X):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler


# ---------------------------------------------------------
# Train Isolation Forest
# ---------------------------------------------------------

def train_model(X):

    print("\nTraining Isolation Forest...")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.08,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X)

    print("Model training completed.")

    return model


# ---------------------------------------------------------
# Generate anomaly predictions
# ---------------------------------------------------------

def generate_predictions(model, X):

    # Isolation Forest:
    #  1  = normal
    # -1  = anomaly

    predictions = model.predict(X)

    # Raw decision scores
    decision_scores = model.decision_function(X)

    return predictions, decision_scores


# ---------------------------------------------------------
# Convert scores to anomaly score
# ---------------------------------------------------------

def create_anomaly_scores(decision_scores):

    # Smaller decision_function values indicate
    # more anomalous observations.

    min_score = decision_scores.min()
    max_score = decision_scores.max()

    if max_score == min_score:

        return pd.Series(
            [50.0] * len(decision_scores)
        )

    normalized = (
        (max_score - decision_scores)
        / (max_score - min_score)
    )

    anomaly_score = normalized * 100

    return pd.Series(
        anomaly_score
    )


# ---------------------------------------------------------
# Save results
# ---------------------------------------------------------

def save_results(df):

    base_dir = Path(__file__).resolve().parent.parent

    output_dir = (
        base_dir
        / "data"
        / "processed"
    )

    output_file = (
        output_dir
        / "ml_anomaly_results.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\nResults saved to:")
    print(output_file)

    return output_file


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("AI/ML BITCOIN ANOMALY DETECTION")
    print("=" * 60)

    # ---------------------------------------------
    # 1. Load data
    # ---------------------------------------------

    df = load_feature_data()

    print(
        f"\nTransactions loaded: {len(df)}"
    )

    # ---------------------------------------------
    # 2. Select features
    # ---------------------------------------------

    X, feature_names = select_features(df)

    print(
        f"ML features selected: {len(feature_names)}"
    )

    print("\nFeatures:")
    for feature in feature_names:
        print(f"  - {feature}")

    # ---------------------------------------------
    # 3. Prepare features
    # ---------------------------------------------

    X = prepare_features(X)

    # ---------------------------------------------
    # 4. Scale
    # ---------------------------------------------

    X_scaled, scaler = scale_features(X)

    # ---------------------------------------------
    # 5. Train model
    # ---------------------------------------------

    model = train_model(X_scaled)

    # ---------------------------------------------
    # 6. Predict
    # ---------------------------------------------

    predictions, decision_scores = (
        generate_predictions(
            model,
            X_scaled
        )
    )

    # ---------------------------------------------
    # 7. Calculate anomaly score
    # ---------------------------------------------

    anomaly_scores = create_anomaly_scores(
        decision_scores
    )

    # ---------------------------------------------
    # 8. Add results
    # ---------------------------------------------

    result_df = df.copy()

    result_df["ml_prediction"] = predictions

    result_df["decision_score"] = decision_scores

    result_df["anomaly_score"] = (
        anomaly_scores
    )

    # ---------------------------------------------
    # 9. Add status
    # ---------------------------------------------

    result_df["ml_status"] = (
        result_df["ml_prediction"]
        .map({
            1: "NORMAL",
            -1: "ANOMALY"
        })
    )

    # ---------------------------------------------
    # 10. Sort by anomaly score
    # ---------------------------------------------

    result_df = result_df.sort_values(
        "anomaly_score",
        ascending=False
    )

    # ---------------------------------------------
    # 11. Save
    # ---------------------------------------------

    save_results(result_df)

    # ---------------------------------------------
    # 12. Display top anomalies
    # ---------------------------------------------

    print("\n" + "=" * 60)
    print("TOP ANOMALOUS TRANSACTIONS")
    print("=" * 60)

    display_columns = [
        "txid",
        "src_ip",
        "primary_wallet",
        "transaction_amount",
        "anomaly_score",
        "ml_status"
    ]

    available_display_columns = [
        column
        for column in display_columns
        if column in result_df.columns
    ]

    print(
        result_df[
            available_display_columns
        ].head(20).to_string(index=False)
    )

    # ---------------------------------------------
    # 13. Summary
    # ---------------------------------------------

    anomaly_count = (
        result_df["ml_prediction"] == -1
    ).sum()

    normal_count = (
        result_df["ml_prediction"] == 1
    ).sum()

    print("\n" + "=" * 60)
    print("MODEL SUMMARY")
    print("=" * 60)

    print(
        f"Normal transactions : {normal_count}"
    )

    print(
        f"Anomalous transactions: {anomaly_count}"
    )

    print("=" * 60)