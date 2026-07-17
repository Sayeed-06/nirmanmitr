"""Test configuration and fixtures."""

from __future__ import annotations

import pytest
from app.parser.dsr_detector import DSRDetector


@pytest.fixture
def dsr_detector() -> DSRDetector:
    """Create a DSR detector with sample known items."""
    known = {"5.33", "5.33.1", "7.1", "7.1.2", "9.44", "12.1.1"}
    return DSRDetector(known_items=known)


@pytest.fixture
def sample_boq_rows() -> list[tuple[str | None, str | None]]:
    """Sample BOQ rows for testing DSR detection."""
    return [
        ("5.33", "Providing and laying cement concrete 1:4:8"),
        ("DSR 7.1", "Brick work in cement mortar 1:6"),
        ("Item 9.44", "Plastering with cement mortar"),
        (None, "CPWD DSR 12.1.1 Providing and fixing steel"),
        ("ABC-123", "Some non-DSR item"),
        (None, "General excavation work"),
        ("5.33.1", None),
    ]
