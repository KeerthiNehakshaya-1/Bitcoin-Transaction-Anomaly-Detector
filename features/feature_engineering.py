import pandas as pd  # type: ignore[reportMissingImports]
import json
from pathlib import Path


# ---------------------------------------------------------
# Utility function
# ---------------------------------------------------------

def parse_list(value):
    """
    Convert a JSON string back into a Python list.
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


# ---------------------------------------------------------
# Load cleaned dataset
# ---------------------------------------------------------

def load_cleaned_data():

    base_dir = Path(__file__).resolve().parent.parent

    file_path = (
        base_dir
        / "data"
        / "processed"
        / "bitcoin_transactions_enriched.csv"
    )

    print(f"Loading cleaned dataset:")
    print(file_path)

    df = pd.read_csv(file_path)

    return df


# ---------------------------------------------------------
# Prepare data types
# ---------------------------------------------------------

def prepare_data(df):

    df = df.copy()

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Convert list-like columns
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


# ---------------------------------------------------------
# Transaction-level features
# ---------------------------------------------------------

def create_transaction_features(df):

    print("\nCreating transaction-level features...")

    df = df.copy()
        # Make sure timestamp is datetime before using .dt
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # Time features
    # -----------------------------------------------------

    df["transaction_hour"] = (
        df["timestamp"].dt.hour
    )

    df["transaction_day"] = (
        df["timestamp"].dt.day
    )

    df["transaction_day_of_week"] = (
        df["timestamp"].dt.dayofweek
    )

    df["transaction_month"] = (
        df["timestamp"].dt.month
    )

    # -----------------------------------------------------
    # Address counts
    # -----------------------------------------------------

    df["input_count"] = (
        df["input_addresses"].apply(len)
    )

    df["output_count"] = (
        df["output_addresses"].apply(len)
    )

    # -----------------------------------------------------
    # Amount calculations
    # -----------------------------------------------------

    df["total_input"] = (
        df["input_amounts"].apply(
            lambda x: sum(float(v) for v in x)
        )
    )

    df["total_output"] = (
        df["output_amounts"].apply(
            lambda x: sum(float(v) for v in x)
        )
    )

    df["transaction_amount"] = (
        df["total_output"]
    )

    # -----------------------------------------------------
    # Input-output difference
    # -----------------------------------------------------

    df["input_output_difference"] = (
        df["total_input"]
        - df["total_output"]
    )

    # -----------------------------------------------------
    # Fee ratio
    # -----------------------------------------------------

    df["fee_ratio"] = (
        df["fee"]
        / (df["total_output"] + 1e-9)
    )

    # -----------------------------------------------------
    # Transaction amount per output
    # -----------------------------------------------------

    df["average_output_amount"] = (
        df["total_output"]
        / (df["output_count"] + 1e-9)
    )

    # -----------------------------------------------------
    # Transaction amount per input
    # -----------------------------------------------------

    df["average_input_amount"] = (
        df["total_input"]
        / (df["input_count"] + 1e-9)
    )

    print("Transaction-level features created.")

    return df


# ---------------------------------------------------------
# Wallet-level behavioral features
# ---------------------------------------------------------

def create_wallet_features(df):

    print("\nCreating wallet-level behavioral features...")

    # Each row can contain multiple wallet addresses.
    # For this synthetic dataset, flatten input/output wallets.

    wallet_records = []

    for _, row in df.iterrows():

        input_wallets = row["input_addresses"]
        output_wallets = row["output_addresses"]

        all_wallets = set(
            input_wallets + output_wallets
        )

        for wallet in all_wallets:

            wallet_records.append({
                "wallet": wallet,
                "txid": row["txid"],
                "src_ip": row["src_ip"],
                "dst_ip": row["dst_ip"],
                "counterparty_wallets":
                    list(
                        (
                            set(input_wallets)
                            | set(output_wallets)
                        )
                        - {wallet}
                    )
            })

    wallet_df = pd.DataFrame(wallet_records)

    if wallet_df.empty:
        return df

    # -----------------------------------------------------
    # Number of transactions involving wallet
    # -----------------------------------------------------

    wallet_tx_count = (
        wallet_df.groupby("wallet")
        .size()
        .rename("wallet_transaction_count")
    )

    # -----------------------------------------------------
    # Number of unique IPs
    # -----------------------------------------------------

    wallet_unique_ips = (
        wallet_df.groupby("wallet")["src_ip"]
        .nunique()
        .rename("wallet_unique_ips")
    )

    # -----------------------------------------------------
    # Number of unique transactions
    # -----------------------------------------------------

    wallet_unique_txids = (
        wallet_df.groupby("wallet")["txid"]
        .nunique()
        .rename("wallet_unique_txids")
    )

    # -----------------------------------------------------
    # Number of unique counterparties
    # -----------------------------------------------------

    counterparty_map = {}

    for wallet, group in wallet_df.groupby("wallet"):

        counterparties = set()

        for values in group["counterparty_wallets"]:

            counterparties.update(values)

        counterparty_map[wallet] = len(counterparties)

    wallet_counterparties = pd.Series(
        counterparty_map,
        name="wallet_unique_counterparties"
    )

    wallet_stats = pd.concat(
        [
            wallet_tx_count,
            wallet_unique_ips,
            wallet_unique_txids,
            wallet_counterparties
        ],
        axis=1
    )

    # Make sure the index is explicitly named "wallet"
    wallet_stats.index.name = "wallet"

    wallet_stats = wallet_stats.reset_index()

    # -----------------------------------------------------
    # Add features to transaction rows
    # -----------------------------------------------------

    # Use first input wallet as representative wallet
    df["primary_wallet"] = df[
        "input_addresses"
    ].apply(
        lambda x: x[0] if len(x) > 0 else "UNKNOWN"
    )

    df = df.merge(
        wallet_stats,
        left_on="primary_wallet",
        right_on="wallet",
        how="left"
    )

    df.drop(
        columns=["wallet"],
        inplace=True
    )

    print("Wallet-level features created.")

    return df


# ---------------------------------------------------------
# IP-level behavioral features
# ---------------------------------------------------------

def create_ip_features(df):

    print("\nCreating IP-level behavioral features...")

    ip_stats = (
        df.groupby("src_ip")
        .agg(
            ip_transaction_count=("txid", "count"),
            ip_unique_wallets=("primary_wallet", "nunique"),
            ip_unique_txids=("txid", "nunique"),
            ip_unique_destinations=("dst_ip", "nunique")
        )
        .reset_index()
    )

    df = df.merge(
        ip_stats,
        on="src_ip",
        how="left"
    )

    print("IP-level features created.")

    return df


# ---------------------------------------------------------
# Temporal behavior features
# ---------------------------------------------------------

def create_temporal_features(df):

    print("\nCreating temporal features...")

    df = df.sort_values("timestamp").copy()

    # Time since previous transaction from same IP
    df["seconds_since_previous_ip_tx"] = (
        df.groupby("src_ip")["timestamp"]
        .diff()
        .dt.total_seconds()
    )

    # Time since previous transaction involving primary wallet
    df["seconds_since_previous_wallet_tx"] = (
        df.groupby("primary_wallet")["timestamp"]
        .diff()
        .dt.total_seconds()
    )

    # Missing differences mean first transaction
    df["seconds_since_previous_ip_tx"] = (
        df["seconds_since_previous_ip_tx"]
        .fillna(-1)
    )

    df["seconds_since_previous_wallet_tx"] = (
        df["seconds_since_previous_wallet_tx"]
        .fillna(-1)
    )

    print("Temporal features created.")

    return df
def create_geoip_features(df):
    """
    Create features from Geo-IP and ASN enrichment.
    """

    print("\nCreating Geo-IP / ASN features...")

    df = df.copy()

    # -----------------------------------------------------
    # Normalize enrichment fields
    # -----------------------------------------------------

    geo_columns = [
        "geo_country_lookup",
        "asn_lookup",
        "dst_geo_country_lookup",
        "dst_asn_lookup"
    ]

    for column in geo_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna("UNKNOWN")
                .astype(str)
                .str.strip()
                .str.upper()
            )

    # -----------------------------------------------------
    # Cross-country transaction
    # -----------------------------------------------------

    if (
        "geo_country_lookup" in df.columns
        and
        "dst_geo_country_lookup" in df.columns
    ):

        df["cross_country_transaction"] = (
            (
                df["geo_country_lookup"]
                != df["dst_geo_country_lookup"]
            )
            &
            (df["geo_country_lookup"] != "UNKNOWN")
            &
            (df["dst_geo_country_lookup"] != "UNKNOWN")
            &
            (df["geo_country_lookup"] != "PRIVATE_OR_RESERVED")
            &
            (df["dst_geo_country_lookup"] != "PRIVATE_OR_RESERVED")
        ).astype(int)

    else:

        df["cross_country_transaction"] = 0

    # -----------------------------------------------------
    # Cross-ASN transaction
    # -----------------------------------------------------

    if (
        "asn_lookup" in df.columns
        and
        "dst_asn_lookup" in df.columns
    ):

        df["cross_asn_transaction"] = (
            (
                df["asn_lookup"]
                != df["dst_asn_lookup"]
            )
            &
            (df["asn_lookup"] != "UNKNOWN")
            &
            (df["dst_asn_lookup"] != "UNKNOWN")
            &
            (df["asn_lookup"] != "PRIVATE_OR_RESERVED")
            &
            (df["dst_asn_lookup"] != "PRIVATE_OR_RESERVED")
        ).astype(int)

    else:

        df["cross_asn_transaction"] = 0

    # -----------------------------------------------------
    # Unique countries observed per source IP
    # -----------------------------------------------------

    if "geo_country_lookup" in df.columns:

        country_counts = (
            df.groupby("src_ip")[
                "geo_country_lookup"
            ]
            .nunique()
            .rename("ip_unique_countries")
        )

        df = df.merge(
            country_counts,
            on="src_ip",
            how="left"
        )

    else:

        df["ip_unique_countries"] = 0

    # -----------------------------------------------------
    # Unique ASNs observed per source IP
    # -----------------------------------------------------

    if "asn_lookup" in df.columns:

        asn_counts = (
            df.groupby("src_ip")[
                "asn_lookup"
            ]
            .nunique()
            .rename("ip_unique_asns")
        )

        df = df.merge(
            asn_counts,
            on="src_ip",
            how="left"
        )

    else:

        df["ip_unique_asns"] = 0

    # -----------------------------------------------------
    # Numeric conversion
    # -----------------------------------------------------

    df["ip_unique_countries"] = (
        pd.to_numeric(
            df["ip_unique_countries"],
            errors="coerce"
        )
        .fillna(0)
    )

    df["ip_unique_asns"] = (
        pd.to_numeric(
            df["ip_unique_asns"],
            errors="coerce"
        )
        .fillna(0)
    )

    print("Geo-IP / ASN features created.")

    return df


# ---------------------------------------------------------
# Final feature dataset
# ---------------------------------------------------------

def create_features(df):

    df = prepare_data(df)

    df = create_transaction_features(df)

    df = create_wallet_features(df)

    df = create_ip_features(df)

    df = create_temporal_features(df)

    df = create_geoip_features(df)

    return df


# ---------------------------------------------------------
# Save feature dataset
# ---------------------------------------------------------

def save_features(df):

    base_dir = Path(__file__).resolve().parent.parent

    processed_dir = (
        base_dir
        / "data"
        / "processed"
    )

    processed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        processed_dir
        / "bitcoin_transactions_features.csv"
    )

    # Convert list columns to JSON before CSV storage
    output_df = df.copy()

    list_columns = [
        "input_addresses",
        "output_addresses",
        "input_amounts",
        "output_amounts"
    ]

    for column in list_columns:

        if column in output_df.columns:

            output_df[column] = (
                output_df[column]
                .apply(json.dumps)
            )

    output_df.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("FEATURE DATASET SAVED")
    print("=" * 60)

    print(output_file)

    return output_file


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("BITCOIN FEATURE ENGINEERING")
    print("=" * 60)

    # Load
    df = load_cleaned_data()

    print(f"\nInput records: {len(df)}")

    # Create features
    feature_df = create_features(df)

    print(
        f"Output records: {len(feature_df)}"
    )

    print(
        f"Output columns: {len(feature_df.columns)}"
    )

    # Save
    save_features(feature_df)

    print("\nFeature engineering completed.")

    print("\nSelected features:")

    selected_columns = [
        "txid",
        "transaction_amount",
        "fee",
        "input_count",
        "output_count",
        "wallet_transaction_count",
        "wallet_unique_ips",
        "wallet_unique_counterparties",
        "ip_transaction_count",
        "ip_unique_wallets",
        "seconds_since_previous_ip_tx"
    ]

    available_columns = [
        c for c in selected_columns
        if c in feature_df.columns
    ]

    print(
        feature_df[available_columns].head(10)
    )


