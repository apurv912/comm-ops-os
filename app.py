from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlmodel import select

import models  # important: registers SQLModel tables in metadata
from db import init_db, get_session


def load_inbox_rows(limit: int = 200) -> pd.DataFrame:
    """
    Inbox = email interactions (Interaction-first model).
    Returns an empty dataframe with stable columns if no rows exist.
    """
    columns = ["id", "timestamp", "channel", "subject", "contact_id"]

    with get_session() as session:
        stmt = (
            select(models.Interaction)
            .where(models.Interaction.channel == "email")
            .order_by(models.Interaction.timestamp.desc())
            .limit(limit)
        )
        rows = session.exec(stmt).all()

    if not rows:
        return pd.DataFrame(columns=columns)

    data = [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "channel": r.channel,
            "subject": r.subject,
            "contact_id": r.contact_id,
        }
        for r in rows
    ]
    return pd.DataFrame(data, columns=columns)


def render_inbox():
    st.subheader("Inbox")
    st.caption('Inbox is an "Interaction" view filtered by channel="email".')

    df = load_inbox_rows()
    st.dataframe(df, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title="ComOps v0", layout="wide")

    # Ensure DB exists + tables are created on first run (AC3)
    init_db()

    st.title("Communication Ops OS (ComOps) — v0.1")
    st.caption("Local-first communication operations mini-OS (Interaction-first engine).")

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Inbox"], index=0)

    if page == "Inbox":
        render_inbox()


if __name__ == "__main__":
    main()