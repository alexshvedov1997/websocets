import logging
import sys
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update

from db import postgres
from db.postgres import get_session
from models.message import Messages
from models.user import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Controller:

    @staticmethod
    async def connect(json_data: dict) -> List[dict]:
        response_data = []
        user_id = json_data.get("user_id")
        async with get_session(postgres.psql_engine) as session:
            users = await session.execute(select(User).where(User.user_id == user_id))
            user_exist = users.fetchone()
            if not user_exist:
                user = User(name=json_data.get("user_name"), user_id=user_id)
                session.add(user)
                await session.commit()
            messages_psql = await session.execute(select(User, Messages).join(
                User, User.id == Messages.user_id).order_by(Messages.created_date).limit(20))
            messages = messages_psql.fetchall()
            for user_message in messages:
                user, message = user_message
                response_data.append({
                    "user_name": user.name,
                    "text": message.text,
                    "create_date": str(message.created_date),
                })
            return response_data

    @staticmethod
    async def create_message(json_data: dict):
        user_id = json_data.get("user_id")
        message = json_data.get("message")
        async with get_session(postgres.psql_engine) as session:
            users = await session.execute(select(User).where(User.user_id == user_id))
            user_exist = users.fetchone()
            if message is not None:
                message = Messages(text=message, user_id=user_exist[0].id)
                session.add(message)
                await session.commit()
                return True

    @staticmethod
    async def comment_message(json_data: dict) -> Optional[bool]:
        user_id = json_data.get("user_id")
        message = json_data.get("message")
        parent_id = json_data.get("parent_id")
        async with get_session(postgres.psql_engine) as session:
            users = await session.execute(select(User).where(User.user_id == user_id))
            user_exist = users.fetchone()
            if message is not None:
                message = Messages(text=message, user_id=user_exist[0].id, parent_id=int(parent_id))
                session.add(message)
                await session.commit()
                return True

    @staticmethod
    async def report_user(json_data: dict) -> None:
        banned_user_id = json_data.get("banned_user_id")
        async with get_session(postgres.psql_engine) as session:
            users = await session.execute(select(User).where(User.user_id == banned_user_id))
            user_exist = users.fetchone()
            report_count = user_exist[0].report_count
            report_count += 1
            await session.execute(
                update(User).where(User.user_id == banned_user_id).values(report_count=report_count)
            )
            await session.commit()

    @staticmethod
    async def check_status(json_data: dict) -> dict:
        response_data = {"user": {}, "messages": [], "method": "/status"}
        user_id = json_data.get("user_id")
        last_message_datetime = json_data.get("last_message_datetime")
        if last_message_datetime:
            last_message_datetime = datetime.strptime(last_message_datetime, '%Y-%m-%d %H:%M:%S.%f')
        else:
            last_message_datetime = datetime.utcnow()
        async with get_session(postgres.psql_engine) as session:
            users = await session.execute(select(User).where(User.user_id == user_id))
            user_exist = users.fetchone()
            report_count = user_exist[0].report_count
            if report_count >= 3:
                session.execute(
                    update(User).where(User.user_id == user_id).values(report_count=0)
                )
                await session.commit()
                response_data["user"]["banned"] = True
            messages_data = await session.execute(select(User, Messages).join(
                User, User.id == Messages.user_id).where(
                Messages.created_date > last_message_datetime
            ).order_by(Messages.created_date).limit(20))
            messages = messages_data.fetchall()
            for user_message in messages:
                user, message = user_message
                response_data["messages"].append({
                    "user_name": user.name,
                    "text": message.text,
                    "create_date": str(message.created_date),
                })
            return response_data
