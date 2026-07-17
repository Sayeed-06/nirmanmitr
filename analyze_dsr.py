#!/usr/bin/env python3
"""Analyze DSR PDF structure for NirmanMitr parser development."""
import pdfplumber
import re
import os

DSR_DIR = "/Users/sayeed/Documents/nirmanmitr"

def analyze_pdf(filepath):
    """Extract and analyze the structure of a DSR PDF."""
    filename = os.path.basename(filepath)
    print(f"\n{'='*60}")
    print(f"FILE: {filename}")
    print(f"{'='*60}")
    
    pdf = pdfplumber.open(filepath)
    print(f"Total pages: {len(pdf.pages)}")
    
    # Sample first 10 pages
    for i in range(min(10, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text()
        if text:
            lines = text.strip().split('\n')
            print(f"\n--- Page {i+1} (first 30 lines) ---")
            for line in lines[:30]:
                print(line)
            
            # Look for DSR item number patterns
            dsr_patterns = re.findall(
                r'(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)', text
            )
            if dsr_patterns:
                unique = list(set(dsr_patterns))[:10]
                print(f"\n  DSR-like numbers found: {unique}")
        
        # Check for tables
        tables = page.extract_tables()
        if tables:
            print(f"  Tables on page {i+1}: {len(tables)}")
            for t_idx, table in enumerate(tables[:2]):
                if table:
                    print(f"    Table {t_idx}: {len(table)} rows")
                    for row in table[:3]:
                        print(f"      {row}")
    
    pdf.close()

# Analyze all PDFs
for f in os.listdir(DSR_DIR):
    if f.endswith('.pdf'):
        analyze_pdf(os.path.join(DSR_DIR, f))
