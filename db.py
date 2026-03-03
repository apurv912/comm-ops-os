from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, text
from sqlmodel import Session, SQLModel, create_engine, select

from models import Interaction

DB_URL = "sqlite:///app.db"
engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # required for Streamlit
)


def init_db() -> None:
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def migrate_db() -> None:
    """Lightweight SQLite migration for v0.3.

    Detects missing columns on the `interaction` table and adds them.
    Does nothing if the table does not exist.
    """
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info('interaction')"))
        rows = res.fetchall()
        if not rows:
            return
        cols = {row[1] for row in rows}
    with engine.begin() as conn:
        if "contact_name" not in cols:
            conn.execute(text("ALTER TABLE interaction ADD COLUMN contact_name TEXT"))
        if "contact_email" not in cols:
            conn.execute(text("ALTER TABLE interaction ADD COLUMN contact_email TEXT"))


def seed_db_if_empty() -> None:
    """Seed minimal sample data only if DB is empty (so we don't duplicate)."""
    with Session(engine) as session:
        count = session.exec(select(func.count(Interaction.id))).one()
        if count and count > 0:
            return

        now = datetime.now()
        seeds = [
            Interaction(
                channel="email",
                subject="Intro: Partnership discussion",
                body="Hi Apurv,\n\nWould love to discuss a potential partnership next week.\n\nBest,\nA",
                timestamp=now - timedelta(days=1, hours=2),
                contact_name="Aditi",
                contact_email="aditi@example.com",
            ),
            Interaction(
                channel="email",
                subject="Follow-up: Meeting notes",
                body="Thanks for the call. Here are the notes...\n\n- Item 1\n- Item 2\n",
                timestamp=now - timedelta(hours=6),
            ),
        ]
        session.add_all(seeds)
        session.commit()


def ensure_db() -> None:
    """Call once at app start: ensures schema + seed data."""
    init_db()
    migrate_db()
    seed_db_if_empty()


def create_interaction(interaction: Interaction) -> Interaction:
    """Insert one Interaction and return it refreshed (with id)."""
    with Session(engine) as session:
        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return interaction


def list_interactions(channel: Optional[str] = "email") -> List[Interaction]:
    """List interactions, newest first. Default: email inbox view."""
    with Session(engine) as session:
        stmt = select(Interaction)
        if channel:
            stmt = stmt.where(Interaction.channel == channel)
        stmt = stmt.order_by(Interaction.timestamp.desc())
        return list(session.exec(stmt).all())


def get_interaction(interaction_id: int) -> Optional[Interaction]:
    """Fetch one interaction by id."""
    with Session(engine) as session:
        return session.get(Interaction, interaction_id)