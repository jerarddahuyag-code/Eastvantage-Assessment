from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "Eastvantage Address Book API"
    app_version: str = "1.0.0"
    app_description: str = (
        "Minimal address book API with coordinate storage, validation, "
        "and proximity search using FastAPI, SQLite, and CQRS."
    )
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    sqlite_db_path: Path = BASE_DIR / "address_book.db"
    database_url: str = f"sqlite+aiosqlite:///{sqlite_db_path}"
    database_echo: bool = False

    default_search_radius_km: float = 5.0
    max_search_radius_km: float = 500.0
    default_query_limit: int = 20
    max_query_limit: int = 100

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
