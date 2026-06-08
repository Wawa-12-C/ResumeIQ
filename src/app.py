"""Resume Analyzer Web Application."""

import logging
from pathlib import Path

from flask import Flask, flash, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

try:
    from src.ai_analyzer import AIResumeAnalyzer
    from src.config import Config
    from src.file_handler import FileHandler
    from src.resume_analyzer import ResumeAnalyzer
except ModuleNotFoundError:
    from ai_analyzer import AIResumeAnalyzer
    from config import Config
    from file_handler import FileHandler
    from resume_analyzer import ResumeAnalyzer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent.parent / "templates"),
    static_folder=str(Path(__file__).parent.parent / "static"),
)
app.config.from_object(Config)
file_handler = FileHandler(app.config["UPLOAD_FOLDER"])
resume_analyzer = AIResumeAnalyzer(
    api_key=app.config["ANTHROPIC_API_KEY"],
    model=app.config["ANTHROPIC_MODEL"],
    fallback_analyzer=ResumeAnalyzer(),
)


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the main page and handle resume uploads."""
    analysis = None

    if request.method == "POST":
        analysis = analyze_uploaded_resume()

    return render_template("index.html", analysis=analysis)


def analyze_uploaded_resume():
    """Validate, save, analyze, and clean up an uploaded resume."""
    uploaded_file = request.files.get("resume")
    if not uploaded_file or uploaded_file.filename == "":
        flash("Please choose a PDF or TXT resume file.")
        return None

    job_description = request.form.get("job_description", "").strip()
    if not job_description:
        flash("Please paste the job description before analyzing.")
        return None

    original_filename = uploaded_file.filename
    if not file_handler.is_allowed(original_filename):
        flash("Unsupported file type. Please upload a PDF or TXT file.")
        return None

    saved_path = None
    try:
        saved_path = file_handler.save(uploaded_file, original_filename)
        text = file_handler.extract_text(saved_path)
        return resume_analyzer.analyze(text, job_description)
    except ValueError as exc:
        flash(str(exc))
        logger.info("Resume validation failed: %s", exc)
    except Exception as exc:  # pylint: disable=broad-except
        flash("Could not analyze this file. Please try another resume.")
        logger.exception("Unexpected resume analysis error: %s", exc)
    finally:
        if saved_path is not None:
            file_handler.cleanup(saved_path)

    return None


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_error):
    """Handle uploads that exceed the configured size limit."""
    flash("The file is too large. Please upload a file smaller than 5 MB.")
    return render_template("index.html", analysis=None), 413


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
