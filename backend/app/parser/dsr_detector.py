"""DSR item number detector using deterministic regex matching.

This module is responsible for detecting CPWD Delhi Schedule of Rates
item numbers from BOQ item descriptions and item number fields.

NO AI or ML is used. All detection is purely regex-based.
"""

from __future__ import annotations

import re
import structlog
from dataclasses import dataclass

logger = structlog.get_logger()

# ─── DSR Item Number Patterns ───
# Ordered from most specific to least specific.
# Each pattern captures the core item number (e.g., "5.33.1").

DSR_PATTERNS: list[re.Pattern] = [
    # "CPWD DSR 5.33.1" or "CPWD DSR Item 5.33"
    re.compile(
        r"(?:CPWD\s+)?DSR\s+(?:Item\s+)?(\d{1,2}\.\d{1,3}(?:\.\d{1,3}){0,3})",
        re.IGNORECASE,
    ),
    # "Item No. 5.33" or "Item 5.33.1"
    re.compile(
        r"Item\s+(?:No\.?\s*)?(\d{1,2}\.\d{1,3}(?:\.\d{1,3}){0,3})",
        re.IGNORECASE,
    ),
    # "Sr. No. 5.33" or "S.No. 5.33.1"
    re.compile(
        r"(?:Sr|S)\.?\s*No\.?\s*(\d{1,2}\.\d{1,3}(?:\.\d{1,3}){0,3})",
        re.IGNORECASE,
    ),
    # Standalone item number at start of text is TOO aggressive.
    # The user explicitly wants it to only match if it says "refer cpwd dsr item_code"
    # So we remove the aggressive standalone matching patterns.
    # re.compile(r"^(\d{1,2}\.\d{1,3}(?:\.\d{1,3}){0,3})\b"),
    # re.compile(r"\b(\d{1,2}\.\d{1,3}(?:\.\d{1,3}){0,3})\b"),
]

# Numbers that are clearly NOT DSR item numbers
FALSE_POSITIVE_PATTERNS = [
    re.compile(r"^\d{4}\.\d{1,2}$"),          # Year-like: 2024.01
    re.compile(r"^\d+\.\d{4,}$"),              # Long decimal: 3.14159
    re.compile(r"^0\.\d+$"),                    # Starts with 0: 0.5
    re.compile(r"^\d{3,}\.\d+$"),              # Too many digits before dot: 100.5
]


@dataclass
class DSRMatch:
    """Result of DSR detection for a single BOQ item."""

    detected_number: str | None
    confidence: str  # "exact", "partial", "none"
    source: str  # "item_number", "description", "none"
    original_text: str


class DSRDetector:
    """Deterministic DSR item number detector.

    Uses regex patterns to extract CPWD DSR item numbers from
    BOQ item number fields and description text. No AI involved.
    """

    def __init__(self, known_items: set[str] | None = None) -> None:
        """Initialize with optional set of known DSR item numbers.

        Args:
            known_items: Set of valid item numbers from the database.
                         Used to upgrade "partial" matches to "exact".
        """
        self.known_items = known_items or set()

    def detect(
        self,
        item_number: str | None,
        description: str | None,
    ) -> DSRMatch:
        """Detect DSR item number from a BOQ row.

        Args:
            item_number: The item number field from the BOQ.
            description: The description text from the BOQ.

        Returns:
            DSRMatch with the detected number and confidence level.
        """
        # Strategy 1: Check the item_number field first (highest confidence)
        if item_number:
            cleaned = self._normalize(item_number)
            match = self._extract_number(cleaned)
            if match and not self._is_false_positive(match):
                confidence = "exact" if match in self.known_items else "partial"
                return DSRMatch(
                    detected_number=match,
                    confidence=confidence,
                    source="item_number",
                    original_text=item_number,
                )

        # Strategy 2: Search within the description text
        if description:
            match = self._extract_from_text(description)
            if match and not self._is_false_positive(match):
                confidence = "exact" if match in self.known_items else "partial"
                return DSRMatch(
                    detected_number=match,
                    confidence=confidence,
                    source="description",
                    original_text=description[:200],
                )

        return DSRMatch(
            detected_number=None,
            confidence="none",
            source="none",
            original_text=(item_number or description or "")[:200],
        )

    def detect_batch(
        self,
        rows: list[tuple[str | None, str | None]],
    ) -> list[DSRMatch]:
        """Detect DSR numbers for multiple rows.

        Args:
            rows: List of (item_number, description) tuples.

        Returns:
            List of DSRMatch results in the same order.
        """
        return [self.detect(item_num, desc) for item_num, desc in rows]

    def _normalize(self, text: str) -> str:
        """Normalize text for DSR number extraction.

        Removes common prefixes like "DSR", "CPWD", "Item" and
        strips whitespace.
        """
        cleaned = text.strip()
        # Remove common prefixes
        cleaned = re.sub(r"^(?:CPWD\s+)?(?:DSR\s+)?(?:Item\s+)?(?:No\.?\s*)?", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _extract_number(self, text: str) -> str | None:
        """Extract a DSR item number from normalized text."""
        # Direct match: the text IS the item number
        direct = re.match(r"^(\d{1,2}\.\d{1,3}(?:\.\d{1,3}){0,3})$", text.strip())
        if direct:
            return direct.group(1)

        # Search with patterns
        return self._extract_from_text(text)

    def _extract_from_text(self, text: str) -> str | None:
        """Search for a DSR item number within text using ordered patterns."""
        for pattern in DSR_PATTERNS:
            match = pattern.search(text)
            if match:
                number = match.group(1)
                if not self._is_false_positive(number):
                    return number
        return None

    def _is_false_positive(self, number: str) -> bool:
        """Check if a detected number is a false positive."""
        for pattern in FALSE_POSITIVE_PATTERNS:
            if pattern.match(number):
                return True
        return False
