try:
    import pandas as pd  # type: ignore[import-not-found]
except ModuleNotFoundError:
    pd = None  # type: ignore[assignment]
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def main():

    alert_file = PROCESSED_DIR / "prioritized_alerts.csv"

    if not alert_file.exists():
        print("❌ prioritized_alerts.csv not found")
        return

    alerts = pd.read_csv(alert_file)

    print("=" * 60)
    print("FINAL PIPELINE TEST")
    print("=" * 60)

    print(f"\nTotal alerts: {len(alerts)}")

    required_columns = [
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
        for column in required_columns
        if column not in alerts.columns
    ]

    if missing:
        print("\n❌ Missing columns:")
        print(missing)
    else:
        print("\n✅ Alert columns verified")

    # -------------------------------------------------
    # Check risk-score range
    # -------------------------------------------------

    invalid_scores = (
        (alerts["risk_score"] < 0)
        |
        (alerts["risk_score"] > 100)
    ).sum()

    if invalid_scores == 0:
        print("✅ Risk scores are within 0-100")
    else:
        print(
            f"❌ Invalid risk scores: {invalid_scores}"
        )

    # -------------------------------------------------
    # Check explanations
    # -------------------------------------------------

    missing_evidence = (
        alerts["evidence"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    if missing_evidence == 0:
        print("✅ All alerts contain explanations")
    else:
        print(
            f"❌ Alerts without explanations: "
            f"{missing_evidence}"
        )

    # -------------------------------------------------
    # Check injected anomalous IP
    # -------------------------------------------------

    target_ip = "172.16.50.1"

    ip_match = alerts[
        alerts["entity"].astype(str) == target_ip
    ]

    if not ip_match.empty:

        row = ip_match.iloc[0]

        print("\n✅ Injected anomalous IP detected")

        print(
            f"IP: {target_ip}"
        )

        print(
            f"Risk score: {row['risk_score']}"
        )

        print(
            f"Risk level: {row['risk_level']}"
        )

        print(
            f"Evidence: {row['evidence']}"
        )

    else:

        print(
            "\n⚠️ Injected anomalous IP was not "
            "found in the alert list."
        )

    # -------------------------------------------------
    # Show top 10
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("TOP 10 ALERTS")
    print("=" * 60)

    print(
        alerts[
            [
                "priority_rank",
                "entity_type",
                "entity",
                "risk_score",
                "risk_level"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()