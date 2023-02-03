"""REST client handling, including TendersElectronicDailyStream base class."""

from backoff.types import Details
from pprint import pprint
import math
import base64
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream


class TendersElectronicDailyStream(RESTStream):
    """TendersElectronicDaily stream class."""

    url_base = "/api/v3.0/notices/search"
    page_size = 100
    current_page = None
    rest_method = "POST"
    records_jsonpath = "$.results[*]"

    def get_url(self, context: dict | None) -> str:
        return "https://ted.europa.eu/api/v3.0/notices/search"

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        total_results = response.json()["total"]
        total_pages = math.ceil(total_results / self.page_size)
        if self.current_page < total_pages:
            return self.current_page + 1
        else:
            return None

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        
        # pagination
        if next_page_token is None:
            next_page_token = 1

        self.current_page = next_page_token

        query = self.config["query"]

        # add starting date to query if incremental import
        if starting_date := self.get_starting_replication_key_value(context):
            ted_formatted_starting_date = starting_date.replace("-", "")
            query = query + f" PD=[>=  {ted_formatted_starting_date}]"
        
        payload = {
            "q": query,
            "fields": ["ND", "PD", "CONTENT" ], 
            "scope": self.config["scope"],
            "pageNum": 1,
            "pageSize": self.page_size,
        }
        self.logger.info(f"TED POST to {self.get_url(context)} payload: '{payload}")
        return payload

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        return {
            "docid": row["ND"],
            "pubdate": row["PD"],
            "xmlbody": base64.b64decode(row["content"]).decode('utf-8'),
        }

    def response_error_message(self, response: requests.Response) -> str:
        # error messages are returned by the TED API in the body
        return response.content