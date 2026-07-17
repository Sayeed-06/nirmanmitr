"""Tests for DSR item number detector."""

from __future__ import annotations

import pytest
from app.parser.dsr_detector import DSRDetector


@pytest.fixture
def detector() -> DSRDetector:
    """Detector with known DSR items."""
    known = {"5.33", "5.33.1", "7.1", "7.1.2", "9.44", "12.1.1"}
    return DSRDetector(known_items=known)


@pytest.fixture
def detector_no_known() -> DSRDetector:
    """Detector without known items (all matches are 'partial')."""
    return DSRDetector()


class TestDSRDetection:
    """Tests for the core DSR detection logic."""

    def test_exact_item_number(self, detector: DSRDetector) -> None:
        """Direct item number field with known DSR number."""
        match = detector.detect("5.33", None)
        assert match.detected_number == "5.33"
        assert match.confidence == "exact"
        assert match.source == "item_number"

    def test_prefixed_dsr(self, detector: DSRDetector) -> None:
        """DSR prefix in item number field."""
        match = detector.detect("DSR 7.1", None)
        assert match.detected_number == "7.1"
        assert match.confidence == "exact"

    def test_cpwd_dsr_prefix(self, detector: DSRDetector) -> None:
        """Full CPWD DSR prefix."""
        match = detector.detect("CPWD DSR 5.33.1", None)
        assert match.detected_number == "5.33.1"
        assert match.confidence == "exact"

    def test_item_prefix(self, detector: DSRDetector) -> None:
        """Item prefix."""
        match = detector.detect("Item 9.44", None)
        assert match.detected_number == "9.44"
        assert match.confidence == "exact"

    def test_description_detection(self, detector: DSRDetector) -> None:
        """DSR number in description text."""
        match = detector.detect(
            None,
            "CPWD DSR 12.1.1 Providing and fixing steel work"
        )
        assert match.detected_number == "12.1.1"
        assert match.confidence == "exact"
        assert match.source == "description"

    def test_no_match(self, detector: DSRDetector) -> None:
        """No DSR number found."""
        match = detector.detect("ABC-123", "General cleaning work")
        assert match.detected_number is None
        assert match.confidence == "none"

    def test_false_positive_year(self, detector: DSRDetector) -> None:
        """Year-like numbers should not match."""
        match = detector.detect("2024.01", None)
        assert match.detected_number is None

    def test_false_positive_decimal(self, detector: DSRDetector) -> None:
        """Long decimals should not match."""
        match = detector.detect("3.14159", None)
        assert match.detected_number is None

    def test_partial_match_unknown_item(self, detector: DSRDetector) -> None:
        """Valid format but not in known items."""
        match = detector.detect("99.99", None)
        assert match.detected_number == "99.99"
        assert match.confidence == "partial"

    def test_nested_item_number(self, detector: DSRDetector) -> None:
        """Multi-level item number."""
        match = detector.detect("5.33.1", None)
        assert match.detected_number == "5.33.1"
        assert match.confidence == "exact"

    def test_batch_detection(self, detector: DSRDetector) -> None:
        """Batch detection of multiple items."""
        rows = [
            ("5.33", "Cement concrete"),
            (None, "DSR 7.1 Brick work"),
            ("unknown", "No DSR reference here"),
        ]
        results = detector.detect_batch(rows)
        assert len(results) == 3
        assert results[0].confidence == "exact"
        assert results[1].confidence == "exact"
        assert results[2].confidence == "none"

    def test_item_number_priority_over_description(self, detector: DSRDetector) -> None:
        """Item number field should take priority over description."""
        match = detector.detect("5.33", "This refers to DSR 7.1 brick work")
        assert match.detected_number == "5.33"
        assert match.source == "item_number"
