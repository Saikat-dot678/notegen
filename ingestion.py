import re
from pdfminer.high_level import extract_text
import pytesseract
from pdf2image import convert_from_path

def load_transcript(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def clean_transcript(raw: str) -> str:
    return re.sub(r"\[\d{2}:\d{2}:\d{2}\]", "", raw)

def extract_pdf_text(path: str) -> str:
    text = extract_text(path)
    if len(text.strip()) > 100:
        return text
    # OCR fallback
    pages = convert_from_path(path, dpi=300)
    return "\n".join(pytesseract.image_to_string(p) for p in pages)
