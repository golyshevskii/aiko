from collections.abc import AsyncGenerator

# Import all models to register them
from core.db.schema import *  # noqa: F403
from core.schema.db.fields import DBInitStrategy
from core.logger import get_logger
from core.settings import settings
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

DB_ENGINE = None
ASESSION = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if ASESSION is None:
        raise RuntimeError("Database is not initialized. Please build the app first.")

    async with ASESSION() as session:
        yield session


def init_db():
    global DB_ENGINE, ASESSION

    if (
        settings.ENV == "prod"
        and settings.DATABASE_INIT_STRATEGY == DBInitStrategy.RECREATE
    ):
        raise RuntimeError(
            "RECREATE strategy is not allowed in production environment."
        )

    DB_ENGINE = create_async_engine(
        url=settings.model_extra["DATABASE_URI"],
        echo=settings.SQL_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        connect_args=settings.DATABASE_CONNECT_ARGS,
    )

    ASESSION = sessionmaker(
        bind=DB_ENGINE,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    engine = create_engine(
        url=settings.model_extra["DATABASE_URI"],
        echo=settings.SQL_ECHO,
        connect_args=settings.DATABASE_CONNECT_ARGS,
    )

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()

    _apply_db_strategy(engine, settings.DATABASE_INIT_STRATEGY)


def _apply_db_strategy(engine, strategy: DBInitStrategy):
    """Apply the selected database initialization strategy."""
    from core.db.base import DBase

    if strategy == DBInitStrategy.CREATE:
        # Default SQLAlchemy behavior - create tables only if they don't exist
        DBase.metadata.create_all(engine, checkfirst=True)
    elif strategy == DBInitStrategy.RECREATE:
        # Drop all tables and recreate them
        DBase.metadata.drop_all(engine)
        DBase.metadata.create_all(engine)
