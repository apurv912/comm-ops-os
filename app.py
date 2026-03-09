# app.py — ComOps v0.3 (Manual Ingestion + Interaction Detail View)

from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict, List

import streamlit as st

from db import (
    create_interaction,
    ensure_db,
    list_interactions,
    get_extracted_fields,
    upsert_extracted_fields,
    create_task,
    get_task_by_interaction,
    list_tasks,
    update_task_status,
)
from db import create_template, list_templates
from extraction import extract_for_interaction
from models import Interaction
from models import Task, Template


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
    
    # Extraction area
    st.divider()

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

    # Extraction area
    st.divider()
    st.subheader("Extraction")

    # Load existing extracted fields if present into a single variable
    current_extracted = None
    if selected.id is not None:
        current_extracted = get_extracted_fields(int(selected.id))

    run_pressed = st.button("Run extraction")
    if run_pressed:
        if not selected.id or int(selected.id) <= 0:
            st.error("Cannot extract: selected interaction has no valid id.")
        else:
            extracted = extract_for_interaction(selected)
            try:
                saved = upsert_extracted_fields(extracted)
            except Exception as e:
                st.error(f"Failed to save extracted fields: {e}")
            else:
                st.success(f"Saved extracted fields (id={saved.id})")
                # update the single source of truth for rendering
                current_extracted = saved

    # Render extracted fields once (either existing or newly saved)
    if current_extracted:
        st.markdown("**Extracted fields:**")
        st.markdown(f"**Summary:** {current_extracted.summary or ''}")
        st.markdown(f"**Intent:** {current_extracted.intent or ''}")
        st.markdown(f"**Suggested Action:** {current_extracted.suggested_action or ''}")
        st.markdown(f"**Confidence:** {current_extracted.confidence}")
        st.markdown(f"**Warnings:** {(current_extracted.warnings or 'None')}")
        st.markdown(f"**Extracted At:** {current_extracted.timestamp}")
    else:
        st.info("No extracted fields yet. Run extraction to generate them.")

    # Task creation area (minimal)
    st.divider()
    st.subheader("Task")

    existing_task = None
    if selected.id is not None:
        existing_task = get_task_by_interaction(int(selected.id))

    if existing_task:
        st.markdown("**Existing task for this interaction:**")
        st.markdown(f"**Title:** {existing_task.title}")
        st.markdown(f"**Status:** {existing_task.status}")
        st.markdown(f"**Created At:** {existing_task.created_at}")
        if existing_task.description:
            st.markdown(f"**Description:** {existing_task.description}")
    
    # ----------------------------
    # Template preview / compose helper (local-only)
    # ----------------------------
    st.divider()
    st.subheader("Template-based Preview (local only)")
    
    try:
        templates = list_templates()
    except Exception:
        templates = []
    
    if not templates:
        st.info("No templates saved. Create one from the Templates page.")
        return
    
    # Map to friendly labels: "id | name"
    tpl_options = [f"{t.id} | {t.name or '(untitled)'}" for t in templates]
    tpl_choice = st.selectbox("Choose a saved template (preview only)", options=["<none>"] + tpl_options, index=0)
    
    if tpl_choice and not tpl_choice.startswith("<none>"):
        try:
            tpl_id = int(tpl_choice.split("|", 1)[0].strip())
        except Exception:
            st.error("Failed to parse selected template")
            return
        tpl_map = {t.id: t for t in templates}
        tpl = tpl_map.get(tpl_id)
        if not tpl:
            st.error("Template not found")
            return
    
        st.markdown(f"**Template:** {tpl.name or '(untitled)'} — {tpl.channel or 'N/A'}")
        st.markdown("**This is a local preview only. This app does not send messages.**")
    
        # Small context hint: prefer extracted summary, fallback to interaction subject
        ctx_snippet = None
        if current_extracted and getattr(current_extracted, "summary", None):
            ctx_snippet = current_extracted.summary
        elif getattr(selected, "subject", None):
            ctx_snippet = (selected.subject or "")
    
        if ctx_snippet:
            st.markdown("**Local context (for reference):**")
            st.write(ctx_snippet)
    
        # Preview fields (read-only) so user sees exactly what would be used
        st.markdown("**Subject Preview**")
        st.text_input("", value=tpl.subject or "", disabled=True, key=f"tpl_subj_{tpl.id}")
    
        st.markdown("**Body Preview**")
        st.text_area("", value=tpl.body or "", disabled=True, height=220, key=f"tpl_body_{tpl.id}")
    else:
        # Only allow task creation if we have extracted fields to base it on
        if not current_extracted:
            st.info("No extracted context — run extraction first to create a task.")
        else:
            if st.button("Create Task"):
                # build a simple default task payload
                title = (current_extracted.suggested_action or current_extracted.intent or "Follow up")
                desc_parts = []
                if current_extracted.summary:
                    desc_parts.append(current_extracted.summary)
                if current_extracted.suggested_action:
                    desc_parts.append(current_extracted.suggested_action)
                description = "\n\n".join(desc_parts) if desc_parts else None

                task = Task(
                    interaction_id=int(selected.id),
                    extracted_fields_id=getattr(current_extracted, "id", None),
                    title=title,
                    description=description,
                    status="open",
                )

                try:
                    created_task = create_task(task)
                except Exception as e:
                    st.error(f"Failed to create task: {e}")
                else:
                    st.success(f"Created task id={created_task.id}")
                    st.markdown(f"**Title:** {created_task.title}")
                    st.markdown(f"**Status:** {created_task.status}")
                    if created_task.description:
                        st.markdown(f"**Description:** {created_task.description}")


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


