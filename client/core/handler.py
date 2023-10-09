import datetime
import logging
import sys

from utils.schemas import RequestSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Handler:

    async def handle(self, data: str, client) -> None:
        try:
            request_data = RequestSchema(raw_data=data)
            method = request_data.json_data.get("method")
            if method == "/status":
                await self.status(request_data, client)
        except Exception as error:
            logger.error(error)

    async def status(self, data: RequestSchema, client) -> None:
        messages = data.json_data.get("messages", [])
        for message in messages:
            print("{user}:{create_date}\n{text}\n".format(
                user=message.get("user_name"),
                create_date=message.get("create_date"),
                text=message.get("text"),
            ))
            client._last_message_datetime = message.get("create_date")
        user = data.json_data.get("user")
        if user:
            banned = user.get("banned")
            if banned:
                client.datetime_banned = datetime.datetime.utcnow() + datetime.timedelta(hours=4)
