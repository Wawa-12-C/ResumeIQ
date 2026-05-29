"""Tests for the ResumeIQ application."""

from io import BytesIO
import unittest

from src.app import app
from src.resume_analyzer import ResumeAnalyzer


class ResumeAnalyzerTestCase(unittest.TestCase):
    """Unit tests for rule-based resume analysis."""

    def test_analyzer_detects_sections_and_skills(self):
        """Analyzer should detect common resume signals."""
        text = """
        Email: alex@example.com
        Phone: 123-456-7890
        Education: UESTC Software Engineering
        Experience: built a Flask API used by 120 users.
        Projects: developed a Python resume analyzer with SQL and Git.
        Skills: Python, Flask, SQL, Git, communication, teamwork.
        """

        result = ResumeAnalyzer().analyze(text)

        self.assertGreaterEqual(result.score, 80)
        self.assertIn("Education", result.found_sections)
        self.assertIn("python", result.technical_skills)
        self.assertIn("teamwork", result.soft_skills)

    def test_analyzer_rejects_empty_text(self):
        """Empty extracted text should raise a clear validation error."""
        with self.assertRaises(ValueError):
            ResumeAnalyzer().analyze("   ")


class FlaskAppTestCase(unittest.TestCase):
    """Integration tests for the Flask upload workflow."""

    def setUp(self):
        """Create a test client."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_loads(self):
        """Home page should render the upload form."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Analyze a Resume", response.data)

    def test_txt_resume_upload_returns_analysis(self):
        """Uploading a TXT resume should produce an analysis result."""
        resume_text = (
            "Email: alex@example.com\n"
            "Phone: 123-456-7890\n"
            "Education: UESTC Software Engineering\n"
            "Experience: built a Flask API for 120 users.\n"
            "Projects: Python resume analyzer\n"
            "Skills: Python, Flask, SQL, Git, communication, teamwork\n"
        )
        data = {
            "resume": (
                BytesIO(resume_text.encode("utf-8")),
                "resume.txt",
            )
        }

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Score", response.data)
        self.assertIn(b"Technical Skills", response.data)

    def test_invalid_file_type_shows_error(self):
        """Uploading an unsupported file type should show an error."""
        data = {"resume": (BytesIO(b"not a resume"), "resume.docx")}

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unsupported file type", response.data)


if __name__ == "__main__":
    unittest.main()
