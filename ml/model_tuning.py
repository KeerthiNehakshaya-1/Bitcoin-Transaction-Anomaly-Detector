try:
    import pandas as pd # pyright: ignore[reportMissingModuleSource]
except ImportError as e:  # pragma: no cover - provide clearer error when dependency missing
    raise ImportError(
        "pandas is required to run model_tuning.py. Install it with `pip install pandas`"
    ) from e
from pathlib import Path

try:
    from sklearn.ensemble import IsolationForest # pyright: ignore[reportMissingModuleSource]
    from sklearn.preprocessing import StandardScaler # pyright: ignore[reportMissingModuleSource]
    from sklearn.metrics import ( # pyright: ignore[reportMissingModuleSource]
        precision_score,
        recall_score,
        f1_score
    )
except ImportError as e:  # pragma: no cover - provide clearer error when dependency missing
    raise ImportError(
        "scikit-learn is required to run model_tuning.py. Install it with `pip install scikit-learn`"
    ) from e


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "bitcoin_transactions_features.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found:\n{DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# =========================================================
# SELECT ML FEATURES
# =========================================================

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

    available = [
        column
        for column in feature_columns
        if column in df.columns
    ]

    X = df[available].copy()

    # Convert to numeric
    for column in X.columns:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    # Replace problematic values
    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    X = X.fillna(0)

    return X


# =========================================================
# CREATE GROUND TRUTH
# =========================================================

def create_ground_truth(df):

    return (
        df["synthetic_scenario"]
        .fillna("normal")
        .astype(str)
        .str.lower()
        .ne("normal")
        .astype(int)
    )


# =========================================================
# TEST ONE MODEL
# =========================================================

def test_model(X_scaled, actual, contamination):

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_scaled)

    predictions = model.predict(
        X_scaled
    )

    predicted = (
        predictions == -1
    ).astype(int)

    precision = precision_score(
        actual,
        predicted,
        zero_division=0
    )

    recall = recall_score(
        actual,
        predicted,
        zero_division=0
    )

    f1 = f1_score(
        actual,
        predicted,
        zero_division=0
    )

    return {
        "contamination": contamination,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "predicted_anomalies": int(
            predicted.sum()
        )
    }


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ISOLATION FOREST PARAMETER TUNING")
    print("=" * 60)

    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    df = load_data()

    print(
        f"\nRecords loaded: {len(df)}"
    )

    # -----------------------------------------------------
    # Features
    # -----------------------------------------------------

    X = select_features(df)

    print(
        f"Features used: {len(X.columns)}"
    )

    # -----------------------------------------------------
    # Ground truth
    # -----------------------------------------------------

    actual = create_ground_truth(
        df
    )

    # -----------------------------------------------------
    # Scale
    # -----------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X
    )

    # -----------------------------------------------------
    # Test different contamination values
    # -----------------------------------------------------

    contamination_values = [
        0.03,
        0.05,
        0.08,
        0.10,
        0.12
    ]

    results = []

    for contamination in contamination_values:

        print(
            f"\nTesting contamination = "
            f"{contamination}"
        )

        result = test_model(
            X_scaled,
            actual,
            contamination
        )

        results.append(result)

        print(
            f"Precision : "
            f"{result['precision']:.4f}"
        )

        print(
            f"Recall    : "
            f"{result['recall']:.4f}"
        )

        print(
            f"F1-score  : "
            f"{result['f1_score']:.4f}"
        )

        print(
            f"Predicted anomalies: "
            f"{result['predicted_anomalies']}"
        )

    # -----------------------------------------------------
    # Results table
    # -----------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        "f1_score",
        ascending=False
    )

    print("\n" + "=" * 60)
    print("TUNING RESULTS")
    print("=" * 60)

    print(
        results_df.to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # Best model
    # -----------------------------------------------------

    best = results_df.iloc[0]

    print("\n" + "=" * 60)
    print("BEST CONFIGURATION")
    print("=" * 60)

    print(
        f"Contamination: "
        f"{best['contamination']}"
    )

    print(
        f"Precision: "
        f"{best['precision']:.4f}"
    )

    print(
        f"Recall: "
        f"{best['recall']:.4f}"
    )

    print(
        f"F1-score: "
        f"{best['f1_score']:.4f}"
    )

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    output_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "model_tuning_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nResults saved to:\n"
        f"{output_file}"
    )