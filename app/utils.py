import datetime
import enum
import uuid

import jwt
from fastapi import Depends
from fastapi.security import APIKeyHeader

from app.configs.main import settings
from app.exceptions.auth import InvalidTokenException

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user_id(token: str = Depends(api_key_header)) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.secret.JWT_SECRET, algorithms=[settings.secret.ALGORITHM])
        user_id: uuid.UUID = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
        return user_id
    except jwt.PyJWTError:
        raise InvalidTokenException


def custom_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, enum.Enum):
        return obj.value
    raise TypeError(f"Type {type(obj)} not serializable")
