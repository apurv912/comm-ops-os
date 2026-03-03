# app.py — ComOps v0.3 (Manual Ingestion + Interaction Detail View)

from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict, List

import streamlit as st

from db import create_interaction, ensure_db, list_interactions
from models import Interaction


# ----------------------------
# Navigation callbacks (safe way)
# ----------------------------
def nav_to_inbox() -> None:
    # Runs as an on_click callback (safe: executes before widgets instantiate on rerun)
    st.session_state["nav_page"] = "Inbox"


# ----------------------------
# UI helpers
# ----------------------------
def _fmt_option(i: Interaction) -> str:
    ts = i.timestamp.strftime("%Y-%m-%d %H:%M")
    subj = (i.subject or "").strip() or "(no subject)"
    return f"{i.id} | {ts} | {subj}"


def _contact_summary(i: Interaction) -> str:
    name = (i.contact_name or "").strip()
    email = (i.contact_email or "").strip()
    if not name and not email:
        return "None"
    if name and email:
        return f"{name} <{email}>"
    return name or email


# ----------------------------
# Pages
# ----------------------------
def render_inbox() -> None:
    st.title("Inbox")
    st.caption('Interactions where channel="email"')

    interactions: List[Interaction] = list_interactions(channel="email")
    st.write(f"Total: **{len(interactions)}**")

    if not interactions:
        st.info("No interactions yet. Add one from **Add Interaction**.")
        return

    rows = [
        {
            "id": i.id,
            "timestamp": i.timestamp.strftime("%Y-%m-%d %H:%M"),
            "subject": (i.subject or "").strip(),
            "contact": _contact_summary(i),
        }
        for i in interactions
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()

    by_id: Dict[int, Interaction] = {int(i.id): i for i in interactions if i.id is not None}
    options = [_fmt_option(i) for i in interactions]

    selected_label = st.selectbox("Select an interaction to view details", options=options)

    try:
        selected_id = int(selected_label.split("|", 1)[0].strip())
    except Exception:
        st.error("Selection parsing failed. Please select again.")
        return

    selected = by_id.get(selected_id)
    if not selected:
        st.error("Could not load the selected interaction.")
        return

    st.subheader("Detail View")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Subject:** {(selected.subject or '').strip() or '(no subject)'}")
        st.markdown(f"**Timestamp:** {selected.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**Channel:** {selected.channel}")
        st.markdown(f"**Contact:** {_contact_summary(selected)}")

    with col2:
        st.markdown("**ID**")
        st.code(str(selected.id))

    st.text_area(
        label="Body",
        value=selected.body or "",
        height=220,
        disabled=True,
        label_visibility="collapsed",
    )


def render_add_interaction() -> None:
    st.title("Add Interaction")
    st.caption("Manual ingestion into SQLite (app.db). Default channel: email.")

    now = datetime.now()
    default_date = now.date()
    default_time = now.time().replace(second=0, microsecond=0)

    with st.form("add_interaction_form", clear_on_submit=False):
        channel = st.selectbox("Channel", options=["email", "whatsapp", "call"], index=0)
        subject = st.text_input("Subject", value="")
        body = st.text_area("Body", value="", height=180)

        c1, c2 = st.columns(2)
        with c1:
            d: date = st.date_input("Timestamp (date)", value=default_date)
        with c2:
            t: time = st.time_input("Timestamp (time)", value=default_time)

        st.markdown("**Contact (optional)**")
        contact_name = st.text_input("Contact name", value="")
        contact_email = st.text_input("Contact email", value="")

        submitted = st.form_submit_button("Create Interaction")

    if submitted:
        timestamp = datetime.combine(d, t)

        inter = Interaction(
            channel=channel,
            subject=subject.strip(),
            body=body,
            timestamp=timestamp,
            contact_name=contact_name.strip() or None,
            contact_email=contact_email.strip() or None,
        )

        try:
            created = create_interaction(inter)
        except Exception as e:
            st.error(f"Failed to create interaction: {e}")
            return

        st.success(f"Created interaction id={created.id}")

        # This will reliably switch the sidebar radio on the rerun.
        st.button("Go to Inbox", on_click=nav_to_inbox)


def render_about() -> None:
    st.title("About / Roadmap")
    st.write(
        """
**ComOps v0** is a local-first communication operations mini-OS.

- Core record: **Interaction** (channel-aware), not Message
- Current scope (v0.3): manual ingestion + inbox + detail view
- Future: extraction (v0.4), task queue (v0.5), reporting (v0.6)
"""
    )


# ----------------------------
# App
# ----------------------------
def main() -> None:
    st.set_page_config(page_title="ComOps v0.3", layout="wide")

    ensure_db()

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Inbox"

    page = st.sidebar.radio(
        "Navigation",
        options=["Inbox", "Add Interaction", "About / Roadmap"],
        key="nav_page",
    )

    if page == "Inbox":
        render_inbox()
    elif page == "Add Interaction":
        render_add_interaction()
    else:
        render_about()


if __name__ == "__main__":
    main()