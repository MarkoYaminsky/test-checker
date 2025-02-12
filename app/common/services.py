from typing import Any, Type

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.models import BaseDatabaseModel
from app.common.types import DatabaseInstanceType


def move_row_values_to_attributes(rows: Result, attribute_names: tuple[str, ...]) -> list[DatabaseInstanceType]:
    annotated_objects = []
    for row in rows:
        main_object, *attributes = row
        for index, attribute_name in enumerate(attribute_names):
            setattr(main_object, attribute_name, attributes[index])
        annotated_objects.append(main_object)
    return annotated_objects


async def quick_select(
    session: AsyncSession, model: Type[DatabaseInstanceType], filters: Any = None, filter_by: Any = None
) -> Result:
    query = select(model)
    if filters is not None:
        query = query.where(*filters)
    if filter_by is not None:
        query = query.filter_by(**filter_by)
    return await session.execute(query)


async def query_relationship(
    session: AsyncSession, instance: BaseDatabaseModel, relationship_attribute: str
) -> list[DatabaseInstanceType]:
    model = instance.__class__
    query = select(model).options(selectinload(getattr(model, relationship_attribute))).filter(model.id == instance.id)
    result = await session.execute(query)
    fetched_instance = result.scalars().first()
    return getattr(fetched_instance, relationship_attribute)
