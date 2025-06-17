# pdf_reader.py

import fitz  # PyMuPDF: used to read and extract text from PDFs
from typing import List, Tuple
from fallback_sector_detection import detect_sectors  # Custom logic for sector detection

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and returns all text from a PDF file using PyMuPDF.
    """
    doc = fitz.open(pdf_path)  # Open the PDF file
    full_text = ""
    for page in doc:
        full_text += page.get_text()  # Extract text from each page
    doc.close()  # Close the document to free resources
    return full_text.strip()  # Return the cleaned, concatenated text


def detect_sectors_from_pdf(pdf_path: str, max_results: int = 3) -> Tuple[List[str], str]:
    """
    Extracts text from a PDF and detects relevant business sectors using fallback logic.
    Returns:
        - A list of detected sector strings (limited to max_results)
        - The full raw extracted text from the PDF
    """
    text = extract_text_from_pdf(pdf_path)  # Step 1: Extract raw text from PDF
    sectors = detect_sectors(text, max_results=max_results)  # Step 2: Detect top sectors
    return sectors, text  # Return both sector list and raw text


# === CLI test block === 
if __name__ == "__main__":
    test_path = "samples/sample_pitchdeck.pdf"  # Path to the PDF used for testing
    sectors, raw_text = detect_sectors_from_pdf(test_path)

    print("Detected Sectors:", sectors)  # Output the list of detected sectors

    print("\n--- Extracted Text Preview ---\n")
    print(raw_text[:1500], "...")  # Preview the first 1500 characters of text
