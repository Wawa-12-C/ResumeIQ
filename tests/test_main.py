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

    def test_job_match_uses_keyword_aliases(self):
        """Job matching should understand common equivalent phrases."""
        resume_text = """
        Projects: built a Python Flask web application with SQL.
        Used Git for version control and wrote pytest unit tests.
        """
        job_description = """
        Looking for RESTful API experience, database knowledge, testing,
        Git, Python, Flask, and web applications.
        """

        result = ResumeAnalyzer().analyze(resume_text, job_description)

        self.assertIn("database", result.matched_keywords)
        self.assertIn("testing", result.matched_keywords)
        self.assertIn("web development", result.matched_keywords)
        self.assertIn("rest api", result.missing_keywords)
        self.assertLess(result.job_match, 100)

    def test_ats_tips_follow_resume_content(self):
        """ATS tips should change based on uploaded resume content."""
        random_result = ResumeAnalyzer().analyze(
            "banana chair moon table unrelated random words"
        )
        detailed_result = ResumeAnalyzer().analyze(
            """
            Email: alex@example.com
            Phone: 123-456-7890
            Education: UESTC Software Engineering
            Projects: Built a Python Flask API with SQL and Git.
            Skills: Python, Flask, SQL, Git, teamwork.
            """
        )

        self.assertNotEqual(random_result.ats_tips, detailed_result.ats_tips)
        self.assertIn("selectable text", random_result.ats_tips[1])


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
            ),
            "job_description": "Python Flask SQL Git intern role",
        }

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Score", response.data)
        self.assertIn(b"Technical Skills", response.data)

    def test_random_txt_upload_does_not_show_sample_skills(self):
        """Random text should not display sample resume skill data."""
        data = {
            "resume": (
                BytesIO(b"banana chair moon table unrelated random words"),
                "random.txt",
            ),
            "job_description": "Python Flask SQL Git intern role",
        }

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No technical skills detected", response.data)
        self.assertNotIn(b"<li>Python</li>", response.data)

    def test_invalid_file_type_shows_error(self):
        """Uploading an unsupported file type should show an error."""
        data = {
            "resume": (BytesIO(b"not a resume"), "resume.docx"),
            "job_description": "Python Flask SQL Git intern role",
        }

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unsupported file type", response.data)

    def test_missing_job_description_shows_error(self):
        """Job description is required for matching."""
        data = {"resume": (BytesIO(b"Python Flask resume"), "resume.txt")}

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please paste the job description", response.data)


if __name__ == "__main__":
    unittest.main()
