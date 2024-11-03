from functools import wraps
from types import MappingProxyType
from typing import Callable, Any, Type

from fastapi import HTTPException
from starlette import status

from app.common.constants import DEFAULT_EXPECTED_EXCEPTIONS
from app.common.exceptions import BaseCustomException


def expects_exceptions(
        exceptions_to_status_codes: dict[Type[BaseCustomException], status] = MappingProxyType({})
) -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        async def wrapper(*args: Any, **kwargs: Any) -> Callable:
            exception_handlers = {**exceptions_to_status_codes, **DEFAULT_EXPECTED_EXCEPTIONS}
            try:
                return await function(*args, **kwargs)
            except tuple(exception_handlers.keys()) as exception:
                raise HTTPException(
                    status_code=exception_handlers[type(exception)], detail=exception.information
                )

        return wrapper

    return decorator
