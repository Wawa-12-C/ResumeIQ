"""Application configuration."""

import os


class Config:
    """Flask application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production",
    )
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"pdf", "txt"}
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get(
        "ANTHROPIC_MODEL",
        "claude-3-5-haiku-latest",
    )
