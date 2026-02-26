from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Load .env if present (safe if it doesn't exist)
load_dotenv()

DEFAULT_DB_URL = "sqlite:///app.db"


@lru_cache(maxsize=1)
def get_engine():
    """
    Single engine instance for the app lifecycle.
    Uses DATABASE_URL if set, otherwise local SQLite app.db.
    """
    db_url = os.getenv("DATABASE_URL") or DEFAULT_DB_URL

    connect_args = {}
    # Needed for SQLite + Streamlit (multithreading)
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    return create_engine(db_url, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Create tables on first run."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Convenience helper for short-lived DB sessions."""
    return Session(get_engine())