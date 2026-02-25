"""PDF parsing service."""
import io

from pypdf import PdfReader


class PdfParser:
    """Extract text from PDF files."""

    @staticmethod
    def extract_text(content: bytes) -> str:
        """Extract raw text from PDF bytes."""
        pdf_stream = io.BytesIO(content)
        reader = PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
