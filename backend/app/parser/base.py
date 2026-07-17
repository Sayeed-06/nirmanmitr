"""Abstract base class for BOQ parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path


@dataclass
class ParsedRow:
    """A single parsed row from a BOQ document.

    This is the intermediate representation used by all parsers
    before DSR detection and database insertion.
    """

    order_index: int
    item_number: str | None = None
    description: str = ""
    quantity: Decimal | None = None
    unit: str | None = None
    rate: Decimal | None = None
    amount: Decimal | None = None
    depth: int = 0
    raw_text: str = ""

    @staticmethod
    def parse_decimal(value: str | float | int | None) -> Decimal | None:
        """Safely parse a value to Decimal, handling commas and units."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            try:
                return Decimal(str(value))
            except (InvalidOperation, ValueError):
                return None

        # Clean string: remove commas, currency symbols, whitespace
        cleaned = str(value).strip()
        cleaned = cleaned.replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "")
        cleaned = cleaned.strip()

        if not cleaned or cleaned in ("-", "—", "N/A", "n/a", ""):
            return None

        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None


@dataclass
class ParseResult:
    """Result from a BOQ parser."""

    rows: list[ParsedRow] = field(default_factory=list)
    source_file: str = ""
    total_pages: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None and len(self.rows) > 0


class BaseParser(ABC):
    """Abstract base class for BOQ document parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> ParseResult:
        """Parse a BOQ file and return structured rows.

        Args:
            file_path: Path to the uploaded file.

        Returns:
            ParseResult with extracted rows and metadata.
        """
        ...

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Check if this parser supports the given file type."""
        ...
