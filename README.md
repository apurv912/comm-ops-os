===== COPY START: README.md =====
# Communication Ops OS (ComOps) — v0.1 (Runnable Foundation)

Local-first “communication operations mini-OS” for tracking outreach interactions and later converting them into tasks + reporting.  
Built to be **engine-ready** for a future PR Outreach OS (PRO).

---

## 1) What this is
A lightweight local app (Streamlit + SQLite) that stores **Interactions** (channel-aware communication events) and shows an **Inbox** view.

## 2) Problem & why it matters (PM framing)
When outreach happens across channels (email today; WhatsApp/calls tomorrow), work becomes messy:
- follow-ups get missed
- context gets lost across tools
- reporting becomes manual and unreliable

ComOps is a local-first foundation to make outreach **trackable, queryable, and future-automatable**.

## 3) Who it’s for
- PR execs / agency associates
- founders doing outbound
- anyone managing recurring outreach + follow-ups who needs a simple system of record

## 4) MVP scope (what’s in / what’s out)
**In (v0.1):**
- Streamlit app boots
- SQLite DB auto-initializes on first run
- Inbox page renders a table of email interactions (may be empty)

**Out (explicitly not in v0.1):**
- email ingestion / Gmail integration
- WhatsApp/call logging UI
- task queue logic
- analytics/reporting
- RAG integration (not a priority right now)

## 5) Key PM decision: Interaction-first engine (why)
**Core record = Interaction, not Message.**

Reason:
- Email, WhatsApp, calls, meetings are all *interactions*.
- Modeling by interaction makes the engine reusable across channels.
- Prevents future refactors when PRO expands beyond email.

Inbox is simply: `Interaction where channel="email"`.

## 6) Tech stack
Streamlit + SQLModel + SQLite (+ python-dotenv)

## 7) How to run
```bash
cd ~/projects/comm-ops-os
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# optional config
cp .env.example .env

streamlit run app.py
8) Project structure

app.py — Streamlit UI shell + Inbox page

models.py — SQLModel tables (Contact, Interaction, Task)

db.py — engine/session helpers + auto table init

app.db — local SQLite database (created on first run)

9) Release Notes (v0.1 — Runnable Foundation)

✅ Bootable Streamlit app with a minimal navigation shell

✅ Auto-creates SQLite DB + tables on first run (app.db)

✅ Inbox table renders safely even with 0 rows (refresh-safe)

10) Screenshots

 Inbox page (empty state)

 DB created on first run

11) Learnings (placeholder)

 What modeling choice reduced future refactors?

 What was the smallest “releasable increment” and why?

 What tradeoffs did we accept to stay v0.1?