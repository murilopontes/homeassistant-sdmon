"""Parse sdmon JSON output."""

from __future__ import annotations

from typing import Any


def parse_sdmon_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize sdmon JSON into integration-friendly data."""
    success = bool(payload.get("success"))
    error = payload.get("error")
    if not error:
        for key in ("error1", "error2"):
            if payload.get(key):
                error = payload[key]
                break

    health = None
    card_type = "unknown"
    if HEALTH := payload.get("enduranceRemainLifePercent"):
        health = float(HEALTH)
        card_type = "endurance"
    elif used := payload.get("healthStatusPercentUsed"):
        health = max(0.0, 100.0 - float(used))
        card_type = "health"

    product = payload.get("productString")
    if isinstance(product, str):
        product = product.strip() or None

    return {
        "success": success,
        "error": error,
        "health": health,
        "card_type": card_type,
        "device": payload.get("device"),
        "sdmon_version": payload.get("version"),
        "product": product,
        "raw": payload,
    }


def metric_value(payload: dict[str, Any], key: str) -> Any:
    """Return a metric value when present."""
    if key not in payload:
        return None
    value = payload[key]
    if value in (None, ""):
        return None
    return value
