from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.auth.services import JWTTokenType, decode_jwt_token, validate_jwt_token_payload
from app.core.db import SessionLocal
from app.users.models import User


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_http_authenticated_user(
    authorization: Optional[str] = Header("Bearer "), db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the http authenticated user from the JWT token in the Authorization header.
    Raises an exception if the token is invalid or expired, or if the header is not present.
    """
    token = authorization.split("Bearer ")[1]
    payload = decode_jwt_token(token)
    return validate_jwt_token_payload(db=db, payload=payload, token_type=JWTTokenType.access)
