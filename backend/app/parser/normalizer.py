"""Data normalization and post-processing for parsed BOQ items."""

from __future__ import annotations

import re

from app.parser.base import ParsedRow


def normalize_rows(rows: list[ParsedRow]) -> list[ParsedRow]:
    """Post-process parsed rows: clean text, fix hierarchy, remove junk.

    Applied after initial parsing, before DSR detection.
    """
    cleaned: list[ParsedRow] = []

    for row in rows:
        # Clean description
        row.description = _clean_text(row.description)

        # Clean item number
        if row.item_number:
            row.item_number = row.item_number.strip()

        # Skip empty or header-like rows
        if _is_junk_row(row):
            continue

        cleaned.append(row)

    # Re-index
    for idx, row in enumerate(cleaned):
        row.order_index = idx

    return cleaned


def _clean_text(text: str) -> str:
    """Clean description text."""
    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Remove stray special characters
    text = re.sub(r"^[\-\*\•\◦]+\s*", "", text)
    return text


def _is_junk_row(row: ParsedRow) -> bool:
    """Detect rows that should be skipped (headers, totals, blanks)."""
    desc = row.description.lower()

    # Too short
    if len(desc) < 3:
        return True

    # Repeated header text
    header_patterns = [
        "description of item",
        "item of work",
        "particulars",
        "schedule of quantities",
        "bill of quantities",
        "page no",
        "grand total",
        "sub total",
        "carried over",
        "brought forward",
        "total of",
    ]
    for pattern in header_patterns:
        if pattern in desc:
            return True

    # All numeric
    if re.match(r"^[\d\s.,\-]+$", row.description):
        return True

    return False
