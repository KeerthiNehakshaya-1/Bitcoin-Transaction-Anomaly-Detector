import pandas as pd  # type: ignore
from pathlib import Path

try:
    from sklearn.metrics import ( # pyright: ignore[reportMissingModuleSource]
        classification_report,
        confusion_matrix,
        precision_score,
        recall_score,
        f1_score,
    )
except ImportError as exc:
    raise RuntimeError(
        "scikit-learn is required to evaluate the model. "
        "Install it with: pip install scikit-learn"
    ) from exc


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml_anomaly_results.csv"
)


# =========================================================
# LOAD RESULTS
# =========================================================

def load_results():

    if not RESULT_FILE.exists():

        raise FileNotFoundError(
            f"ML result file not found:\n{RESULT_FILE}"
        )

    return pd.read_csv(RESULT_FILE)


# =========================================================
# PREPARE LABELS
# =========================================================

def prepare_labels(df):

    df = df.copy()

    # -----------------------------------------------------
    # Actual ground truth
    # -----------------------------------------------------

    df["actual"] = (
        df["synthetic_scenario"]
        .fillna("normal")
        .astype(str)
        .str.lower()
        .ne("normal")
        .astype(int)
    )

    # -----------------------------------------------------
    # ML prediction
    # -----------------------------------------------------

    df["predicted"] = (
        df["ml_prediction"] == -1
    ).astype(int)

    return df


# =========================================================
# EVALUATE
# =========================================================

def evaluate(df):

    actual = df["actual"]

    predicted = df["predicted"]

    # -----------------------------------------------------
    # Confusion matrix
    # -----------------------------------------------------

    matrix = confusion_matrix(
        actual,
        predicted
    )

    tn, fp, fn, tp = matrix.ravel()

    print("\n" + "=" * 60)
    print("CONFUSION MATRIX")
    print("=" * 60)

    print(
        f"True Negatives : {tn}"
    )

    print(
        f"False Positives: {fp}"
    )

    print(
        f"False Negatives: {fn}"
    )

    print(
        f"True Positives : {tp}"
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

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

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1-score  : {f1:.4f}"
    )

    # -----------------------------------------------------
    # Detailed report
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)

    print(
        classification_report(
            actual,
            predicted,
            target_names=[
                "Normal",
                "Anomaly"
            ],
            zero_division=0
        )
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


# =========================================================
# CHECK KNOWN SCENARIOS
# =========================================================

def check_scenarios(df):

    print("\n" + "=" * 60)
    print("SCENARIO DETECTION")
    print("=" * 60)

    scenarios = (
        df["synthetic_scenario"]
        .fillna("normal")
        .value_counts()
    )

    for scenario, count in scenarios.items():

        subset = df[
            df["synthetic_scenario"]
            == scenario
        ]

        detected = (
            subset["predicted"]
            .sum()
        )

        detection_rate = (
            detected / len(subset)
            if len(subset) > 0
            else 0
        )

        print(
            f"\nScenario: {scenario}"
        )

        print(
            f"Total records : {len(subset)}"
        )

        print(
            f"Detected      : {detected}"
        )

        print(
            f"Detection rate: "
            f"{detection_rate:.2%}"
        )


# =========================================================
# SAVE METRICS
# =========================================================

def save_metrics(metrics):

    output_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "ml_evaluation_metrics.csv"
    )

    metrics_df = pd.DataFrame(
        [metrics]
    )

    metrics_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nMetrics saved to:\n{output_file}"
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("BITCOIN ANOMALY MODEL EVALUATION")
    print("=" * 60)

    df = load_results()

    print(
        f"\nRecords loaded: {len(df)}"
    )

    df = prepare_labels(df)

    metrics = evaluate(df)

    check_scenarios(df)

    save_metrics(metrics)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETED")
    print("=" * 60)