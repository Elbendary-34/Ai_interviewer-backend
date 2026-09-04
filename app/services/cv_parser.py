import os
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(file_path: str) -> str:
    """Extract text from files such as PDF and DOCX."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    if ext == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif ext in [".docx", ".doc"]:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return text.strip()