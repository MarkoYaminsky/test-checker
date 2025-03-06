from typing import Any, Type

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, selectinload

from app.common.models import BaseDatabaseModel
from app.common.types import DatabaseInstanceType
from app.student_tests.exceptions import InvalidRelationshipAttributeException


def move_row_values_to_attributes(rows: Result, attribute_names: tuple[str, ...]) -> list[DatabaseInstanceType]:
    annotated_objects = []
    for row in rows:
        main_object, *attributes = row
        for index, attribute_name in enumerate(attribute_names):
            setattr(main_object, attribute_name, attributes[index])
        annotated_objects.append(main_object)
    return annotated_objects


async def quick_select(
    session: AsyncSession, model: Type[DatabaseInstanceType], filters: Any = None, filter_by: dict = None
) -> Result:
    query = select(model)
    if filters is not None:
        query = query.where(*filters)
    if filter_by is not None:
        query = query.filter_by(**filter_by)
    return await session.execute(query)


async def query_relationship(
    session: AsyncSession, instance: BaseDatabaseModel, relationship_attributes: list[QueryableAttribute]
) -> list[DatabaseInstanceType]:
    model = instance.__class__
    main_attribute, *derivative_loads = relationship_attributes
    main_load = selectinload(main_attribute)
    for attribute in derivative_loads:
        main_load = main_load.selectinload(attribute)
    query = select(model).options(main_load).filter(model.id == instance.id)
    result = await session.execute(query)
    fetched_instance = result.scalars().first()
    current_object = getattr(fetched_instance, main_attribute.key)
    for attribute in derivative_loads:
        relation_name = attribute.key
        current_object = getattr(current_object, relation_name, None)
        if current_object is None:
            raise InvalidRelationshipAttributeException(relation_name)
    return current_object
