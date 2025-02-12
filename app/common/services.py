from typing import Any, Optional, Sequence, Type

from sqlalchemy import BinaryExpression, Row
from sqlalchemy.orm import Query, Session

from app.common.types import DatabaseInstanceType


def get_all_entities_query(
    db: Session, model: Type[DatabaseInstanceType], *, condition: Optional[BinaryExpression] = None, **filters: Any
) -> Query[DatabaseInstanceType]:
    query = db.query(model)
    if condition is not None:
        query = query.filter(condition)
    if filters:
        query = query.filter_by(**filters)
    return query


def move_row_values_to_attributes(rows: Sequence[Row], attribute_names: tuple[str, ...]) -> list[DatabaseInstanceType]:
    for row in rows:
        main_object, *attributes = row
        for index, attribute_name in enumerate(attribute_names):
            setattr(main_object, attribute_name, attributes[index])
    return [row[0] for row in rows]
