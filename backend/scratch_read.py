import pdfplumber
import sys

def read_text():
    print("Reading text from page 30...")
    with pdfplumber.open("../DSR-2021.pdf") as pdf:
        text = pdf.pages[30].extract_text()
        print("\n--- EXTRACTED TEXT ---")
        print(text[:2000])
        print("----------------------\n")

if __name__ == "__main__":
    read_text()
