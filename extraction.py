from typing import Optional

from models import Interaction, ExtractedFields


def _first_meaningful_text(body: str, limit: int = 160) -> str:
    if not body:
        return ""
    text = " ".join(body.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0]


def _detect_intent(subject: str, body: str) -> Optional[str]:
    text = " ".join([subject or "", body or ""]).lower()
    if any(k in text for k in ("follow up", "follow-up", "checking in")):
        return "follow_up"
    if any(k in text for k in ("meeting", "schedule", "call")):
        return "meeting"
    if any(k in text for k in ("info", "details", "share", "send")):
        return "information"
    return None


def extract_for_interaction(interaction: Interaction) -> ExtractedFields:
    """Return an UNSAVED ExtractedFields object for the given Interaction.

    Defensive: if `interaction.id` is None, use -1 as a placeholder for
    `interaction_id` so the returned object always contains an int.
    """
    subj = (interaction.subject or "").strip()
    body = (interaction.body or "").strip()

    # Summary: prefer subject, otherwise first meaningful chars of body
    if subj:
        summary = subj
    else:
        summary = _first_meaningful_text(body)

    # Intent detection via simple keyword matching
    intent = _detect_intent(subj, body) or "general"

    # Suggested action by intent
    if intent == "follow_up":
        suggested_action = "Review and follow up"
    elif intent == "meeting":
        suggested_action = "Review and schedule response"
    elif intent == "information":
        suggested_action = "Review and send information"
    else:
        suggested_action = "Review manually"

    # Confidence: higher when intent matched by keywords
    if intent in ("follow_up", "meeting", "information"):
        confidence = 0.8
    elif summary:
        confidence = 0.5
    else:
        confidence = 0.2

    # Warnings
    warns = []
    if not subj:
        warns.append("missing_subject")
    if not body:
        warns.append("missing_body")
    if not getattr(interaction, "contact_email", None):
        warns.append("missing_contact_email")
    warnings = ";".join(warns)

    interaction_id = interaction.id if (interaction.id is not None) else -1

    extracted = ExtractedFields(
        interaction_id=interaction_id,
        summary=summary,
        intent=intent,
        suggested_action=suggested_action,
        confidence=confidence,
        warnings=warnings,
    )

    return extracted
