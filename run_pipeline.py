import subprocess
import sys
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# RUN A PYTHON SCRIPT
# =========================================================

def run_step(description, script):

    print("\n")
    print("=" * 70)
    print(description)
    print("=" * 70)

    command = [
        sys.executable,
        str(BASE_DIR / script)
    ]

    result = subprocess.run(
        command,
        cwd=BASE_DIR
    )

    if result.returncode != 0:

        print(
            f"\n❌ STEP FAILED: {description}"
        )

        sys.exit(
            result.returncode
        )

    print(
        f"\n✅ STEP COMPLETED: {description}"
    )


# =========================================================
# MAIN PIPELINE
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("BITCOIN TRANSACTION ANALYTICS PIPELINE")
    print("=" * 70)

    print(
        "\nStarting complete offline processing pipeline..."
    )

    # -----------------------------------------------------
    # 1. Data ingestion
    # -----------------------------------------------------

    run_step(
        "STEP 1 - DATA INGESTION",
        "ingestion/loader.py"
    )

    # -----------------------------------------------------
    # 2. Validation + Cleaning
    # -----------------------------------------------------

    run_step(
        "STEP 2 - DATA VALIDATION AND CLEANING",
        "preprocessing/cleaner.py"
    )

    # -----------------------------------------------------
    # 3. Geo-IP enrichment
    # -----------------------------------------------------

    run_step(
        "STEP 3 - GEO-IP / ASN ENRICHMENT",
        "geoip/enrichment.py"
    )

    # -----------------------------------------------------
    # 4. Feature engineering
    # -----------------------------------------------------

    run_step(
        "STEP 4 - FEATURE ENGINEERING",
        "features/feature_engineering.py"
    )

    # -----------------------------------------------------
    # 5. Correlation
    # -----------------------------------------------------

    run_step(
        "STEP 5 - IP / TXID / WALLET CORRELATION",
        "correlation/correlate.py"
    )

    # -----------------------------------------------------
    # 6. Graph construction
    # -----------------------------------------------------

    run_step(
        "STEP 6 - ENTITY GRAPH CONSTRUCTION",
        "graph/graph_builder.py"
    )

    # -----------------------------------------------------
    # 7. ML anomaly detection
    # -----------------------------------------------------

    run_step(
        "STEP 7 - AI/ML ANOMALY DETECTION",
        "ml/anomaly_detection.py"
    )

    # -----------------------------------------------------
    # 8. Entity detection
    # -----------------------------------------------------

    run_step(
        "STEP 8 - ENTITY-LEVEL DETECTION",
        "ml/entity_detection.py"
    )
    #-----------------------------------------------------
    # 9. Entity clustering
    # -----------------------------------------------------
    
    run_step(
        "STEP 9 - DBSCAN ENTITY CLUSTERING",
        "ml/clustering.py"
    )

# -----------------------------------------------------
    # 10. Risk scoring
    # -----------------------------------------------------

    run_step(
        "STEP 10 - EXPLAINABLE RISK SCORING",
        "ml/risk_scoring.py"
    )

    # -----------------------------------------------------
    # 11. Model evaluation
    # -----------------------------------------------------

    run_step(
        "STEP 11 - MODEL EVALUATION",
        "ml/evaluate_model.py"
    )

    print("\n")
    print("=" * 70)
    print("🎉 COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 70)

    print(
        "\nProcessed files are available under:"
    )

    print(
        BASE_DIR / "data" / "processed"
    )

    print(
        "\nTo start the dashboard, run:"
    )

    print(
        "streamlit run dashboard/app.py"
    )