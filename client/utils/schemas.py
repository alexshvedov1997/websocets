import json
import re
from dataclasses import dataclass, field
from typing import Optional

JSON_PATTERN = r'\{.*\}$'


class SocketRequest:

    def generate_request(self, method: str, uri: str, json_data: dict) -> str:
        request_data = "{method} {uri} HTTP/1.1\r\n\r\n".format(
            method=method,
            uri=uri,
        )
        request_data += json.dumps(json_data)
        return request_data


@dataclass
class RequestSchema:
    raw_data: str = field(repr=False)
    host: Optional[str] = field(repr=False, default=None)
    http_method: Optional[str] = field(repr=False, default=None)
    endpoint: Optional[str] = field(repr=False, default=None)
    json_data: Optional[dict] = field(repr=False, default=None)

    def __post_init__(self) -> None:
        self.__do_parse()

    def __do_parse(self) -> None:
        lines = self.raw_data.split('\n')
        method, uri, http_version = lines[0].split()
        self.http_method = method
        self.endpoint = uri
        match = re.search(JSON_PATTERN, self.raw_data, re.DOTALL)
        if match:
            self.json_data = json.loads(match.group(0))
