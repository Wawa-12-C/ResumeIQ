"""Tests for the ResumeIQ application."""

from io import BytesIO
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from src.app import app
from src.ai_analyzer import AIResumeAnalyzer
from src.resume_analyzer import ResumeAnalysis, ResumeAnalyzer


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

    def test_measurable_impact_detects_real_world_phrasings(self):
        """Measurable impact should catch common quantified achievements."""
        examples = (
            "Optimized API requests to run 3x faster.",
            "Reduced deployment time by 40%.",
            "Served 1,000 customers during launch.",
            "Improved accuracy 12%.",
        )

        for text in examples:
            with self.subTest(text=text):
                self.assertTrue(ResumeAnalyzer._has_measurable_impact(text))


class AIResumeAnalyzerTestCase(unittest.TestCase):
    """Unit tests for AI-backed resume analysis."""

    def test_successful_json_response_builds_analysis(self):
        """A valid AI JSON response should build a ResumeAnalysis."""
        response = SimpleNamespace(
            content=[
                SimpleNamespace(
                    text=(
                        '{"score": 88, "job_match": 75, '
                        '"summary": "Strong backend resume.", '
                        '"found_sections": ["Experience"], '
                        '"missing_sections": ["Education"], '
                        '"technical_skills": ["Python"], '
                        '"soft_skills": ["communication"], '
                        '"strengths": ["API impact"], '
                        '"suggestions": ["Add education"], '
                        '"ats_tips": ["Use standard headings"], '
                        '"matched_keywords": ["python"], '
                        '"missing_keywords": ["flask"]}'
                    )
                )
            ]
        )
        anthropic_module = ModuleType("anthropic")
        anthropic_module.Anthropic = MagicMock()

        with patch.dict("sys.modules", {"anthropic": anthropic_module}):
            with patch("anthropic.Anthropic") as anthropic_cls:
                anthropic_cls.return_value.messages.create.return_value = response
                result = AIResumeAnalyzer(
                    api_key="test-key",
                    model="claude-test",
                ).analyze("Experience: Python API", "Python Flask role")

        self.assertIsInstance(result, ResumeAnalysis)
        self.assertEqual(result.score, 88)
        self.assertEqual(result.job_match, 75)
        self.assertEqual(result.technical_skills, ("Python",))
        self.assertEqual(result.source, "AI analysis")
        anthropic_cls.assert_called_once_with(api_key="test-key")

    def test_malformed_ai_response_falls_back(self):
        """Bad AI scores should trigger rule-based fallback analysis."""
        response = SimpleNamespace(
            content=[
                SimpleNamespace(
                    text=(
                        '{"score": "not numeric", "job_match": 75, '
                        '"summary": "Bad score"}'
                    )
                )
            ]
        )
        anthropic_module = ModuleType("anthropic")
        anthropic_module.Anthropic = MagicMock()

        with patch.dict("sys.modules", {"anthropic": anthropic_module}):
            with patch("anthropic.Anthropic") as anthropic_cls:
                anthropic_cls.return_value.messages.create.return_value = response
                result = AIResumeAnalyzer(
                    api_key="test-key",
                    model="claude-test",
                ).analyze(
                    "Email: alex@example.com Projects: built Python Flask API.",
                    "Python Flask role",
                )

        self.assertEqual(result.source, "Rule-based fallback")
        self.assertNotEqual(result.score, 0)

    def test_missing_api_key_uses_fallback_directly(self):
        """No API key should skip the AI client and use fallback analysis."""
        fallback = MagicMock()
        fallback.analyze.return_value = ResumeAnalysis(
            score=61,
            job_match=55,
            word_count=10,
            found_sections=("Projects",),
            missing_sections=("Education",),
            technical_skills=("python",),
            soft_skills=(),
            strengths=("python",),
            suggestions=("Add education.",),
            ats_tips=("Avoid tables.",),
            matched_keywords=("python",),
            missing_keywords=("flask",),
            summary="Fallback summary.",
        )

        result = AIResumeAnalyzer(
            api_key="",
            model="claude-test",
            fallback_analyzer=fallback,
        ).analyze("Projects: Python", "Python Flask role")

        fallback.analyze.assert_called_once_with(
            "Projects: Python",
            "Python Flask role",
        )
        self.assertEqual(result.source, "Rule-based fallback")


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

    @patch("src.file_handler.FileHandler.validate_mime_type")
    def test_txt_resume_upload_returns_analysis(self, _validate_mime_type):
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

    @patch("src.file_handler.FileHandler.validate_mime_type")
    def test_random_txt_upload_does_not_show_sample_skills(self, _validate_mime_type):
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

    def test_upload_larger_than_max_content_length_returns_413(self):
        """Oversized uploads should return the Flask 413 error page."""
        data = {
            "resume": (
                BytesIO(b"x" * (app.config["MAX_CONTENT_LENGTH"] + 1)),
                "large.txt",
            ),
            "job_description": "Python Flask SQL Git intern role",
        }

        response = self.client.post(
            "/",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 413)
        self.assertIn(b"too large", response.data.lower())


if __name__ == "__main__":
    unittest.main()
