import pandas as pd # type: ignore
import json
from pathlib import Path


def parse_list(value):
    """
    Convert address/amount fields into Python lists.

    Handles:
    - already-existing Python lists
    - JSON strings such as '["WALLET_N_0001"]'
    - simple comma-separated strings
    """
    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    if isinstance(value, str):
        value = value.strip()

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

            return [parsed]

        except (json.JSONDecodeError, TypeError):
            if "," in value:
                return [item.strip() for item in value.split(",")]

            return [value]

    return [value]


def normalize_text(value):
    """Normalize text values."""

    if pd.isna(value):
        return ""

    return str(value).strip().upper()


def clean_dataframe(df):
    """
    Clean and normalize the Bitcoin transaction DataFrame.
    """

    print("\n" + "=" * 60)
    print("DATA CLEANING AND NORMALIZATION")
    print("=" * 60)

    df = df.copy()

    # ---------------------------------------------------------
    # 1. Remove completely empty rows
    # ---------------------------------------------------------

    before = len(df)

    df = df.dropna(how="all")

    after = len(df)

    print(f"\nEmpty rows removed: {before - after}")

    # ---------------------------------------------------------
    # 2. Remove duplicate TXIDs
    # ---------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(subset=["txid"], keep="first")

    after = len(df)

    print(f"Duplicate TXIDs removed: {before - after}")

    # ---------------------------------------------------------
    # 3. Normalize timestamp
    # ---------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Remove records with unusable timestamps
    df = df.dropna(subset=["timestamp"])

    # ---------------------------------------------------------
    # 4. Normalize IP addresses
    # ---------------------------------------------------------

    df["src_ip"] = (
        df["src_ip"]
        .astype(str)
        .str.strip()
    )

    df["dst_ip"] = (
        df["dst_ip"]
        .astype(str)
        .str.strip()
    )

    # ---------------------------------------------------------
    # 5. Normalize TXID
    # ---------------------------------------------------------

    df["txid"] = (
        df["txid"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ---------------------------------------------------------
    # 6. Normalize script type, country and ASN
    # ---------------------------------------------------------

    df["script_type"] = df["script_type"].apply(normalize_text)

    df["geo_country"] = df["geo_country"].apply(normalize_text)

    df["asn"] = df["asn"].apply(normalize_text)

    # ---------------------------------------------------------
    # 7. Convert ports to numeric
    # ---------------------------------------------------------

    df["src_port"] = pd.to_numeric(
        df["src_port"],
        errors="coerce"
    )

    df["dst_port"] = pd.to_numeric(
        df["dst_port"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 8. Convert fee to numeric
    # ---------------------------------------------------------

    df["fee"] = pd.to_numeric(
        df["fee"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 9. Parse wallet/address fields
    # ---------------------------------------------------------

    df["input_addresses"] = (
        df["input_addresses"]
        .apply(parse_list)
    )

    df["output_addresses"] = (
        df["output_addresses"]
        .apply(parse_list)
    )

    # ---------------------------------------------------------
    # 10. Parse amount fields
    # ---------------------------------------------------------

    df["input_amounts"] = (
        df["input_amounts"]
        .apply(parse_list)
    )

    df["output_amounts"] = (
        df["output_amounts"]
        .apply(parse_list)
    )

    # Convert all amounts to numeric
    df["input_amounts"] = df["input_amounts"].apply(
        lambda values: [
            float(value)
            for value in values
            if str(value).strip() != ""
        ]
    )

    df["output_amounts"] = df["output_amounts"].apply(
        lambda values: [
            float(value)
            for value in values
            if str(value).strip() != ""
        ]
    )

    # ---------------------------------------------------------
    # 11. Remove impossible negative monetary values
    # ---------------------------------------------------------

    df["input_amounts"] = df["input_amounts"].apply(
        lambda values: [x for x in values if x >= 0]
    )

    df["output_amounts"] = df["output_amounts"].apply(
        lambda values: [x for x in values if x >= 0]
    )

    df.loc[df["fee"] < 0, "fee"] = None

    # ---------------------------------------------------------
    # 12. Create transaction-level derived fields
    # ---------------------------------------------------------

    df["input_count"] = (
        df["input_addresses"]
        .apply(len)
    )

    df["output_count"] = (
        df["output_addresses"]
        .apply(len)
    )

    df["total_input"] = (
        df["input_amounts"]
        .apply(sum)
    )

    df["total_output"] = (
        df["output_amounts"]
        .apply(sum)
    )

    # Amount transferred
    df["transaction_amount"] = df["total_output"]

    # ---------------------------------------------------------
    # 13. Reorder columns
    # ---------------------------------------------------------

    columns = [
        "timestamp",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "txid",
        "input_addresses",
        "output_addresses",
        "input_amounts",
        "output_amounts",
        "input_count",
        "output_count",
        "total_input",
        "total_output",
        "transaction_amount",
        "fee",
        "script_type",
        "geo_country",
        "asn",
        "synthetic_scenario"
    ]

    # Keep only columns that actually exist
    columns = [
        column for column in columns
        if column in df.columns
    ]

    df = df[columns]

    # ---------------------------------------------------------
    # 14. Reset index
    # ---------------------------------------------------------

    df = df.reset_index(drop=True)

    print("\nCleaning completed successfully.")

    print(f"Final records: {len(df)}")
    print(f"Final columns: {len(df.columns)}")

    return df


def save_cleaned_data(df):

    base_dir = Path(__file__).resolve().parent.parent

    processed_dir = base_dir / "data" / "processed"

    processed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        processed_dir /
        "bitcoin_transactions_cleaned.csv"
    )

    # Lists are converted to JSON strings for CSV storage
    output_df = df.copy()

    list_columns = [
        "input_addresses",
        "output_addresses",
        "input_amounts",
        "output_amounts"
    ]

    for column in list_columns:
        if column in output_df.columns:
            output_df[column] = output_df[column].apply(
                json.dumps
            )

    output_df.to_csv(
        output_file,
        index=False
    )

    print(f"\n✅ Cleaned dataset saved to:")
    print(output_file)

    return output_file
if __name__ == "__main__":

    # Import the loader
    import sys

    sys.path.append(
        str(Path(__file__).resolve().parent.parent)
    )

    from ingestion.loader import load_dataset

    base_dir = Path(__file__).resolve().parent.parent

    input_file = (
        base_dir /
        "data" /
        "raw" /
        "bitcoin_transactions.csv"
    )

    print(f"Loading: {input_file}")

    # Load raw data
    df = load_dataset(input_file)

    print(f"Raw records: {len(df)}")

    # Clean data
    cleaned_df = clean_dataframe(df)

    # Save cleaned data
    save_cleaned_data(cleaned_df)

    print("\nFirst 5 cleaned records:")
    print(cleaned_df.head())