def render_tasks() -> None:
    st.title("Task Queue")
    st.caption("Lightweight task list (Session 5)")

    tasks = list_tasks()
    st.write(f"Total tasks: **{len(tasks)}**")

    if not tasks:
        st.info("No tasks yet. Create one from an Interaction detail view.")
        return

    for t in tasks:
        header = f"{t.title or '(no title)'} — {t.status}"
        with st.expander(header):
            st.markdown(f"**ID:** {t.id}")
            st.markdown(f"**Interaction ID:** {t.interaction_id}")
            st.markdown(f"**Status:** {t.status}")
            due = "No due date"
            if getattr(t, "due_date", None):
                try:
                    due = t.due_date.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    due = str(t.due_date)
            st.markdown(f"**Due:** {due}")
            if getattr(t, "created_at", None):
                st.markdown(f"**Created At:** {t.created_at}")
            if t.description:
                st.markdown("**Description:**")
                st.write(t.description)

            # Lightweight status update control
            options = ["open", "in_progress", "done"]
            try:
                default_idx = options.index(t.status)
            except Exception:
                default_idx = 0

            new_status = st.selectbox("Update status", options=options, index=default_idx, key=f"status_{t.id}")
            if st.button("Apply", key=f"apply_{t.id}"):
                try:
                    updated = update_task_status(t.id, new_status)
                except Exception as e:
                    st.error(f"Failed to update status: {e}")
                else:
                    st.success(f"Updated task status to {updated.status}")


def render_templates() -> None:
    st.title("Templates")
    st.caption("Create and view stored templates (Session 6)")

    with st.form("create_template_form", clear_on_submit=False):
        name = st.text_input("Name", value="")
        channel = st.selectbox("Channel", options=["", "email", "whatsapp", "call"], index=0)
        template_type = st.text_input("Type (optional)", value="")
        subject = st.text_input("Subject", value="")
        body = st.text_area("Body", value="", height=200)

        submitted = st.form_submit_button("Create Template")

    if submitted:
        tpl = Template(
            name=(name or "").strip(),
            channel=(channel or None) if channel else None,
            template_type=(template_type or None) if template_type else None,
            subject=(subject or None) if subject else None,
            body=(body or None) if body else None,
        )

        try:
            created = create_template(tpl)
        except Exception as e:
            st.error(f"Failed to create template: {e}")
        else:
            st.success(f"Created template id={created.id}")

    st.divider()
    st.subheader("Saved Templates")

    templates = list_templates()
    st.write(f"Total templates: **{len(templates)}**")

    if not templates:
        st.info("No templates yet. Create one using the form above.")
        return

    for t in templates:
        header = f"{t.name or '(untitled)'} — {t.channel or 'N/A'}"
        with st.expander(header):
            st.markdown(f"**ID:** {t.id}")
            if t.template_type:
                st.markdown(f"**Type:** {t.template_type}")
            if t.subject:
                st.markdown(f"**Subject:** {t.subject}")
            if t.body:
                st.markdown("**Body:**")
                st.write(t.body)
            if getattr(t, "created_at", None):
                st.markdown(f"**Created At:** {t.created_at}")


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
        options=["Inbox", "Task Queue", "Templates", "Add Interaction", "About / Roadmap"],
        key="nav_page",
    )

    if page == "Inbox":
        render_inbox()
    elif page == "Task Queue":
        render_tasks()
    elif page == "Templates":
        render_templates()
    elif page == "Add Interaction":
        render_add_interaction()
    else:
        render_about()


if __name__ == "__main__":
    main()