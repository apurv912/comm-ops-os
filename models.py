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