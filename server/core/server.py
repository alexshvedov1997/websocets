import asyncio
import json
import logging
import sys
from asyncio.streams import StreamReader, StreamWriter

from core.controller import Controller
from core.schemas import HTTPResponse, RequestSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Server:

    def __init__(self, host="127.0.0.1", port=8001):
        self._controller = Controller()
        self._server_host = host
        self._server_port = port

    async def listen(self, reader: StreamReader, writer: StreamWriter):
        while True:
            try:
                http_response = ""
                data = await reader.read(1024)
                if not data:
                    break
                logger.info("Request data {}".format(data))
                request_data = RequestSchema(raw_data=data.decode('utf8'))
                if request_data.endpoint == "/connect":
                    json_data = await self._controller.connect(request_data.json_data)
                    http_response = HTTPResponse(
                        200,
                        content_type='application/json',
                        body=json.dumps(json_data)).to_string()
                elif request_data.endpoint == "/message":
                    json_data = await self._controller.create_message(request_data.json_data)
                elif request_data.endpoint == "/comment":
                    json_data = await self._controller.comment_message(request_data.json_data)
                elif request_data.endpoint == "/report":
                    json_data = await self._controller.report_user(request_data.json_data)
                elif request_data.endpoint == "/status":
                    json_data = await self._controller.check_status(request_data.json_data)
                    http_response = HTTPResponse(
                        200,
                        content_type='application/json',
                        body=json.dumps(json_data)).to_string()
                logger.info("Response data {}".format(http_response))
                writer.write(http_response.encode("utf-8"))
                await writer.drain()
            except Exception as e:
                print(e)
            finally:
                writer.close()

    async def run(self):
        srv = await asyncio.start_server(
            self.listen,
            self._server_host,
            self._server_port,
        )

        async with srv:
            await srv.serve_forever()
