import os
from pypdf import PdfReader
from docx import Document


def extract_text(path):
    """Returns list of {"page": number, "text": "..."}"""
    ext = os.path.splitext(path)[1].lower()
    pages = []

    if ext == ".pdf":
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page": i, "text": text})

    elif ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            pages.append({"page": 1, "text": f.read()})

    elif ext == ".docx":
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        pages.append({"page": 1, "text": text})

    return pages