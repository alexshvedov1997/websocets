import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from db import postgres
from server.core.server import Server
from server.core.settings import settings


def init_db() -> None:
    postgres.psql_engine = create_async_engine(
        "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}".format(
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            db_name=settings.db_name,
        ),
        echo=True,
        future=True,
    )


async def init_models() -> None:
    async with postgres.psql_engine.begin() as conn:
        await conn.run_sync(postgres.Base.metadata.drop_all)
        await conn.run_sync(postgres.Base.metadata.create_all)


async def main() -> None:
    server = Server()
    loop = asyncio.get_event_loop()
    task1 = loop.create_task(init_models())
    task2 = loop.create_task(server.run())
    await task1
    await task2


if __name__ == "__main__":
    init_db()
    asyncio.run(main())
