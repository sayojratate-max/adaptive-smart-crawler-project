import fitz  # PyMuPDF
import docx

from genai_processor import summarize, extract_keywords, classify_category
from database import insert_document


def extract_text_from_pdf(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()


def extract_text_from_docx(file_bytes):
    doc = docx.Document(file_bytes)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text.strip()


def extract_text_from_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore").strip()


def analyze_document(file_name: str, file_bytes: bytes, save_to_db: bool = True):
    """
    Extract text → summarize → keywords → category
    """
    if file_name.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif file_name.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    elif file_name.endswith(".txt"):
        text = extract_text_from_txt(file_bytes)
    else:
        raise ValueError("Unsupported file type")

    if not text:
        raise ValueError("No text extracted from document")

    text = text[:10000]  # limit huge docs

    summary = summarize(text)
    keywords = extract_keywords(text)
    category = classify_category(text)

    if save_to_db:
        insert_document(
            source=f"Uploaded File: {file_name}",
            title=file_name,
            raw_text=text,
            summary=summary,
            keywords=keywords,
            category=category
        )

    return {
        "text": text,
        "summary": summary,
        "keywords": keywords,
        "category": category
    }
