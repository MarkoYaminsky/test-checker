import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, Column, DateTime

from app.core.db import Base


class BaseDatabaseModel(Base):
    __abstract__ = True

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
