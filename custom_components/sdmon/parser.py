"""Parse sdmon JSON output."""

from __future__ import annotations

import re
from typing import Any

_TB_PATTERN = re.compile(r"^([0-9]+(?:\.[0-9]+)?)\s*TB$", re.IGNORECASE)
_GB_PATTERN = re.compile(r"^([0-9]+(?:\.[0-9]+)?)\s*GB$", re.IGNORECASE)


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
    elif remain := payload.get("remainLifeTime"):
        if isinstance(remain, str) and remain.endswith("%"):
            health = float(remain.rstrip("%"))
        else:
            health = float(remain)
        card_type = "longsys"

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


def parse_tb_string_to_bytes(value: str) -> int | None:
    """Convert sdmon size strings such as 0.58TB to bytes."""
    text = value.strip()
    if match := _TB_PATTERN.match(text):
        return int(float(match.group(1)) * 1024**4)
    if match := _GB_PATTERN.match(text):
        return int(float(match.group(1)) * 1024**3)
    return None


def metric_value(payload: dict[str, Any], definition: dict[str, Any] | str) -> Any:
    """Return a metric value from sdmon JSON using key fallbacks and transforms."""
    if isinstance(definition, str):
        definition = {"key": definition}

    candidates = definition.get("candidates")
    if not candidates:
        key = definition.get("key")
        if not key:
            return None
        candidates = [
            {
                "key": key,
                "multiplier": definition.get("multiplier", 1),
                "transform": definition.get("transform"),
            }
        ]

    for candidate in candidates:
        key = candidate.get("key")
        if not key or key not in payload:
            continue
        value = payload[key]
        if value in (None, ""):
            continue

        transform = candidate.get("transform")
        if transform == "tb_string":
            parsed = parse_tb_string_to_bytes(str(value))
            if parsed is not None:
                return parsed
            continue

        multiplier = candidate.get("multiplier", 1)
        if multiplier != 1:
            return int(value) * multiplier
        return value

    return None
