from preprocessing.cleaner import parse_list


def test_parse_json_list():

    result = parse_list(
        '["WALLET_A", "WALLET_B"]'
    )

    assert result == [
        "WALLET_A",
        "WALLET_B"
    ]


def test_parse_empty_value():

    result = parse_list(None)

    assert result == []