from palworld_exporter.providers.util import hex_uid_to_decimal


def test_hex_uid_to_decimal():
    assert hex_uid_to_decimal('3C291D4D000000000000000000000000') == '1009327437'
    assert hex_uid_to_decimal('FBB2E40C000000000000000000000000') == '4222805004'


def test_hex_uid_to_decimal_ignores_trailing_chars():
    # Only the first 8 hex chars are the meaningful uid prefix
    assert hex_uid_to_decimal('3C291D4D') == hex_uid_to_decimal(
        '3C291D4DFFFFFFFFFFFFFFFFFFFFFFFF')
