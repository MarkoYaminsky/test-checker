from sqlalchemy import Column, String

from app.common.models import BaseDatabaseModel


class User(BaseDatabaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

