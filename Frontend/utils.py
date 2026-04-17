"""Frontend formatting helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from frontend.design_system import C


def score_color(score):
    score = score or 0
    if score >= 70:
        return C["green"]
    if score >= 50:
        return C["orange"]
    return C["red"]


def relative_time(raw: str, fallback: str = "-") -> str:
    if not raw:
        return fallback
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = datetime.strptime(str(raw), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return str(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "just-now"
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h"
    days = hours // 24
    return f"{days}d"
