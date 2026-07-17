"""CSV parser using pandas."""

from __future__ import annotations

import re
import structlog
from pathlib import Path

import pandas as pd

from app.parser.base import BaseParser, ParsedRow, ParseResult

logger = structlog.get_logger()


class CSVParser(BaseParser):
    """Parse BOQ tables from CSV files using pandas.

    Strategy:
    1. Read CSV with pandas (handles encoding, delimiters)
    2. Auto-detect or match column headers
    3. Extract rows with data cleaning
    """

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".csv"

    def parse(self, file_path: Path) -> ParseResult:
        """Parse a CSV BOQ document."""
        result = ParseResult(source_file=str(file_path))

        try:
            # Try common encodings
            df = None
            for encoding in ("utf-8", "latin-1", "cp1252"):
                try:
                    df = pd.read_csv(str(file_path), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                result.error = "Could not decode CSV file with any supported encoding"
                return result

            # Clean column names
            df.columns = [str(c).strip() for c in df.columns]

            # Map columns
            col_mapping = self._detect_columns(df.columns.tolist())

            if not col_mapping:
                result.error = "Could not detect BOQ column structure in CSV"
                result.warnings.append(f"Columns found: {df.columns.tolist()}")
                return result

            rows: list[ParsedRow] = []
            for idx, (_, row) in enumerate(df.iterrows()):
                parsed = self._extract_row(row, col_mapping, idx)
                if parsed and parsed.description.strip():
                    rows.append(parsed)

            result.rows = rows
            result.total_pages = 1
            logger.info("csv_parse_complete", file=file_path.name, rows=len(rows))
        except Exception as e:
            result.error = f"CSV parsing failed: {e!s}"
            logger.error("csv_parse_error", file=str(file_path), error=str(e))

        return result

    def _detect_columns(self, columns: list[str]) -> dict[str, str] | None:
        """Map DataFrame columns to BOQ fields.

        Returns dict mapping field_name → column_name.
        """
        mapping: dict[str, str] = {}
        matches = 0

        for col in columns:
            lower = col.lower().strip()
            if re.search(r"s\.?\s*no|sr\.?\s*no|sl\.?\s*no", lower):
                mapping["serial"] = col
                matches += 1
            elif re.search(r"item\s*no|item\s*number|dsr\s*no", lower):
                mapping["item_number"] = col
                matches += 1
            elif re.search(r"description|particulars|item\s*of\s*work", lower):
                mapping["description"] = col
                matches += 1
            elif re.search(r"quant|qty", lower):
                mapping["quantity"] = col
                matches += 1
            elif re.search(r"^unit$", lower):
                mapping["unit"] = col
                matches += 1
            elif re.search(r"^rate$|rate\s*per", lower):
                mapping["rate"] = col
                matches += 1
            elif re.search(r"amount|total|value", lower):
                mapping["amount"] = col
                matches += 1

        if "description" in mapping and matches >= 3:
            return mapping
        return None

    def _extract_row(
        self, row: pd.Series, mapping: dict[str, str], order_idx: int
    ) -> ParsedRow | None:
        """Extract a ParsedRow from a pandas row."""
        def get_val(key: str) -> str | None:
            col = mapping.get(key)
            if col and col in row.index:
                val = row[col]
                if pd.notna(val):
                    return str(val).strip()
            return None

        description = get_val("description") or ""
        if not description or len(description) < 2:
            return None

        item_num = get_val("item_number") or get_val("serial")
        depth = 0
        if item_num:
            parts = item_num.split(".")
            if len(parts) > 1:
                depth = len(parts) - 1

        return ParsedRow(
            order_index=order_idx,
            item_number=item_num,
            description=description,
            quantity=ParsedRow.parse_decimal(get_val("quantity")),
            unit=get_val("unit"),
            rate=ParsedRow.parse_decimal(get_val("rate")),
            amount=ParsedRow.parse_decimal(get_val("amount")),
            depth=depth,
        )
