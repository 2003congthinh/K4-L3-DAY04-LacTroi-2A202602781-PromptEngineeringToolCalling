from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from tools._shared import ROOT, err


TICKET_DIR = ROOT / "tickets"


def create_ticket(
    summary: str = "",
    priority: str = "medium",
    asset_id: str = "",
    confirmed: bool = False,
) -> dict[str, Any]:
    normalized_summary = (summary or "").strip()
    normalized_priority = (priority or "medium").strip().lower()
    if not normalized_summary:
        return {"tool": "create_ticket", "error": "missing_summary"}
    if normalized_priority not in {"low", "medium", "high", "critical"}:
        return {"tool": "create_ticket", "error": "invalid_priority", "priority": normalized_priority}
    if not confirmed:
        return {
            "tool": "create_ticket",
            "status": "needs_confirmation",
            "message": "Create the ticket only after explicit user confirmation.",
        }
    try:
        now = datetime.now(timezone.utc)
        normalized_asset = (asset_id or "").strip().upper()
        seed = f"{now.isoformat()}|{normalized_summary}|{normalized_priority}|{normalized_asset}"
        ticket_id = "LAB-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8].upper()
        payload = {
            "ticket_id": ticket_id,
            "summary": normalized_summary,
            "priority": normalized_priority,
            "asset_id": normalized_asset or None,
            "created_at": now.isoformat(),
            "source": "educational_local_mock",
        }
        TICKET_DIR.mkdir(parents=True, exist_ok=True)
        path = TICKET_DIR / f"{ticket_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"tool": "create_ticket", "status": "created", "ticket_id": ticket_id, "path": str(path)}
    except Exception as exc:
        return err("create_ticket", exc)
