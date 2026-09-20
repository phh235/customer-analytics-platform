"""Helpers for stable, human-readable entity reference codes."""

from __future__ import annotations


def next_reference_code(prefix: str, existing_codes: list[str | None]) -> str:
    """Return the next numeric reference code for a prefix."""
    highest = 0
    marker = f"{prefix}-"

    for code in existing_codes:
        if not code or not code.startswith(marker):
            continue
        suffix = code.removeprefix(marker)
        if suffix.isdigit():
            highest = max(highest, int(suffix))

    return f"{marker}{highest + 1:06d}"
