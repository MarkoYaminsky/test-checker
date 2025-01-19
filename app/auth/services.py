from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.auth.constants import ENCODING_ALGORITHM
from app.auth.exceptions import InvalidJWTTokenException
from app.auth.types import JWTTokenPayload, JWTTokenType
from app.common.utilities import get_user_model
from app.core.config import settings

User = get_user_model()

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_jwt_token(user_id: UUID, token_type: JWTTokenType) -> str:
    token_type_to_expiration_delta = {
        JWTTokenType.access: timedelta(minutes=settings.access_token_expiration_time_in_minutes),
        JWTTokenType.refresh: timedelta(days=settings.refresh_token_expiration_time_in_days),
    }
    expiration_datetime = datetime.utcnow() + token_type_to_expiration_delta[token_type]
    token_data = {"user_id": str(user_id), "token_type": token_type.name, "exp": expiration_datetime}
    encoded_jwt = jwt.encode(token_data, settings.encoding_key, algorithm=ENCODING_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[JWTTokenPayload]:
    try:
        payload = jwt.decode(token, settings.encoding_key, algorithms=[ENCODING_ALGORITHM])
        expiration_datetime = datetime.utcfromtimestamp(float(payload.pop("exp", 0)))
        return JWTTokenPayload(**payload, exp=expiration_datetime) if payload else None
    except jwt.PyJWTError:
        raise InvalidJWTTokenException


def validate_jwt_token_payload(db: Session, payload: JWTTokenPayload, token_type: JWTTokenType) -> User:
    from app.users.services import get_all_users_query

    if payload.token_type != token_type.name or payload.exp < datetime.utcnow():
        raise InvalidJWTTokenException
    user = get_all_users_query(db, id=payload.user_id).scalar()
    if user is None:
        raise InvalidJWTTokenException
    return user


def issue_access_token_by_refresh_token(refresh_token: str) -> str:
    payload = decode_jwt_token(refresh_token)
    if payload is None or payload.exp < datetime.utcnow():
        raise InvalidJWTTokenException
    return create_jwt_token(user_id=UUID(payload.user_id), token_type=JWTTokenType.access)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)
