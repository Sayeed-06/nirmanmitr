"""PDF parser using pdfplumber with camelot fallback."""

from __future__ import annotations

import re
import structlog
from pathlib import Path

from app.parser.base import BaseParser, ParsedRow, ParseResult

logger = structlog.get_logger()

# Common BOQ header patterns to identify the table structure
HEADER_PATTERNS = [
    re.compile(r"s\.?\s*no\.?|sr\.?\s*no\.?|sl\.?\s*no\.?", re.IGNORECASE),
    re.compile(r"item\s*no\.?|item\s*number", re.IGNORECASE),
    re.compile(r"description|particulars|item\s*of\s*work", re.IGNORECASE),
    re.compile(r"quant|qty", re.IGNORECASE),
    re.compile(r"unit", re.IGNORECASE),
    re.compile(r"rate", re.IGNORECASE),
    re.compile(r"amount|total", re.IGNORECASE),
]


class PDFParser(BaseParser):
    """Parse BOQ tables from PDF files using pdfplumber.

    Strategy:
    1. Extract all tables from each page using pdfplumber
    2. Detect the header row by matching common BOQ column names
    3. Map columns to ParsedRow fields
    4. Handle multi-page table continuation
    5. Fallback to camelot if pdfplumber yields poor results
    """

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    def parse(self, file_path: Path) -> ParseResult:
        """Parse a PDF BOQ document."""
        result = ParseResult(source_file=str(file_path))

        try:
            rows = self._parse_with_pdfplumber(file_path, result)

            # Fallback to camelot if pdfplumber yields few results
            if len(rows) < 3:
                logger.info("pdfplumber_low_yield", count=len(rows), file=str(file_path))
                camelot_rows = self._parse_with_camelot(file_path, result)
                if len(camelot_rows) > len(rows):
                    rows = camelot_rows
                    result.warnings.append("Used camelot fallback parser")

            result.rows = rows
            logger.info(
                "pdf_parse_complete",
                file=file_path.name,
                rows=len(rows),
                pages=result.total_pages,
            )
        except Exception as e:
            result.error = f"PDF parsing failed: {e!s}"
            logger.error("pdf_parse_error", file=str(file_path), error=str(e))

        return result

    def _parse_with_pdfplumber(self, file_path: Path, result: ParseResult) -> list[ParsedRow]:
        """Primary PDF parsing using pdfplumber."""
        import pdfplumber

        rows: list[ParsedRow] = []
        col_mapping: dict[str, int] | None = None
        order_idx = 0

        with pdfplumber.open(str(file_path)) as pdf:
            result.total_pages = len(pdf.pages)

            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    if not table:
                        continue

                    for row_data in table:
                        if not row_data or all(not cell for cell in row_data):
                            continue

                        # Try to detect header row
                        if col_mapping is None:
                            mapping = self._detect_header(row_data)
                            if mapping:
                                col_mapping = mapping
                                continue

                        # If we have a column mapping, extract data
                        if col_mapping:
                            parsed = self._extract_row(row_data, col_mapping, order_idx)
                            if parsed and parsed.description.strip():
                                rows.append(parsed)
                                order_idx += 1
                        else:
                            # Try heuristic extraction without header
                            parsed = self._heuristic_extract(row_data, order_idx)
                            if parsed and parsed.description.strip():
                                rows.append(parsed)
                                order_idx += 1

        return rows

    def _parse_with_camelot(self, file_path: Path, result: ParseResult) -> list[ParsedRow]:
        """Fallback PDF parsing using camelot."""
        try:
            import camelot
        except ImportError:
            result.warnings.append("Camelot not available for fallback")
            return []

        rows: list[ParsedRow] = []
        order_idx = 0

        try:
            tables = camelot.read_pdf(str(file_path), pages="all", flavor="lattice")

            if not tables or len(tables) == 0:
                tables = camelot.read_pdf(str(file_path), pages="all", flavor="stream")

            for table in tables:
                df = table.df

                # Try to find header row
                col_mapping = None
                for idx, row in df.iterrows():
                    mapping = self._detect_header(row.tolist())
                    if mapping:
                        col_mapping = mapping
                        continue

                    if col_mapping:
                        parsed = self._extract_row(row.tolist(), col_mapping, order_idx)
                        if parsed and parsed.description.strip():
                            rows.append(parsed)
                            order_idx += 1

        except Exception as e:
            result.warnings.append(f"Camelot fallback failed: {e!s}")

        return rows

    def _detect_header(self, row: list) -> dict[str, int] | None:
        """Detect if a row is a table header and return column mapping.

        Returns a dict like: {"item_number": 0, "description": 1, "quantity": 2, ...}
        """
        if not row:
            return None

        cells = [str(cell).strip().lower() if cell else "" for cell in row]
        mapping: dict[str, int] = {}
        matches = 0

        for idx, cell in enumerate(cells):
            if not cell:
                continue
            if re.search(r"s\.?\s*no|sr\.?\s*no|sl\.?\s*no", cell):
                mapping["serial"] = idx
                matches += 1
            elif re.search(r"item\s*no|item\s*number|dsr\s*no", cell):
                mapping["item_number"] = idx
                matches += 1
            elif re.search(r"description|particulars|item\s*of\s*work|specification", cell):
                mapping["description"] = idx
                matches += 1
            elif re.search(r"quant|qty", cell):
                mapping["quantity"] = idx
                matches += 1
            elif re.search(r"^unit$|unit\s*of", cell):
                mapping["unit"] = idx
                matches += 1
            elif re.search(r"^rate$|rate\s*per|rate\s*\(", cell):
                mapping["rate"] = idx
                matches += 1
            elif re.search(r"amount|total|value", cell):
                mapping["amount"] = idx
                matches += 1

        # Need at least description + 1 other column to be a valid header
        if "description" in mapping and matches >= 3:
            return mapping

        return None

    def _extract_row(
        self,
        row: list,
        mapping: dict[str, int],
        order_idx: int,
    ) -> ParsedRow | None:
        """Extract a ParsedRow using the detected column mapping."""
        if not row:
            return None

        def get_cell(key: str) -> str | None:
            idx = mapping.get(key)
            if idx is not None and idx < len(row):
                val = row[idx]
                return str(val).strip() if val else None
            return None

        description = get_cell("description") or ""
        if not description or len(description) < 2:
            return None

        # Detect depth from indentation or numbering
        depth = self._detect_depth(get_cell("serial"), get_cell("item_number"), description)

        return ParsedRow(
            order_index=order_idx,
            item_number=get_cell("item_number") or get_cell("serial"),
            description=description,
            quantity=ParsedRow.parse_decimal(get_cell("quantity")),
            unit=get_cell("unit"),
            rate=ParsedRow.parse_decimal(get_cell("rate")),
            amount=ParsedRow.parse_decimal(get_cell("amount")),
            depth=depth,
            raw_text=" | ".join(str(c) for c in row if c),
        )

    def _heuristic_extract(self, row: list, order_idx: int) -> ParsedRow | None:
        """Heuristic extraction when no header is detected.

        Assumes common BOQ format: [SNo, ItemNo, Description, Qty, Unit, Rate, Amount]
        """
        cells = [str(c).strip() if c else "" for c in row]
        cells = [c for c in cells if c]

        if len(cells) < 3:
            return None

        # Find the longest cell — likely the description
        desc_idx = max(range(len(cells)), key=lambda i: len(cells[i]))
        description = cells[desc_idx]

        if len(description) < 5:
            return None

        # Item number is typically before description
        item_number = cells[desc_idx - 1] if desc_idx > 0 else None

        # Numeric cells after description are likely qty, rate, amount
        numeric_cells = []
        for i in range(desc_idx + 1, len(cells)):
            val = ParsedRow.parse_decimal(cells[i])
            if val is not None:
                numeric_cells.append((i, val, cells[i]))

        quantity = numeric_cells[0][1] if len(numeric_cells) > 0 else None
        rate = numeric_cells[1][1] if len(numeric_cells) > 1 else None
        amount = numeric_cells[2][1] if len(numeric_cells) > 2 else None

        # Unit might be text between description and first number
        unit = None
        for i in range(desc_idx + 1, min(desc_idx + 3, len(cells))):
            if ParsedRow.parse_decimal(cells[i]) is None and len(cells[i]) < 15:
                unit = cells[i]
                break

        return ParsedRow(
            order_index=order_idx,
            item_number=item_number,
            description=description,
            quantity=quantity,
            unit=unit,
            rate=rate,
            amount=amount,
            depth=0,
            raw_text=" | ".join(cells),
        )

    def _detect_depth(
        self,
        serial: str | None,
        item_number: str | None,
        description: str,
    ) -> int:
        """Detect hierarchy depth from numbering patterns."""
        # Check item number dot depth: "5" = 0, "5.1" = 1, "5.1.2" = 2
        target = item_number or serial
        if target:
            parts = target.split(".")
            if len(parts) > 1 and all(p.strip().isdigit() for p in parts if p.strip()):
                return len(parts) - 1

        # Check leading whitespace in description
        stripped = description.lstrip()
        leading_spaces = len(description) - len(stripped)
        if leading_spaces > 4:
            return min(leading_spaces // 4, 3)

        return 0
