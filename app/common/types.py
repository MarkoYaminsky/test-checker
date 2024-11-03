from typing import TypeVar

from app.common.models import BaseDatabaseModel

DatabaseInstanceType = TypeVar("DatabaseInstanceType", bound=BaseDatabaseModel)
