import argparse
import shutil
import subprocess
import sys
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"



# =========================================================
# WINDOWS UTF-8 OUTPUT
# =========================================================

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =========================================================
# ARGUMENTS
# =========================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Offline Bitcoin Transaction "
            "Analytics Pipeline"
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help=(
            "Path to input CSV, JSON or XML file"
        )
    )

    return parser.parse_args()


# =========================================================
# VALIDATE INPUT
# =========================================================

def validate_input(input_file):
    """
    Check that the input file exists and uses a
    supported format.
    """

    input_path = Path(input_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{input_path}"
        )

    if not input_path.is_file():
        raise ValueError(
            f"Input path is not a file:\n{input_path}"
        )

    extension = input_path.suffix.lower()

    supported_formats = {
        ".csv",
        ".json",
        ".xml"
    }

    if extension not in supported_formats:
        raise ValueError(
            "Unsupported file format.\n"
            "Supported formats: CSV, JSON, XML"
        )

    return input_path


# =========================================================
# PREPARE INPUT
# =========================================================

def prepare_input(input_file):
    """
    Copy the selected input into data/raw as active_input
    while preserving its original extension.
    """

    input_path = validate_input(input_file)

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    extension = input_path.suffix.lower()

    active_input = (
        RAW_DIR
        / f"active_input{extension}"
    )

    # Remove previous active input files so that the
    # pipeline cannot accidentally use an old format.
    for old_file in RAW_DIR.glob("active_input.*"):

        try:
            old_file.unlink()
        except Exception:
            pass

    shutil.copy2(
        input_path,
        active_input
    )

    return active_input


# =========================================================
# PREPARE CANONICAL CSV
# =========================================================

def create_canonical_csv(active_input):
    """
    Convert the selected CSV/JSON/XML input into one
    canonical CSV file.

    Downstream stages can then consistently use:

        data/raw/bitcoin_transactions.csv
    """

    print("\nPreparing standardized input...")

    try:

        # Import the loader function from your project.
        from ingestion.loader import load_dataset

        df = load_dataset(
            active_input
        )

    except Exception as error:

        raise RuntimeError(
            "Unable to parse the input dataset.\n"
            f"Input: {active_input}\n"
            f"Reason: {error}"
        ) from error

    if df is None:
        raise RuntimeError(
            "The loader returned None instead of a DataFrame."
        )

    if df.empty:
        raise ValueError(
            "The input dataset is empty."
        )

    canonical_file = (
        RAW_DIR
        / "bitcoin_transactions.csv"
    )

    df.to_csv(
        canonical_file,
        index=False
    )

    print(
        f"Standardized records: {len(df)}"
    )

    print(
        f"Standardized columns: {len(df.columns)}"
    )

    print(
        f"Canonical file: {canonical_file}"
    )

    return canonical_file


# =========================================================
# RUN ONE PIPELINE STEP
# =========================================================

def run_step(
    step_number,
    description,
    script,
    extra_args=None
):
    """
    Execute one Python script and stop the pipeline
    immediately if the script fails.
    """

    print("\n")
    print("=" * 70)
    print(
        f"STEP {step_number} - {description}"
    )
    print("=" * 70)

    script_path = (
        BASE_DIR / script
    )

    if not script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found:\n{script_path}"
        )

    command = [
        sys.executable,
        str(script_path)
    ]

    if extra_args:
        command.extend(
            [str(arg) for arg in extra_args]
        )

    # Force child Python processes to use UTF-8.
    environment = dict()

    import os

    environment.update(
        os.environ
    )

    environment[
        "PYTHONIOENCODING"
    ] = "utf-8"

    environment[
        "PYTHONUTF8"
    ] = "1"

    try:

        result = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            env=environment
        )

    except Exception as error:

        raise RuntimeError(
            f"Could not start step:\n"
            f"{description}\n"
            f"Reason: {error}"
        ) from error

    if result.returncode != 0:

        raise RuntimeError(
            f"Step failed:\n"
            f"{description}\n"
            f"Exit code: {result.returncode}"
        )

    print(
        f"STEP {step_number} COMPLETED"
    )


