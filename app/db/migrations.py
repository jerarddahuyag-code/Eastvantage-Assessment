import asyncio
import logging
from pathlib import Path
from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger("eastvantage.address_book.migrations")
settings = get_settings()


def apply_alembic_migrations() -> None:
    base_dir = Path(__file__).resolve().parent.parent.parent
    alembic_cfg_path = base_dir / "alembic.ini"

    if alembic_cfg_path.exists():
        logger.info(f"Applying Alembic migrations from {alembic_cfg_path}")
        alembic_cfg = Config(str(alembic_cfg_path))
        sqlite_sync_url = f"sqlite:///{settings.sqlite_db_path}"
        alembic_cfg.set_main_option("sqlalchemy.url", sqlite_sync_url)
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied successfully.")
    else:
        logger.warning("alembic.ini not found, skipping migration runner.")


async def initialize_database() -> None:
    """Execute Alembic migrations in a worker thread, falling back to declarative creation on failure.

    Alembic commands run synchronously; executing via asyncio.to_thread prevents blocking the event loop.
    The fallback ensures the application boots even if run in environments without migration history.
    """
    try:
        await asyncio.to_thread(apply_alembic_migrations)
    except Exception as exc:
        logger.warning(
            f"Alembic auto-migration encountered an error ({exc}); "
            "falling back to Base.metadata.create_all."
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized via Base.metadata.create_all.")
