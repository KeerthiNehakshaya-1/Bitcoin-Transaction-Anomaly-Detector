try:
    import pandas as pd  # type: ignore[reportMissingImports]
except ImportError as exc:
    raise ImportError(
        "pandas is required to validate the Bitcoin dataset. Install it with 'pip install pandas'."
    ) from exc

from ipaddress import ip_address


# Required fields according to the NTRO problem statement
REQUIRED_COLUMNS = [
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
    "fee",
    "script_type",
    "geo_country",
    "asn"
]


def check_required_columns(df):
    """Check whether all required columns are present."""

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing:
        print("❌ Missing columns:")
        for column in missing:
            print(f"   - {column}")
        return False

    print("✅ All required columns are present.")
    return True


def check_missing_values(df):
    """Check important fields for missing values."""

    important_columns = [
        "timestamp",
        "src_ip",
        "dst_ip",
        "txid",
        "fee"
    ]

    print("\nMissing values:")

    has_missing = False

    for column in important_columns:
        count = df[column].isna().sum()

        if count > 0:
            print(f"⚠️ {column}: {count}")
            has_missing = True
        else:
            print(f"✅ {column}: 0")

    return not has_missing


def is_valid_ip(value):
    """Return True if value is a valid IP address."""

    try:
        ip_address(str(value))
        return True
    except ValueError:
        return False


def check_ip_addresses(df):
    """Validate source and destination IP addresses."""

    invalid_src = (~df["src_ip"].apply(is_valid_ip)).sum()
    invalid_dst = (~df["dst_ip"].apply(is_valid_ip)).sum()

    print("\nIP address validation:")

    print(f"✅ Invalid source IPs: {invalid_src}")
    print(f"✅ Invalid destination IPs: {invalid_dst}")

    return invalid_src == 0 and invalid_dst == 0


def check_ports(df):
    """Validate source and destination ports."""

    src_ports = pd.to_numeric(df["src_port"], errors="coerce")
    dst_ports = pd.to_numeric(df["dst_port"], errors="coerce")

    invalid_src = ((src_ports < 0) | (src_ports > 65535)).sum()
    invalid_dst = ((dst_ports < 0) | (dst_ports > 65535)).sum()

    print("\nPort validation:")

    print(f"✅ Invalid source ports: {invalid_src}")
    print(f"✅ Invalid destination ports: {invalid_dst}")

    return invalid_src == 0 and invalid_dst == 0


def check_numeric_fields(df):
    """Check whether amounts and fees are numeric."""

    numeric_columns = [
        "fee"
    ]

    print("\nNumeric field validation:")

    valid = True

    for column in numeric_columns:
        converted = pd.to_numeric(df[column], errors="coerce")
        invalid = converted.isna().sum()

        if invalid > 0:
            print(f"❌ {column}: {invalid} invalid values")
            valid = False
        else:
            print(f"✅ {column}: all values numeric")

    return valid


def check_timestamps(df):
    """Check whether timestamps can be parsed."""

    converted = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid = converted.isna().sum()

    print("\nTimestamp validation:")

    if invalid == 0:
        print("✅ All timestamps are valid.")
    else:
        print(f"❌ Invalid timestamps: {invalid}")

    return invalid == 0


def check_duplicate_txids(df):
    """Check for duplicate transaction IDs."""

    duplicates = df["txid"].duplicated().sum()

    print("\nTXID validation:")

    if duplicates == 0:
        print("✅ No duplicate TXIDs found.")
    else:
        print(f"⚠️ Duplicate TXIDs found: {duplicates}")

    return duplicates == 0


def validate_dataframe(df):
    """Run all validation checks."""

    print("\n" + "=" * 60)
    print("BITCOIN DATASET VALIDATION")
    print("=" * 60)

    results = []

    results.append(check_required_columns(df))
    results.append(check_missing_values(df))
    results.append(check_ip_addresses(df))
    results.append(check_ports(df))
    results.append(check_numeric_fields(df))
    results.append(check_timestamps(df))
    results.append(check_duplicate_txids(df))

    print("\n" + "=" * 60)

    if all(results):
        print("✅ DATASET PASSED VALIDATION")
    else:
        print("⚠️ DATASET NEEDS CLEANING")

    print("=" * 60)

    return all(results)