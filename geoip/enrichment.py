from pathlib import Path
from ipaddress import ip_address
import maxminddb # pyright: ignore[reportMissingImports]

try:
    import pandas as pd # pyright: ignore[reportMissingModuleSource]
except ImportError:
    pd = None


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

GEOIP_DIR = BASE_DIR / "data" / "geoip"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

COUNTRY_DB = GEOIP_DIR / "dbip-country.mmdb"
ASN_DB = GEOIP_DIR / "dbip-asn.mmdb"


# =========================================================
# IP TYPE CHECK
# =========================================================

def is_public_ip(ip):

    try:
        address = ip_address(str(ip))

        return (
            not address.is_private
            and not address.is_loopback
            and not address.is_reserved
            and not address.is_multicast
            and not address.is_unspecified
        )

    except ValueError:
        return False


# =========================================================
# COUNTRY LOOKUP
# =========================================================

def lookup_country(reader, ip):

    if not is_public_ip(ip):
        return "PRIVATE_OR_RESERVED"

    try:

        result = reader.get(str(ip))

        if not result:
            return "UNKNOWN"

        # DB-IP MMDB structures can vary slightly.
        # Try common country fields.

        country = result.get("country")

        if isinstance(country, dict):

            code = (
                country.get("iso_code")
                or country.get("code")
                or country.get("country_code")
            )

            if code:
                return str(code).upper()

        if isinstance(country, str):
            return country.upper()

    except Exception:
        return "UNKNOWN"

    return "UNKNOWN"


# =========================================================
# ASN LOOKUP
# =========================================================

def lookup_asn(reader, ip):

    if not is_public_ip(ip):
        return "PRIVATE_OR_RESERVED"

    try:

        result = reader.get(str(ip))

        if not result:
            return "UNKNOWN"

        asn = (
            result.get("autonomous_system_number")
            or result.get("asn")
        )

        if asn is not None:

            return f"AS{asn}"

    except Exception:
        return "UNKNOWN"

    return "UNKNOWN"


# =========================================================
# ENRICH DATASET
# =========================================================

def enrich_dataset(df):

    if not COUNTRY_DB.exists():

        raise FileNotFoundError(
            f"Country database not found:\n{COUNTRY_DB}"
        )

    if not ASN_DB.exists():

        raise FileNotFoundError(
            f"ASN database not found:\n{ASN_DB}"
        )

    print("\nOpening local Geo-IP databases...")

    country_reader = maxminddb.open_database(
        str(COUNTRY_DB)
    )

    asn_reader = maxminddb.open_database(
        str(ASN_DB)
    )

    try:

        df = df.copy()

        print("Enriching source IP addresses...")

        df["geo_country_lookup"] = (
            df["src_ip"]
            .apply(
                lambda ip: lookup_country(
                    country_reader,
                    ip
                )
            )
        )

        df["asn_lookup"] = (
            df["src_ip"]
            .apply(
                lambda ip: lookup_asn(
                    asn_reader,
                    ip
                )
            )
        )

        print("Enriching destination IP addresses...")

        df["dst_geo_country_lookup"] = (
            df["dst_ip"]
            .apply(
                lambda ip: lookup_country(
                    country_reader,
                    ip
                )
            )
        )

        df["dst_asn_lookup"] = (
            df["dst_ip"]
            .apply(
                lambda ip: lookup_asn(
                    asn_reader,
                    ip
                )
            )
        )

    finally:

        country_reader.close()
        asn_reader.close()

    return df


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("OFFLINE GEO-IP / ASN ENRICHMENT")
    print("=" * 60)

    input_file = (
        PROCESSED_DIR
        / "bitcoin_transactions_cleaned.csv"
    )

    if not input_file.exists():

        raise FileNotFoundError(
            f"Input file not found:\n{input_file}"
        )

    df = pd.read_csv(input_file)

    print(
        f"\nRecords loaded: {len(df)}"
    )

    enriched_df = enrich_dataset(df)

    output_file = (
        PROCESSED_DIR
        / "bitcoin_transactions_enriched.csv"
    )

    enriched_df.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("ENRICHMENT COMPLETED")
    print("=" * 60)

    print(
        f"\nSaved to:\n{output_file}"
    )

    print("\nSample results:")

    print(
        enriched_df[
            [
                "src_ip",
                "geo_country",
                "asn",
                "geo_country_lookup",
                "asn_lookup",
                "dst_ip",
                "dst_geo_country_lookup",
                "dst_asn_lookup"
            ]
        ].head(10).to_string(
            index=False
        )
    )