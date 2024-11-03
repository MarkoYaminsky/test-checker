class BaseCustomException(Exception):
    description: str
    code: str

    def __init__(self, description: str, code: str = ""):
        self.description = description
        self.code = code
        super().__init__({"description": description, "code": code})

    @property
    def information(self) -> dict[str, str]:
        return {"description": self.description, "code": self.code}
