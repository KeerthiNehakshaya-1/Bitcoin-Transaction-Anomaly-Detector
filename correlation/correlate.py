import json
from pathlib import Path

try:
    import pandas as pd  # type: ignore[import-not-found]
except ModuleNotFoundError:
    pd = None


def parse_list(value):
    """
    Convert a JSON string into a Python list.
    """

    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return [result]

    except (json.JSONDecodeError, TypeError):
        return []


def load_feature_data():
    """
    Load the feature-engineered dataset.
    """

    base_dir = Path(__file__).resolve().parent.parent

    file_path = (
        base_dir
        / "data"
        / "processed"
        / "bitcoin_transactions_features.csv"
    )

    print(f"Loading feature dataset:")
    print(file_path)

    return pd.read_csv(file_path)


def prepare_data(df):

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    list_columns = [
        "input_addresses",
        "output_addresses",
        "input_amounts",
        "output_amounts"
    ]

    for column in list_columns:

        if column in df.columns:
            df[column] = df[column].apply(parse_list)

    return df


def create_correlation_table(df):

    print("\nCreating IP-TXID-Wallet correlations...")

    records = []

    for _, row in df.iterrows():

        input_wallets = row["input_addresses"]
        output_wallets = row["output_addresses"]

        input_amounts = row["input_amounts"]
        output_amounts = row["output_amounts"]

        # Make sure at least one value exists
        if not input_wallets:
            input_wallets = ["UNKNOWN_INPUT"]

        if not output_wallets:
            output_wallets = ["UNKNOWN_OUTPUT"]

        # Create relationships between input and output wallets
        for input_wallet in input_wallets:

            for output_wallet in output_wallets:

                records.append({
                    "timestamp": row["timestamp"],
                    "src_ip": row["src_ip"],
                    "dst_ip": row["dst_ip"],
                    "src_port": row["src_port"],
                    "dst_port": row["dst_port"],
                    "txid": row["txid"],
                    "input_wallet": input_wallet,
                    "output_wallet": output_wallet,
                    "input_amounts": input_amounts,
                    "output_amounts": output_amounts,
                    "transaction_amount": row[
                        "transaction_amount"
                    ],
                    "fee": row["fee"],
                    "script_type": row["script_type"],
                    "geo_country": row["geo_country"],
                    "asn": row["asn"]
                })

    correlation_df = pd.DataFrame(records)

    return correlation_df


def create_ip_summary(correlation_df):

    """
    Summarize relationships observed for each IP.
    """

    ip_summary = (
        correlation_df
        .groupby("src_ip")
        .agg(
            transaction_count=("txid", "nunique"),
            unique_wallets=(
                "input_wallet",
                "nunique"
            ),
            unique_destinations=(
                "dst_ip",
                "nunique"
            ),
            total_transaction_value=(
                "transaction_amount",
                "sum"
            )
        )
        .reset_index()
    )

    return ip_summary


def create_wallet_summary(correlation_df):

    """
    Summarize relationships observed for each wallet.
    """

    input_summary = (
        correlation_df
        .groupby("input_wallet")
        .agg(
            transactions_as_input=("txid", "nunique"),
            unique_ips=("src_ip", "nunique"),
            unique_output_wallets=(
                "output_wallet",
                "nunique"
            ),
            total_value_sent=(
                "transaction_amount",
                "sum"
            )
        )
        .reset_index()
        .rename(
            columns={
                "input_wallet": "wallet"
            }
        )
    )

    return input_summary


def save_results(
    correlation_df,
    ip_summary,
    wallet_summary
):

    base_dir = Path(__file__).resolve().parent.parent

    output_dir = (
        base_dir
        / "data"
        / "processed"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Correlation table
    correlation_file = (
        output_dir
        / "ip_txid_wallet_correlation.csv"
    )

    correlation_df.to_csv(
        correlation_file,
        index=False
    )

    # IP summary
    ip_file = (
        output_dir
        / "ip_relationship_summary.csv"
    )

    ip_summary.to_csv(
        ip_file,
        index=False
    )

    # Wallet summary
    wallet_file = (
        output_dir
        / "wallet_relationship_summary.csv"
    )

    wallet_summary.to_csv(
        wallet_file,
        index=False
    )

    print("\nFiles created:")

    print(correlation_file)
    print(ip_file)
    print(wallet_file)


if __name__ == "__main__":

    print("=" * 60)
    print("BITCOIN NETWORK-BLOCKCHAIN CORRELATION")
    print("=" * 60)

    # Load
    df = load_feature_data()

    print(f"\nRecords loaded: {len(df)}")

    # Prepare
    df = prepare_data(df)

    # Correlate
    correlation_df = create_correlation_table(df)

    print(
        f"Correlation records: {len(correlation_df)}"
    )

    # Create summaries
    ip_summary = create_ip_summary(
        correlation_df
    )

    wallet_summary = create_wallet_summary(
        correlation_df
    )

    # Save
    save_results(
        correlation_df,
        ip_summary,
        wallet_summary
    )

    print("\n" + "=" * 60)
    print("CORRELATION COMPLETED")
    print("=" * 60)

    print("\nSample correlations:")
    print(
        correlation_df[
            [
                "timestamp",
                "src_ip",
                "txid",
                "input_wallet",
                "output_wallet",
                "transaction_amount"
            ]
        ].head(10)
    )