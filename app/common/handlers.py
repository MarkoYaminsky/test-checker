from typing import Any, Type

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.common.services.db import quick_select
from app.common.types import DatabaseInstanceType
from app.common.utilities import get_user_model

User = get_user_model()


async def get_object_or_404(
    session: AsyncSession, model: Type[DatabaseInstanceType], **filters: Any
) -> DatabaseInstanceType:
    obj = (await quick_select(session=session, model=model, filter_by=filters)).scalar()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return obj


def check_if_object_belongs_to_user(object_user: User, access_user: User):
    if object_user != access_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this object"
        )
    return object_user
