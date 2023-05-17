from typing import Any

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


def catch_exceptions(func: Any) -> Any:
    """
    Decorator for accessing the database. Traps SQL errors.
    :param func:
    :return: Callable func
    """
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NoResultFound:
            raise HTTPException(status_code=404, detail='No entry found')
        except IntegrityError:
            raise HTTPException(status_code=403, detail='Already taken')
    return wrapped


def request(func: Any) -> Any:
    """
    Decorator for accessing the database.
    Creates an asynchronous session.
    Rolls back changes if there is an error.
    :param func:
    :return: Callable func
    """
    async def wrapped(*args, session: AsyncSession, **kwargs) -> Any:
        async with session as session:
            async with session.begin():
                return await func(*args, session, **kwargs)
    return wrapped
