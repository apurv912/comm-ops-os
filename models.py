from datetime import datetime, date
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    email: Optional[str] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    interactions: list["Interaction"] = Relationship(back_populates="contact")
    tasks: list["Task"] = Relationship(back_populates="contact")


class Interaction(SQLModel, table=True):
    """
    Core record (PM decision): store interaction events, not raw messages.
    Email/WhatsApp/Call are all 'interactions' with different channels.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    channel: str = Field(default="email", index=True)  # email | whatsapp | call | ...
    subject: Optional[str] = Field(default=None)
    body: Optional[str] = Field(default=None)

    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True, nullable=False)

    contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    contact: Optional["Contact"] = Relationship(back_populates="interactions")

    tasks: list["Task"] = Relationship(back_populates="interaction")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    status: str = Field(default="todo", index=True)  # todo | doing | done

    due_date: Optional[date] = Field(default=None, index=True)

    contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    contact: Optional["Contact"] = Relationship(back_populates="tasks")

    interaction_id: Optional[int] = Field(default=None, foreign_key="interaction.id")
    interaction: Optional["Interaction"] = Relationship(back_populates="tasks")