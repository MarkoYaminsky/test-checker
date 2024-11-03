from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ChatAPI"

    # Database
    database_name: str
    database_user: str
    database_password: str
    database_host: str = "localhost"
    database_port: int = 5432

    # JWT
    encoding_key: str
    refresh_token_expiration_time_in_days: int
    access_token_expiration_time_in_minutes: int

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.database_user}:{self.database_password}@"
            f"{self.database_host}:{self.database_port}/{self.database_name}"
        )


settings = Settings()
