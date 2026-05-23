"""
Resume Analyzer Web Application
"""

import logging
import sys
from pathlib import Path

from flask import Flask, render_template

# Make sure Python can find the src/ package when running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── Create the Flask app ──────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent.parent / "templates"),
    static_folder=str(Path(__file__).parent.parent / "static"),
)
app.config.from_object(Config)   # load settings from config.py

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")   # swap to "Hello World" if no HTML yet


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)