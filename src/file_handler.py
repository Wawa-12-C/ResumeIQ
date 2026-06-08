"""
File handling utilities for the Resume Analyzer.

Provides save, text extraction, and cleanup functionality
for uploaded resume files.
"""

import importlib
import logging
import os
from pathlib import Path

from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "txt"}
EXPECTED_MIME_TYPES = {
    ".pdf": {"application/pdf"},
    ".txt": {"text/plain"},
}


class FileHandler:
    """Handles file operations for uploaded resumes."""

    def __init__(self, upload_folder: str) -> None:
        """
        Initialize FileHandler.

        Args:
            upload_folder: Directory where uploaded files are stored.
        """
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def is_allowed(self, filename: str) -> bool:
        """
        Check if a filename has an allowed extension.

        Args:
            filename: The name of the file to check.

        Returns:
            True if the extension is allowed, False otherwise.
        """
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    def save(self, file_obj, filename: str) -> Path:
        """
        Save an uploaded file to the upload directory.

        Args:
            file_obj: The file object from Flask's request.files.
            filename: Filename to save as.

        Returns:
            Path to the saved file.
        """
        safe_filename = secure_filename(filename)
        if not safe_filename:
            raise ValueError("The uploaded file name is invalid.")

        filepath = self.upload_folder / safe_filename
        file_obj.save(filepath)
        logger.info("Saved uploaded file: %s", filepath)
        return filepath

    def extract_text(self, filepath: Path) -> str:
        """
        Extract plain text from a file.

        Supports .txt and .pdf extensions.

        Args:
            filepath: Path to the file.

        Returns:
            Extracted text as a string.

        Raises:
            ValueError: If the file type is unsupported.
        """
        self.validate_mime_type(filepath)
        suffix = filepath.suffix.lower()

        if suffix == ".txt":
            return self._read_txt(filepath)
        if suffix == ".pdf":
            return self._read_pdf(filepath)

        raise ValueError(f"Unsupported file type: {suffix}")

    def validate_mime_type(self, filepath: Path) -> None:
        """
        Verify the file's actual MIME type matches its extension.

        Args:
            filepath: Path to the file.

        Raises:
            ValueError: If the extension is unsupported or content mismatches it.
        """
        suffix = filepath.suffix.lower()
        expected_mime_types = EXPECTED_MIME_TYPES.get(suffix)
        if expected_mime_types is None:
            raise ValueError(f"Unsupported file type: {suffix}")

        try:
            magic = importlib.import_module("magic")
        except ImportError as exc:
            raise ValueError(
                "File type validation is unavailable. Please install python-magic."
            ) from exc

        detected_mime_type = magic.from_file(str(filepath), mime=True)
        if detected_mime_type not in expected_mime_types:
            expected = "PDF" if suffix == ".pdf" else "plain text"
            raise ValueError(
                f"The uploaded file content is not valid {expected}."
            )

    def cleanup(self, filepath: Path) -> None:
        """
        Delete a file from disk.

        Args:
            filepath: Path to the file to remove.
        """
        try:
            os.remove(filepath)
            logger.info("Cleaned up file: %s", filepath)
        except OSError as exc:
            logger.warning("Could not delete file %s: %s", filepath, exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_txt(filepath: Path) -> str:
        """Read a plain-text file with UTF-8 fallback to latin-1."""
        try:
            return filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return filepath.read_text(encoding="latin-1")

    @staticmethod
    def _read_pdf(filepath: Path) -> str:
        """Extract text from a PDF using PyMuPDF (fitz)."""
        try:
            fitz = importlib.import_module("fitz")

            text_parts: list[str] = []
            with fitz.open(str(filepath)) as doc:
                for page in doc:
                    text_parts.append(page.get_text())
            return "\n".join(text_parts)

        except ImportError:
            logger.warning("PyMuPDF not installed; falling back to pdfminer.")
            return FileHandler._read_pdf_pdfminer(filepath)

    @staticmethod
    def _read_pdf_pdfminer(filepath: Path) -> str:
        """Fallback PDF extraction using pdfminer.six."""
        try:
            pdfminer = importlib.import_module("pdfminer.high_level")
        except ImportError as exc:
            raise ImportError(
                "Neither PyMuPDF nor pdfminer.six is installed for PDF extraction."
            ) from exc

        pdfminer_extract = getattr(pdfminer, "extract_text")
        return pdfminer_extract(str(filepath))