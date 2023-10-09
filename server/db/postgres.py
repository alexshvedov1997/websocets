import logging
import sys
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

psql_engine = None
Base = declarative_base()


def async_session_generator(engine):
    return sessionmaker(
        engine, class_=AsyncSession
    )


@asynccontextmanager
async def get_session(engine):
    try:
        async_session = async_session_generator(engine)
        async with async_session() as session:
            yield session
    except Exception as error:
        logger.error("Error in init session {}".format(error))
        await session.rollback()
        raise
    finally:
        await session.close()
