from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services import JWTTokenType, decode_jwt_token, validate_jwt_token_payload
from app.core.db import SessionLocal
from app.users.models import User


async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
        await session.commit()


async def get_http_authenticated_user(
    authorization: Optional[str] = Header("Bearer "), session: AsyncSession = Depends(get_db_session)
) -> User | None:
    """
    Get the http authenticated user from the JWT token in the Authorization header.
    Raises an exception if the token is invalid or expired, or if the header is not present.
    """
    token = authorization.split("Bearer ")[1]
    payload = decode_jwt_token(token)
    return await validate_jwt_token_payload(session=session, payload=payload, token_type=JWTTokenType.access)
