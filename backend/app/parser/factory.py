"""Parser factory — selects the appropriate parser by file type."""

from __future__ import annotations

from pathlib import Path

from app.parser.base import BaseParser
from app.parser.pdf_parser import PDFParser
from app.parser.excel_parser import ExcelParser
from app.parser.csv_parser import CSVParser


_PARSERS: list[BaseParser] = [
    PDFParser(),
    ExcelParser(),
    CSVParser(),
]


def create_parser(file_path: str | Path) -> BaseParser:
    """Return the appropriate parser for the given file type.

    Args:
        file_path: Path to the BOQ file.

    Returns:
        A parser instance that can handle the file.

    Raises:
        ValueError: If no parser supports the file type.
    """
    path = Path(file_path)

    for parser in _PARSERS:
        if parser.supports(path):
            return parser

    supported = ", ".join(p.__class__.__name__ for p in _PARSERS)
    raise ValueError(
        f"Unsupported file type: {path.suffix}. "
        f"Supported parsers: {supported}"
    )
