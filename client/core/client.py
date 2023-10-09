import asyncio
import datetime
import json
import logging
import sys
import uuid
from typing import Optional

import requests
from aioconsole import ainput

from core.handler import Handler
from utils.schemas import SocketRequest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

RETRY = 3


class Client:

    def __init__(self, server_host="127.0.0.1", server_port=8001, limit_message=20):
        self._client_uuid = None
        self._client_name = None
        self._is_blocked = False
        self._server_host = server_host
        self._server_port = server_port
        self._limit_message = limit_message
        self._message_counter = 0
        self._datetime_to_clear = None
        self._last_message_datetime = None
        self.datetime_banned = None

    def generate_user_uid(self) -> None:
        self._client_uuid = uuid.uuid4()

    def __server_url(self) -> str:
        return "http://{host}:{port}".format(
            host=self._server_host,
            port=self._server_port,
        )

    def connect(self) -> None:
        try:
            for _ in range(RETRY):
                url_connected = self.__server_url() + "/connect"
                self.generate_user_uid()
                response = requests.post(url=url_connected, data=json.dumps(
                    {
                        "user_id": str(self._client_uuid),
                        "user_name": "test",
                    }
                ))
                messages = response.json()
                for message in messages:
                    print("{user}:{create_date}\n{text}\n".format(
                        user=message.get("user_name"),
                        create_date=message.get("create_date"),
                        text=message.get("text"),
                    ))
                    self._last_message_datetime = message.get("create_date")
                return
        except Exception as error:
            logger.error(error)

    async def tcp_client(self, request_data: str) -> None:
        try:
            reader, writer = await asyncio.open_connection(self._server_host, self._server_port)
            writer.write(request_data.encode("utf-8"))
            await writer.drain()
            data = await reader.read(1000)
            decode_data = data.decode()
            await Handler().handle(decode_data, self)
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logger.error(e)

    async def _check_if_command(self, message: str) -> Optional[dict]:
        command_message = message.strip()
        list_args = command_message.split()
        if list_args and len(list_args) >= 2:
            command_dict = {}
            if list_args[0] in ["/comment", "/report"]:
                command = list_args.pop(0)
                command_dict[command] = list_args
                return command_dict
        return None

    async def get_message_from_chat(self) -> None:
        request_message = None
        while True:
            if self._message_counter <= self._limit_message and not (
                self.datetime_banned and datetime.datetime.utcnow() > self.datetime_banned
            ):
                message = await ainput()
                command = await self._check_if_command(message)
                if command:
                    endpoint = list(command.keys())[0]
                    payload = command[endpoint]
                    if endpoint == "/comment":
                        message_id = payload.pop(0)
                        message = " ".join(payload)
                        request_message = SocketRequest().generate_request(
                            "POST",
                            endpoint,
                            {"parent_id": message_id, "message": message, "user_id": str(self._client_uuid)})
                    elif endpoint == "/report":
                        request_message = SocketRequest().generate_request(
                            "POST",
                            endpoint,
                            {"banned_user_id": payload[0]})
                else:
                    request_message = SocketRequest().generate_request(
                        "POST",
                        "/message",
                        {"message": message, "user_id": str(self._client_uuid)})
                await self.tcp_client(request_message)
                self._message_counter += 1
                if self._message_counter == 1:
                    self._datetime_to_clear = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    async def check_limit_messages(self) -> None:
        while True:
            current_datetime = datetime.datetime.utcnow()
            if self._datetime_to_clear and current_datetime > self._datetime_to_clear:
                self._message_counter = 0
            await asyncio.sleep(60)

    async def check_status(self) -> None:
        while True:
            await asyncio.sleep(90)
            request_message = SocketRequest().generate_request(
                "POST",
                "/status",
                {"user_id": str(self._client_uuid), "last_message_datetime": self._last_message_datetime})
            await self.tcp_client(request_message)
