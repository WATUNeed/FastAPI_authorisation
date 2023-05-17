from datetime import timedelta, datetime
from typing import Optional

from jose import jwt

from config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creating a JWT token based on dict data and expire.
    :param data:
    :param expires_delta:
    :return: JWT token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_min)

    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
