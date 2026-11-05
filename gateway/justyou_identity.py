"""Optional, read-only JustYou identity projection for admitted gateway messages.

The binding is an operator-enrolled *candidate*, never authentication or
authorization. It cannot change Hermes' source, session routing, or privileges.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


def annotate_admitted_event(event: Any, database: str | Path) -> bool:
    """Project a pre-enrolled channel address into metadata AFTER gateway admission.

    A missing configured DB raises: operator configuration must not silently
    degrade into a different identity interpretation.
    """
    source = event.source
    platform = getattr(getattr(source, "platform", None), "value", None)
    address = getattr(source, "user_id", None)
    # Identity binding follows the receiving transport, not the routed runtime.
    from gateway.session_identity import identity_of
    routing = identity_of(source)
    profile = routing.transport_profile if routing else (getattr(source, "profile", None) or "default")
    if not platform or not address or getattr(event, "internal", False):
        return False
    with sqlite3.connect(f"file:{Path(database).resolve()}?mode=ro", uri=True, timeout=3) as connection:
        row = connection.execute(
            "SELECT principal_id, relationship_id, binding_id FROM bindings "
            "WHERE channel=? AND scope=? AND address=? AND active=1",
            (str(platform), str(profile), str(address)),
        ).fetchone()
    if row is None:
        return False
    if not isinstance(event.metadata, dict):
        raise TypeError("Hermes event metadata must be dict")
    event.metadata["justyou_identity_candidate_v1"] = {
        "principal_id": row[0],
        "relationship_id": row[1],
        "binding_id": row[2],
        "sender_authenticated": False,
        "execution_authorized": False,
    }
    return True


def annotate_if_configured(event: Any) -> bool:
    """No-op by default. Explicit env opt-in only, with existing Hermes auth intact."""
    database = os.environ.get("JUSTYOU_COMM_BINDINGS_DB")
    return annotate_admitted_event(event, database) if database else False



def diagnostic_reply(event: Any) -> str | None:
    """Deterministic response for an already admitted user message.

    Caller MUST run Hermes admission, pause gate and pending-control handlers
    first. This is diagnostic text only and never grants tool authority.
    """
    if getattr(event, "internal", False) or not isinstance(getattr(event, "text", None), str):
        return None
    if event.text.strip().casefold() != "justyou verify":
        return None
    source = event.source
    platform = getattr(getattr(source, "platform", None), "value", None) or "unknown"
    binding = event.metadata.get("justyou_identity_candidate_v1", {}) if isinstance(event.metadata, dict) else {}
    principal = binding.get("principal_id") if isinstance(binding, dict) else None
    safe_principal = principal if isinstance(principal, str) and principal.isascii() and principal.replace("-", "").replace("_", "").isalnum() and len(principal) <= 64 else "none"
    return (
        "JustYou / Hermes diagnose\n"
        f"Kanal: {platform}\n"
        "Hermes avsenderkontroll: ADMITTED\n"
        f"Identitetskandidat: {safe_principal}\n"
        f"Binding: {'FOUND' if principal else 'NOT_FOUND'}\n"
        "Avsender kryptografisk verifisert av JustYou: NEI\n"
        "REHT utførelsestillatelse: IKKE UTSTEDT\n"
        "Diagnose gir ingen ny handlingsfullmakt."
    )
