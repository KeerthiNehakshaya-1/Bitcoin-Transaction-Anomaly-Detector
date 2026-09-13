import pandas as pd

from preprocessing.validation import (
    check_required_columns,
    is_valid_ip
)


def test_valid_ip():

    assert is_valid_ip("8.8.8.8") is True


def test_invalid_ip():

    assert is_valid_ip("not_an_ip") is False


def test_required_columns():

    df = pd.DataFrame({
        "timestamp": [],
        "src_ip": [],
        "dst_ip": [],
        "src_port": [],
        "dst_port": [],
        "txid": [],
        "input_addresses": [],
        "output_addresses": [],
        "input_amounts": [],
        "output_amounts": [],
        "fee": [],
        "script_type": [],
        "geo_country": [],
        "asn": []
    })

    assert check_required_columns(df) is True