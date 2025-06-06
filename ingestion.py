from PyPDF2 import PdfReader
import re

def extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def clean_transcript(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()
