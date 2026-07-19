"""
tools/pdf_reader_tool.py

A minimal, single-responsibility CrewAI tool that extracts raw text
from a PDF file on disk. It does NOT summarize, chunk, embed, clean,
or OCR the text - that is deliberately left to other parts of the crew.
"""

from pathlib import Path
from pypdf import PdfReader
from crewai.tools import tool

def extract_pdf_text(file_path: str) -> str:          # ADD: plain function, no LLM/tool overhead
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found at '{file_path}'."
    if path.suffix.lower() != ".pdf":
        return f"Error: '{file_path}' is not a PDF file."
    try:
        reader = PdfReader(path)
    except Exception as e:
        return f"Error: Could not open PDF. Reason: {e}"

    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    if not text_parts:
        return "Error: No extractable text found in this PDF (it may be scanned or image-based)."
    return "\n".join(text_parts)

@tool("PDF Reader Tool")
def read_pdf(file_path: str) -> str:
    """
    Extract and return the raw text content of a PDF file.

    Args:
        file_path: Path to the PDF file to read (relative or absolute).

    Returns:
        The extracted text as a single string, with each page's text
        separated by a newline. If the PDF cannot be read or contains
        no extractable text, a short human-readable error string is
        returned instead (never raises, so the agent can react to it).
    """
    return extract_pdf_text(file_path)