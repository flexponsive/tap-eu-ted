"""Stream type classes for tap-eu-ted."""

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_eu_ted.client import TendersElectronicDailyStream


class DocumentsStream(TendersElectronicDailyStream):
    """Define custom stream."""

    name = "documents"
    path = ""
    primary_keys = ["docid"]
    replication_method = "INCREMENTAL"
    replication_key = "pubdate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("docid", th.StringType, description="TED DocID"),
        th.Property("pubdate", th.DateType, description="Publication Day"),
        th.Property("xmlbody", th.StringType, description="XML Body"),
    ).to_dict()
