from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings


async def get_db_session() -> Generator:
    """
    Connects to the database.
    :return: Session.
    """
    try:
        engine = create_async_engine(settings.db_url, future=True, echo=True)
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
