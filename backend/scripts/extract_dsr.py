"""
DSR Extraction Script

This script automatically parses a CPWD DSR PDF, extracts all valid items
(Item Number, Description, Unit), and inserts them into the Neon database.

Usage:
    export DATABASE_URL="postgresql+asyncpg://..."
    python scripts/extract_dsr.py /path/to/DSR-2021.pdf
"""

import sys
import re
import asyncio
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is not installed. Please run: pip install pdfplumber")
    sys.exit(1)

# Add parent directory to path for app imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.base import async_session_factory, init_db
from app.repositories.dsr_repository import DSRRepository
from app.models.dsr_item import DSRItem

# Regex to match DSR Item numbers (e.g., "1.1", "2.14.1", "12.2.1.3")
ITEM_REGEX = re.compile(r"^(\d+\.\d+(\.\d+)*)$")

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove excessive newlines and spaces
    return re.sub(r'\s+', ' ', text).strip()

def parse_pdf(pdf_path: str):
    items = []
    
    print(f"Opening PDF: {pdf_path} (This might take a moment...)")
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")
        
        current_item = None
        
        # We start from page 15 usually, to skip table of contents
        # You can adjust this range based on the actual PDF structure.
        for i in range(0, total_pages):
            page = pdf.pages[i]
            tables = page.extract_tables()
            
            for table in tables:
                for row in table:
                    # Clean the row
                    cleaned_row = [clean_text(cell) if cell else "" for cell in row]
                    
                    if len(cleaned_row) < 3:
                        continue
                        
                    # Usually: [Item No, Description, Unit, Rate]
                    col_0 = cleaned_row[0]
                    
                    if ITEM_REGEX.match(col_0):
                        # If we have an existing item, save it
                        if current_item and current_item["item_number"]:
                            items.append(current_item)
                            
                        # Start a new item
                        current_item = {
                            "item_number": col_0,
                            "chapter": f"Chapter {col_0.split('.')[0]}", # Estimate chapter from first digit
                            "official_description": cleaned_row[1],
                            "measurement_unit": cleaned_row[2] if len(cleaned_row) > 2 else "",
                            "simple_title": "",
                            "summary": "",
                            "purpose": "",
                            "where_used": [],
                            "materials": [],
                            "execution_steps": [],
                            "common_mistakes": [],
                            "specification_reference": "",
                            "search_keywords": []
                        }
                    elif current_item and col_0 == "" and cleaned_row[1] != "":
                        # Continuation of the previous item's description
                        current_item["official_description"] += " " + cleaned_row[1]
                        
                        # Sometimes unit is on the next line
                        if not current_item["measurement_unit"] and len(cleaned_row) > 2 and cleaned_row[2]:
                            current_item["measurement_unit"] = cleaned_row[2]

        # Append the very last item
        if current_item and current_item["item_number"]:
            items.append(current_item)

    print(f"Successfully extracted {len(items)} items from the PDF.")
    return items


async def seed_extracted_items(items):
    print("Connecting to database...")
    await init_db()

    async with async_session_factory() as session:
        repo = DSRRepository(session)
        created = 0
        updated = 0

        print("Injecting items into database...")
        for data in items:
            # We don't overwrite knowledge fields if they exist, only raw DSR data
            existing = await repo.get_by_item_number(data["item_number"])
            
            if existing:
                # Update only the raw fields
                update_data = {
                    "official_description": data["official_description"],
                    "measurement_unit": data["measurement_unit"]
                }
                await repo.update(existing, update_data)
                updated += 1
            else:
                item = DSRItem(**data)
                await repo.create(item)
                created += 1

            if (created + updated) % 100 == 0:
                print(f"  Processed {created + updated} items...")

        await session.commit()
    
    print(f"\nExtraction and injection complete!")
    print(f"Created: {created}")
    print(f"Updated: {updated}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_dsr.py <path_to_pdf>")
        sys.exit(1)
        
    pdf_file = sys.argv[1]
    
    if not Path(pdf_file).exists():
        print(f"Error: File '{pdf_file}' not found.")
        sys.exit(1)
        
    extracted_items = parse_pdf(pdf_file)
    
    if extracted_items:
        asyncio.run(seed_extracted_items(extracted_items))
    else:
        print("No items found. Ensure the PDF is a valid CPWD DSR.")
