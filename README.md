*** Begin README: ComOps v0.4 ***

# Communication Ops OS (ComOps) — v0.4 (Extraction Pipeline)

A local-first “communication operations mini-OS” that stores outreach events and incrementally turns them into operational artifacts (extractions, tasks, reports).
# Communication Ops OS (ComOps) — v0.6 (Templates + Execution Speed Layer)

A compact, local-first “communication operations mini-OS” for operators to capture interactions, extract structured context, and iterate toward lightweight execution patterns.

## Problem / Why this exists
Outreach workflows (PR, partnerships, recruiting, sales) are operationally heavy: context is scattered, follow-ups slip, and lightweight reuse of content is hard. ComOps is a local, minimal system-of-record that helps operators capture interactions and turn them into action artifacts with low friction.

## User
Product operators, partnership leads, and early-stage GTM practitioners who want a portable, privacy-first inbox + lightweight task and template tooling for reliable follow-ups.

## Scope (v0.6)
- Local-first storage of `Interaction`, `ExtractedFields`, `Task`, and `Template` records (SQLite).
- Create / view Interactions, run local extraction, create Tasks from extraction context.
- Create, list, and preview Templates in-app (local-only, read-only preview in Interaction context).

### What v0.6 adds
- `Template` model persisted in SQLite (name, channel, type, subject, body, timestamps).
- UI to create and manage Templates (Session 6 Templates page).
- Lightweight template-use flow in the Interaction Detail view: select a stored Template and preview Subject/Body locally (compose preview only — does not send).
- Small DB repair helpers ensure backward-compatible lightweight schema evolution on startup.

## Product flow / architecture
- `app.py` — Streamlit UI (Inbox, Interaction Detail, Templates, Task Queue)
- `models.py` — SQLModel table definitions: `Interaction`, `ExtractedFields`, `Task`, `Template`
- `extraction.py` — deterministic extractor that produces `ExtractedFields` from an `Interaction`
- `db.py` — SQLite engine, create/repair helpers, and CRUD helpers for all models

Typical Template preview flow (v0.6):
1. User selects an Interaction in Inbox → Detail View.
2. Optionally run extraction to build contextual `ExtractedFields`.
3. From the Detail View, open the Template chooser and pick a stored Template.
4. The app shows a read-only Subject and Body preview, and a small local context snippet (interaction subject or extracted summary) for reference.

This flow is explicitly local-only and intended as a copy/paste or reference helper in early product iterations.

## Why Templates are kept lightweight
- Avoids premature complexity (placeholder engines, variable interpolation, delivery integrations).
- Keeps surface area small for a portfolio demo while enabling meaningful reuse patterns.
- Local persistence ensures safety, privacy, and reproducibility for evaluators.

## What is out of scope (explicitly)
- Sending messages, delivery integrations, or scheduling.
- Advanced templating, placeholder resolution, or personalisation engines.
- Multi-user syncing, webhooks, or audit trails.

## Local-first persistence note
All data is stored in `app.db` (SQLite). On first run the app will create necessary tables; the included lightweight repair helpers add missing columns for backward compatibility without destructive migrations.

## Screenshots (placeholders)
- `docs/screenshots/v0.6-templates-list.png` — Templates page (create + list)
- `docs/screenshots/v0.6-interaction-template-preview.png` — Interaction detail showing Template preview

## Roadmap / session progression
- v0.3: Basic Inbox, Add Interaction, stable selection, Detail View
- v0.4: Local extraction pipeline (`ExtractedFields`)
- v0.5: Task model & Task Queue (create tasks from extraction)
- v0.6: Templates (create, store, local preview) — this release

## Key learnings & tradeoffs
- Shipping small, composable primitives (Interaction → ExtractedFields → Task → Template) keeps scope manageable.
- SQLite + SQLModel makes the project runnable and inspectable for interview/portfolio use.
- Lightweight schema repair via PRAGMA + `ALTER TABLE` is practical for single-user local demos but not a substitute for proper migrations in production.

## Quick run (same as before)
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python -m streamlit run app.py
```

> For a fresh demo, stop Streamlit and remove `app.db`.

## Repo structure (quick)
- `app.py` — Streamlit UI
- `models.py` — SQLModel table definitions
- `db.py` — SQLite engine + init/repair + CRUD helpers
- `extraction.py` — deterministic extractor
- `requirements.txt` — Python deps for local run

## License / usage
Portfolio / learning project. Use freely for experimentation.

*** End README: ComOps v0.6 ***


---