# =========================================================
# CHECK REQUIRED PIPELINE OUTPUT
# =========================================================

def check_output_files():

    print("\n")
    print("=" * 70)
    print("CHECKING PIPELINE OUTPUTS")
    print("=" * 70)

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

    missing_files = []

    for filename in required_files:

        path = (
            PROCESSED_DIR / filename
        )

        if path.exists():

            print(
                f"[OK] {filename}"
            )

        else:

            print(
                f"[MISSING] {filename}"
            )

            missing_files.append(
                filename
            )

    if missing_files:

        raise RuntimeError(
            "The pipeline completed but "
            "some expected output files are missing:\n"
            + "\n".join(missing_files)
        )

    print(
        "\nAll expected output files are present."
    )


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    print("=" * 70)
    print(
        "BITCOIN TRANSACTION ANALYTICS PIPELINE"
    )
    print("=" * 70)

    print(
        "\nStarting complete offline processing pipeline..."
    )

    # -----------------------------------------------------
    # Parse command-line input
    # -----------------------------------------------------

    args = parse_arguments()

    # -----------------------------------------------------
    # Prepare directories
    # -----------------------------------------------------

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Validate and copy user input
    # -----------------------------------------------------

    active_input = prepare_input(
        args.input
    )

    print(
        f"\nActive input file:"
    )

    print(
        active_input
    )

    # -----------------------------------------------------
    # Convert CSV/JSON/XML into canonical CSV
    # -----------------------------------------------------

    canonical_csv = create_canonical_csv(
        active_input
    )

    # =====================================================
    # STEP 1
    # =====================================================

    run_step(
        1,
        "DATA INGESTION",
        "ingestion/loader.py",
        [
            "--input",
            str(active_input)
        ]
    )

    # =====================================================
    # STEP 2
    # =====================================================

    run_step(
        2,
        "DATA VALIDATION AND CLEANING",
        "preprocessing/cleaner.py"
    )

    # =====================================================
    # STEP 3
    # =====================================================

    run_step(
        3,
        "GEO-IP / ASN ENRICHMENT",
        "geoip/enrichment.py"
    )

    # =====================================================
    # STEP 4
    # =====================================================

    run_step(
        4,
        "FEATURE ENGINEERING",
        "features/feature_engineering.py"
    )

    # =====================================================
    # STEP 5
    # =====================================================

    run_step(
        5,
        "IP / TXID / WALLET CORRELATION",
        "correlation/correlate.py"
    )

    # =====================================================
    # STEP 6
    # =====================================================

    run_step(
        6,
        "ENTITY GRAPH CONSTRUCTION",
        "graph/graph_builder.py"
    )

    # =====================================================
    # STEP 7
    # =====================================================

    run_step(
        7,
        "AI/ML ANOMALY DETECTION",
        "ml/anomaly_detection.py"
    )

    # =====================================================
    # STEP 8
    # =====================================================

    run_step(
        8,
        "ENTITY-LEVEL DETECTION",
        "ml/entity_detection.py"
    )

    # =====================================================
    # STEP 9
    # =====================================================

    run_step(
        9,
        "DBSCAN ENTITY CLUSTERING",
        "ml/clustering.py"
    )

    # =====================================================
    # STEP 10
    # =====================================================

    run_step(
        10,
        "EXPLAINABLE RISK SCORING",
        "ml/risk_scoring.py"
    )

    # =====================================================
    # STEP 11
    # =====================================================

    run_step(
        11,
        "MODEL EVALUATION",
        "ml/evaluate_model.py"
    )

    # =====================================================
    # FINAL OUTPUT CHECK
    # =====================================================

    check_output_files()

    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    print("\n")
    print("=" * 70)
    print(
        "COMPLETE PIPELINE FINISHED SUCCESSFULLY"
    )
    print("=" * 70)

    print(
        "\nProcessed files:"
    )

    print(
        PROCESSED_DIR
    )

    print(
        "\nDashboard command:"
    )

    print(
        "python -m streamlit run dashboard/app.py"
    )

    print(
        "\nPipeline completed successfully."
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print("\n")
        print("=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(
            f"\nReason:\n{error}"
        )

        sys.exit(1)