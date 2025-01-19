from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.common.models import BaseDatabaseModel


class User(BaseDatabaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    tests = relationship("Test", back_populates="teacher", cascade="all, delete-orphan")
