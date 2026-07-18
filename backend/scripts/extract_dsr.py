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

import pdfplumber

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
        current_desc_lines = []
        
        for i in range(0, total_pages):
            page = pdf.pages[i]
            text = page.extract_text()
            if not text:
                continue
                
            for line in text.split('\n'):
                line = clean_text(line)
                if not line:
                    continue
                
                # Match "1.1", "2.14.1", etc. followed by space and text
                match = re.match(r"^(\d+\.\d+(?:\.\d+)*)\s+(.*)", line)
                
                if match:
                    # Save previous item
                    if current_item:
                        current_item["official_description"] = " ".join(current_desc_lines)
                        items.append(current_item)
                    
                    item_no = match.group(1)
                    rest_of_line = match.group(2)
                    
                    current_item = {
                        "item_number": item_no,
                        "chapter": f"Chapter {item_no.split('.')[0]}",
                        "official_description": "", # Will be joined at the end
                        "measurement_unit": "", 
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
                    current_desc_lines = [rest_of_line]
                
                elif current_item:
                    # Not a new item, so it's a continuation of the current item's description
                    # It might include the Unit and Rate at the end, but we will just bundle it all in description
                    # so that it is fully searchable.
                    current_desc_lines.append(line)

        # Append the very last item
        if current_item:
            current_item["official_description"] = " ".join(current_desc_lines)
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
