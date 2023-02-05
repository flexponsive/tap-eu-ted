"""TendersElectronicDaily tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_eu_ted.streams import DocumentsStream

# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [DocumentsStream]


class TapTendersElectronicDaily(Tap):
    """TendersElectronicDaily tap class."""

    name = "tap-eu-ted"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "query",
            th.StringType,
            required=True,
            description="The TED Expert Search Query to select results",
        ),
        th.Property(
            "scope", th.IntegerType, default=3, description="document scope (3 = all)"
        ),
        th.Property(
            "max_pages",
            th.IntegerType,
            default=0,
            description="stop tap when max pages is reached",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapTendersElectronicDaily.cli()
