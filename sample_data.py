from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from sqlmodel import select

import models
from db import init_db, get_session


def _sample_email_rows() -> List[dict]:
    """
    3 deterministic sample email interactions.
    We use fixed timestamps so we can reliably detect "already loaded".
    """
    return [
        {
            "channel": "email",
            "subject": "Sample: Intro outreach to journalist",
            "body": (
                "Hi there,\n\n"
                "Reaching out with a short intro and a story angle for your beat.\n"
                "If relevant, I can share a 3-bullet brief + spokesperson availability.\n\n"
                "Thanks,\nComOps Sample"
            ),
            "timestamp": datetime(2026, 2, 24, 9, 30, 0),
            "contact_id": None,
        },
        {
            "channel": "email",
            "subject": "Sample: Follow-up (no response yet)",
            "body": (
                "Hi,\n\n"
                "Quick follow-up on my earlier note.\n"
                "Happy to tailor the angle to your audience or share data points.\n\n"
                "Best,\nComOps Sample"
            ),
            "timestamp": datetime(2026, 2, 25, 11, 0, 0),
            "contact_id": None,
        },
        {
            "channel": "email",
            "subject": "Sample: Coverage secured — thank you",
            "body": (
                "Hi,\n\n"
                "Thank you for covering the story. Really appreciate it.\n"
                "If helpful, I can share additional context or connect you to the team.\n\n"
                "Regards,\nComOps Sample"
            ),
            "timestamp": datetime(2026, 2, 26, 8, 15, 0),
            "contact_id": None,
        },
    ]


def seed_sample_emails() -> Dict[str, int]:
    """
    Idempotent seed:
    - First run inserts 3
    - Second run inserts 0, skips 3

    Strategy (simple MVP): consider a row "same" if:
    channel + subject + timestamp match.
    """
    init_db()

    inserted = 0
    skipped = 0
    rows = _sample_email_rows()

    with get_session() as session:
        for r in rows:
            exists = session.exec(
                select(models.Interaction).where(
                    models.Interaction.channel == r["channel"],
                    models.Interaction.subject == r["subject"],
                    models.Interaction.timestamp == r["timestamp"],
                )
            ).first()

            if exists:
                skipped += 1
                continue

            session.add(models.Interaction(**r))
            inserted += 1

        session.commit()

    return {"inserted": inserted, "skipped": skipped}