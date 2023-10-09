import json
import re
from dataclasses import dataclass, field
from typing import Optional

JSON_PATTERN = r'\{.*\}$'


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


class HTTPResponse:
    def __init__(
            self,
            status_code: int = 200,
            content_type: str = 'text/html',
            body: str = ''
    ):
        self.status_code = status_code
        self.content_type = content_type
        self.body = body

    def to_string(self) -> str:
        response = f"HTTP/1.1 {self.status_code} {self.get_status_text(self.status_code)}\r\n"
        response += f"Content-Type: {self.content_type}\r\n"
        response += f"Content-Length: {len(self.body)}\r\n\r\n"
        response += self.body
        return response

    @staticmethod
    def get_status_text(status_code: int) -> str:
        status_text = {
            200: 'OK',
            404: 'Not Found',
            201: "Created"
        }
        return status_text.get(status_code, 'Unknown')
