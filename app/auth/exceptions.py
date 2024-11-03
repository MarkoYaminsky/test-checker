from fastapi import HTTPException
from starlette import status


class InvalidJWTTokenException(HTTPException):
    def __init__(self, detail: str = "Invalid or absent authorization token.") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
