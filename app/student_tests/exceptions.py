from app.common.exceptions import BaseCustomException


class DuplicateTestNameException(BaseCustomException):
    def __init__(self, name: str):
        super().__init__(description=f"The test with name {name} already exists.", code="test-name-duplicate")


class InvalidRelationshipAttributeException(BaseCustomException):
    def __init__(self, attribute_name: str):
        super().__init__(
            description=f"The relationship attribute {attribute_name} is invalid.",
            code="invalid-relationship-attribute",
        )
