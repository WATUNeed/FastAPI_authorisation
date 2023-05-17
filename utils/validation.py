import re
import uuid
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError


LETTER_MATCH_PATTERN = re.compile(r"[а-яА-Яa-zA_Z\-]+$")
PASSWORD_MATCH_PATTERN = re.compile(
    r'^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$'
)


def validate_id(value: Any) -> uuid.UUID:
    """
    Checks the data type of the variable value.
    :param value:
    :return:
    """
    if not isinstance(value, uuid.UUID):
        raise HTTPException(status_code=422, detail=f'ID should contains only UUID type.')
    return value


def validate_name(value: Any) -> str:
    """
    Checks the data type of the variable value.
    :param value:
    :return:
    """
    if not LETTER_MATCH_PATTERN.match(value):
        raise HTTPException(status_code=422, detail='Field should contains only letters')
    return validate_empty(value)


def validate_empty(value: Any) -> str:
    """
    Checks the data type of the variable value.
    :param value:
    :return:
    """
    if not value:
        raise HTTPException(status_code=400, detail='Field cannot be empty')
    return value


def validate_password(value: Any) -> str:
    """
    Checks the data type of the variable value.
    :param value:
    :return:
    """
    if not re.fullmatch(PASSWORD_MATCH_PATTERN, value):
        raise HTTPException(status_code=422, detail='The password is too simple')
    return value


def validate_email(value: Any):
    """
    IMPORTANT! Do not use in api module.
    There may be a problem with cyclic imports.

    Checks the data type of the variable value.
    :param value:
    :return:
    """
    from api.models import ShowEmail
    try:
        return ShowEmail(email=value)
    except ValidationError:
        raise HTTPException(status_code=422, detail='Invalid email address')
