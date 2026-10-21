from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas das variáveis de ambiente (ou do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mysql_user: str
    mysql_password: str
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "caronas"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


settings = Settings()
