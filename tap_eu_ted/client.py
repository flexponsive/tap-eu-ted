"""REST client handling, including TendersElectronicDailyStream base class."""

import base64
import math
from typing import Any, Iterable, Optional

import requests
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream


class TendersElectronicDailyStream(RESTStream):
    """TendersElectronicDaily stream class."""

    url_base = "/api/v3.0/notices/search"
    is_sorted = True
    page_size = 100
    current_page = None
    rest_method = "POST"
    records_jsonpath = "$.results[*]"

    primary_keys = ["docid"]
    replication_method = "INCREMENTAL"
    replication_key = "pubdate"

    def get_url(self, context: dict | None) -> str:
        """Search API v3.0 URL."""
        return "https://ted.europa.eu/api/v3.0/notices/search"

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Calculate the next page number required."""
        total_results = response.json()["total"]
        total_pages = math.ceil(total_results / self.page_size)

        next_page = None
        if self.current_page is None:
            next_page = 1
        elif self.current_page < total_pages:
            next_page = self.current_page + 1

        max_pages = self.config["max_pages"]
        if max_pages > 0 and next_page is not None:
            if next_page >= max_pages:
                next_page = None

        return next_page

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare payload with query and pagination."""
        # pagination
        if next_page_token is None:
            next_page_token = 1
        self.current_page = next_page_token

        query = self.config["query"]

        # add starting date to query if incremental import
        if starting_date := self.get_starting_replication_key_value(context):
            ted_formatted_starting_date = starting_date.replace("-", "")
            query = query + f" AND PD=[>=  {ted_formatted_starting_date}]"

        payload = {
            "q": query,
            "fields": ["ND", "PD", "CONTENT"],
            "scope": self.config["scope"],
            "pageNum": self.current_page,
            "pageSize": self.page_size,
            "sortField": "PD",
            "reverseOrder": False,  # this means oldest results first
        }
        self.logger.info(f"TED POST to {self.get_url(context)} payload: '{payload}")
        return payload

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse Response."""
        responseMeta = response.json()
        responseMeta["current_page_results"] = len(responseMeta["results"])
        responseMeta.pop("results")
        self.logger.info(f"TED RESPONSE METADATA: '{responseMeta}")
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """Post-Process, i.e. base64 decode the XML."""
        return {
            "docid": row["ND"],
            "pubdate": row["PD"],
            "xmlbody": base64.b64decode(row["content"]).decode("utf-8"),
        }

    def response_error_message(self, response: requests.Response) -> str:
        """Return error messages from TED API (they are in the body)."""
        return str(response.content)
