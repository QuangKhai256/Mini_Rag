from pathlib import Path
from typing import List, Tuple

from docx import Document
from pypdf import PdfReader


PageText = List[Tuple[int, str]]


def load_pdf(path: Path) -> PageText:
    reader = PdfReader(str(path))
    return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]


def load_docx(path: Path) -> PageText:
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return [(1, "\n".join(paragraphs))]


def load_txt(path: Path) -> PageText:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [(1, text)]


def load_document(path: Path) -> PageText:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in {".docx", ".doc"}:
        return load_docx(path)
    if suffix == ".txt":
        return load_txt(path)
    raise ValueError(f"Unsupported file type: {suffix}")
