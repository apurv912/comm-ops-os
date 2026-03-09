from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, text
from sqlmodel import Session, SQLModel, create_engine, select

from models import Interaction, ExtractedFields, Task, Template

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


def repair_task_table() -> None:
    """Lightweight SQLite repair for the `task` table.

    Checks existing columns and adds any missing columns required by the
    current `Task` model using safe `ALTER TABLE ... ADD COLUMN` statements.
    Does nothing if the table does not exist yet.
    """
    # Full expected Task schema (simple SQLite types). Note: adding
    # an `id` column via ALTER TABLE will not retroactively make it a
    # PRIMARY KEY in existing tables, but we add it here for schema
    # compatibility in simple cases where the column is missing.
    expected = {
        "id": "INTEGER",
        "interaction_id": "INTEGER",
        "extracted_fields_id": "INTEGER",
        "title": "TEXT",
        "description": "TEXT",
        "status": "TEXT",
        "due_date": "TEXT",
        "priority": "INTEGER",
        "created_at": "TEXT",
        "updated_at": "TEXT",
    }

    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info('task')"))
        rows = res.fetchall()
        if not rows:
            return
        existing_cols = {row[1] for row in rows}

    with engine.begin() as conn:
        for col, sql_type in expected.items():
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE task ADD COLUMN {col} {sql_type}"))


def repair_template_table() -> None:
    """Lightweight SQLite repair for the `template` table.

    Adds any missing columns required by the current `Template` model.
    Does nothing if the table does not exist yet.
    """
    expected = {
        "id": "INTEGER",
        "name": "TEXT",
        "channel": "TEXT",
        "template_type": "TEXT",
        "subject": "TEXT",
        "body": "TEXT",
        "created_at": "TEXT",
        "updated_at": "TEXT",
    }

    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info('template')"))
        rows = res.fetchall()
        if not rows:
            return
        existing_cols = {row[1] for row in rows}

    with engine.begin() as conn:
        for col, sql_type in expected.items():
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE template ADD COLUMN {col} {sql_type}"))


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
    repair_task_table()
    repair_template_table()
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


def get_extracted_fields(interaction_id: int) -> Optional[ExtractedFields]:
    """Return the ExtractedFields row for the given interaction_id, or None."""
    with Session(engine) as session:
        stmt = select(ExtractedFields).where(ExtractedFields.interaction_id == interaction_id)
        return session.exec(stmt).first()


def upsert_extracted_fields(extracted: ExtractedFields) -> ExtractedFields:
    """Insert or update the ExtractedFields row for an interaction.

    If a row exists for `extracted.interaction_id`, update its fields.
    Otherwise insert a new row. Commit, refresh, and return the saved row.
    """
    if not getattr(extracted, "interaction_id", None) or extracted.interaction_id <= 0:
        raise ValueError("extracted.interaction_id must be a positive int")

    with Session(engine) as session:
        # find existing by interaction_id
        stmt = select(ExtractedFields).where(ExtractedFields.interaction_id == extracted.interaction_id)
        existing = session.exec(stmt).first()

        if existing:
            # update allowed fields
            existing.summary = extracted.summary
            existing.intent = extracted.intent
            existing.suggested_action = extracted.suggested_action
            existing.confidence = extracted.confidence
            existing.warnings = extracted.warnings
            existing.timestamp = extracted.timestamp

            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        # insert new
        session.add(extracted)
        session.commit()
        session.refresh(extracted)
        return extracted


def create_task(task: Task) -> Task:
    """Insert one Task and return it refreshed (with id)."""
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def list_tasks() -> List[Task]:
    """Return all tasks, newest first by created_at."""
    with Session(engine) as session:
        stmt = select(Task).order_by(Task.created_at.desc())
        return list(session.exec(stmt).all())


def get_task(task_id: int) -> Optional[Task]:
    """Fetch one task by id."""
    with Session(engine) as session:
        return session.get(Task, task_id)


def get_task_by_interaction(interaction_id: int) -> Optional[Task]:
    """Return the first Task associated with an interaction, or None."""
    with Session(engine) as session:
        stmt = select(Task).where(Task.interaction_id == interaction_id)
        return session.exec(stmt).first()


def update_task_status(task_id: int, status: str) -> Task:
    """Update the status (and updated_at) of a task and return it.

    Raises `ValueError` if task not found.
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task id={task_id} not found")
        task.status = status
        task.updated_at = datetime.now()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def create_template(template: Template) -> Template:
    """Insert one Template and return it refreshed (with id)."""
    with Session(engine) as session:
        session.add(template)
        session.commit()
        session.refresh(template)
        return template


def list_templates() -> List[Template]:
    """Return all templates, newest first by created_at."""
    with Session(engine) as session:
        stmt = select(Template).order_by(Template.created_at.desc())
        return list(session.exec(stmt).all())


def get_template(template_id: int) -> Optional[Template]:
    """Fetch one template by id."""
    with Session(engine) as session:
        return session.get(Template, template_id)


def update_template(template: Template) -> Template:
    """Update an existing Template (must have id) and return it."""
    if not getattr(template, "id", None):
        raise ValueError("template.id must be provided for update")
    with Session(engine) as session:
        existing = session.get(Template, template.id)
        if not existing:
            raise ValueError(f"Template id={template.id} not found")

        existing.name = template.name
        existing.channel = template.channel
        existing.template_type = template.template_type
        existing.subject = template.subject
        existing.body = template.body
        existing.updated_at = datetime.now()

        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing