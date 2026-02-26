<<<<<<< HEAD
# Communication Ops OS (ComOps) — v0 (Local-first)
=======

# Communication Ops OS (ComOps) — v0.1 (Runnable Foundation)
>>>>>>> origin/main

A local-first “communication operations mini-OS” that stores outreach events and later turns them into tasks + reporting.

## Product idea (PM framing)
**Problem:** Outreach work (PR, partnerships, sales, recruiting) gets messy fast — follow-ups are missed, context is scattered, and reporting becomes manual.  
**Goal:** Build a small, reusable engine that records *communication events* and later converts them into tasks + reporting.

### Core decision (important)
We store **Interaction** (channel-aware event), not “Message”.
- Email is just: `Interaction where channel="email"`
- Later, WhatsApp/calls are also Interactions (same engine).

This keeps the core engine reusable for future **PR Outreach OS (PRO)**.

---

## Current Release: v0.2 — Sample Data Loader + Persistence Proof

### What shipped
- A button in the app: **“Load sample emails”**
- Seeds **3 sample email interactions** into SQLite (`app.db`)
- Clicking again does **NOT** create duplicates  
  (you’ll see “inserted=0, skipped=3” on the second click)

### “Idempotent” in simple words
You can click the load button multiple times, and it will **not duplicate** the same sample emails.

### Release notes (v0.2)
- Added an **idempotent sample email loader** (`sample_data.py`) that inserts 3 emails once
- Added a **Streamlit button** to load sample emails and show `inserted / skipped` counts
- Inbox lists seeded email interactions from SQLite (`app.db`) and persists across restarts

---

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# optional
cp .env.example .env

