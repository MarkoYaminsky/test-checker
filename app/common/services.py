from typing import Any, Optional, Type

from sqlalchemy import BinaryExpression
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
