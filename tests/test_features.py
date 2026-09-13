import pandas as pd

from features.feature_engineering import (
    create_transaction_features
)


def test_transaction_features():

    df = pd.DataFrame({
        "timestamp": [
            "2026-01-01 12:00:00"
        ],
        "input_addresses": [
            ["WALLET_A"]
        ],
        "output_addresses": [
            ["WALLET_B"]
        ],
        "input_amounts": [
            [1.1]
        ],
        "output_amounts": [
            [1.0]
        ],
        "fee": [
            0.1
        ]
    })

    result = create_transaction_features(df)

    assert "input_count" in result.columns
    assert "output_count" in result.columns
    assert "transaction_amount" in result.columns

    assert result.iloc[0]["input_count"] == 1
    assert result.iloc[0]["output_count"] == 1
    assert result.iloc[0]["transaction_amount"] == 1.0