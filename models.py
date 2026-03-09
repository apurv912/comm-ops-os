from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Interaction(SQLModel, table=True):
    """
    Core record for ComOps.
    Interaction-first (not message-first) so it generalizes to PR later
    (email/whatsapp/call are all just channels).
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    channel: str = Field(default="email", index=True)  # e.g., email, whatsapp, call
    subject: str = Field(default="")
    body: str = Field(default="")

    # Timestamp of the interaction (not DB write time)
    timestamp: datetime = Field(default_factory=datetime.now, index=True)

    # Lightweight contact info (optional)
    contact_name: Optional[str] = Field(default=None)
    contact_email: Optional[str] = Field(default=None)


class ExtractedFields(SQLModel, table=True):
    """Per-interaction extraction results (one row per Interaction).

    Stored as a separate table (no ORM Relationship) and kept SQLite
    friendly. `interaction_id` is unique so there is at most one
    ExtractedFields row for an Interaction.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # link to Interaction by id (no foreign_key/Relationship used here)
    interaction_id: int = Field(index=True, unique=True)

    summary: str = Field(default="")
    intent: str = Field(default="")
    suggested_action: str = Field(default="")
    confidence: float = Field(default=0.0)
    warnings: str = Field(default="")

    # timestamp of the extraction operation
    timestamp: datetime = Field(default_factory=datetime.now, index=True)


class Task(SQLModel, table=True):
    """Lightweight Task entity associated (optionally) with an Interaction
    and/or ExtractedFields. Kept minimal and SQLite-friendly.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # optional linkage to Interaction / ExtractedFields (no ORM Relationship)
    interaction_id: Optional[int] = Field(default=None, index=True)
    extracted_fields_id: Optional[int] = Field(default=None, index=True)

    title: str = Field(default="")
    description: Optional[str] = Field(default=None)

    status: str = Field(default="open", index=True)
    due_date: Optional[datetime] = Field(default=None)
    priority: Optional[int] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now, index=True)