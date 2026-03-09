*** Begin README: ComOps v0.4 ***

# Communication Ops OS (ComOps) — v0.4 (Extraction Pipeline)

A local-first “communication operations mini-OS” that stores outreach events and incrementally turns them into operational artifacts (extractions, tasks, reports).

## Problem / Why this exists
Outreach work (PR, partnerships, sales, recruiting) gets scattered: follow-ups are missed, context is fragmented, and manual reporting is expensive. ComOps offers a compact, local-first system of record so operators can capture interactions reliably and iterate toward automation.

### Core decision
We store **Interaction** (a channel-aware event) as the core record — not individual messages. This keeps the model flexible across channels (email, WhatsApp, calls) and easy to extend.

---

## Current user flow (v0.4)
- Add Interaction via the form (default channel = `email`).
- View the Inbox (newest-first), select an interaction to see the Detail View.
- From the Detail View, click **Run extraction** to produce structured `ExtractedFields` and persist them to the DB.
- Re-run extraction updates the same extracted row (no duplicates).

---

## Current scope through v0.4
- Manual ingestion (create Interaction)
- Inbox + stable selection + Detail View
- Local extraction pipeline (deterministic, local-only)
- `ExtractedFields` persisted per-Interaction (one row per Interaction)

### Not included
- External AI/LLM calls or integrations
- Task queue, templates, reporting (planned for later sessions)

---

## v0.4 — Release summary
- `ExtractedFields` model: one row per `Interaction` to store extraction results.
- `extraction.py`: deterministic local extractor that builds an `ExtractedFields` object from an `Interaction`.
- `db.py`: helpers `get_extracted_fields()` and `upsert_extracted_fields()` for idempotent persistence.
- `app.py`: UI action to run extraction from the Detail View; displays Summary, Intent, Suggested Action, Confidence, Warnings, and Extracted At.

---

## Product decisions & tradeoffs
- Local-first SQLite for a runnable portfolio demo.
- Deterministic extraction (no external services) keeps Session 4 focused and reproducible.
- Lightweight migration approach (ad-hoc checks + ALTER TABLE) avoids adding a migrations framework.

---

## Lightweight architecture / pipeline
- `app.py` — Streamlit UI (Inbox, Add Interaction, Detail View, Run extraction)
- `models.py` — `Interaction` and `ExtractedFields` SQLModel definitions
- `extraction.py` — deterministic, local-only extraction logic
- `db.py` — engine + schema init + helpers (`get_extracted_fields`, `upsert_extracted_fields`)

Extraction flow (v0.4):
1. User selects an Interaction.
2. Clicks “Run extraction”.
3. `extract_for_interaction()` produces an `ExtractedFields` object.
4. `upsert_extracted_fields()` saves it (insert or update existing row).

---

## Test checklist for v0.4 (manual smoke tests)
- T1: Create an Interaction → confirm success message.
- T2: Select Interaction → run extraction → success message appears.
- T3: Confirm extracted fields (Summary, Intent, Suggested Action, Confidence, Warnings, Extracted At) are displayed.
- T4: Re-run extraction for same Interaction → no duplicate rows; existing row is updated.
- T5: Restart Streamlit → saved extracted fields persist and reappear.

---

## Next roadmap
- **Session 5:** Task queue (convert Interactions → follow-up tasks). This is the next discrete scope.

---

## Screenshots (placeholders)
- `docs/screenshots/v0.4-inbox.png`
![alt text](image-1.png)
- `docs/screenshots/v0.4-detail-extraction.png`
![alt text](image-2.png)

---

## Repo structure (quick)
- `app.py` — Streamlit UI
- `models.py` — SQLModel table definitions (`Interaction`, `ExtractedFields`)
- `db.py` — SQLite engine + init/migration + CRUD helpers
- `extraction.py` — deterministic local extraction helper
- `app.db` — local SQLite database (gitignored)

---

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python -m streamlit run app.py
```

> If you want a “fresh start”, stop Streamlit and delete `app.db`, then rerun.

---

## Key PM decisions & tradeoffs (summary)
- **Interaction-first** model to keep engine reusable across channels.
- **Local-first SQLite** to ship fast and keep the demo runnable.
- **Deterministic local extraction** for Session 4 to limit scope and dependency surface.

---

## License / usage
Portfolio / learning project. Use freely for experimentation.

*** End README: ComOps v0.4 ***

===== COPY END: README.md (FULL FILE) =====