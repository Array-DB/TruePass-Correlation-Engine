"""Database engine and session helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from truepass.config import AppSettings


def create_database_engine(settings: AppSettings) -> Engine:
    """Create a SQLAlchemy engine from typed settings."""

    return create_engine(
        settings.database.url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=settings.database.pool_size,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Yield a transaction-scoped session and rollback on error."""

    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
