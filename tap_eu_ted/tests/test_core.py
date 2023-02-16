"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_tap_test_class

from tap_eu_ted.tap import TapTendersElectronicDaily

SAMPLE_CONFIG = {
    # test query: IT consulting contracts, open procedure, in cyprus
    "query": "PC=[72000000] AND PR=[open] AND RC=[CYP]",
    "start_date": "2023-01-01"
}

# Run standard built-in tap tests from the SDK:
TestTapTendersElectronicDaily = get_tap_test_class(
    tap_class=TapTendersElectronicDaily, config=SAMPLE_CONFIG
)
