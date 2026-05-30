"""AI-powered resume analysis service."""

from __future__ import annotations

import importlib
import json
import logging
import re
from typing import Any

try:
    from src.resume_analyzer import ResumeAnalysis, ResumeAnalyzer
except ModuleNotFoundError:
    from resume_analyzer import ResumeAnalysis, ResumeAnalyzer


logger = logging.getLogger(__name__)


class AIResumeAnalyzer:
    """Analyze resumes with an AI model, falling back to local rules."""

    def __init__(
        self,
        api_key: str,
        model: str,
        fallback_analyzer: ResumeAnalyzer | None = None,
    ) -> None:
        """Initialize the analyzer."""
        self.api_key = api_key
        self.model = model
        self.fallback_analyzer = fallback_analyzer or ResumeAnalyzer()

    def analyze(
        self,
        resume_text: str,
        job_description: str = "",
    ) -> ResumeAnalysis:
        """Return AI analysis when configured, otherwise local analysis."""
        if not self.api_key:
            analysis = self.fallback_analyzer.analyze(
                resume_text,
                job_description,
            )
            return self._with_source(analysis, "Rule-based fallback")

        try:
            data = self._request_ai_analysis(resume_text, job_description)
            return self._build_analysis(data, resume_text)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("AI analysis failed: %s", exc)
            analysis = self.fallback_analyzer.analyze(
                resume_text,
                job_description,
            )
            return self._with_source(analysis, "Rule-based fallback")

    def _request_ai_analysis(
        self,
        resume_text: str,
        job_description: str,
    ) -> dict[str, Any]:
        """Call the AI provider and parse its JSON response."""
        try:
            anthropic = importlib.import_module("anthropic")
        except ImportError as exc:
            raise RuntimeError(
                "The anthropic package is not installed."
            ) from exc

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=1200,
            temperature=0.2,
            system=(
                "You are a resume screening assistant. Analyze only the "
                "provided resume text and optional job description. Return "
                "strict JSON with no markdown."
            ),
            messages=[
                {
                    "role": "user",
                    "content": self._build_prompt(
                        resume_text,
                        job_description,
                    ),
                }
            ],
        )
        content = response.content[0].text
        return self._extract_json(content)

    @staticmethod
    def _build_prompt(resume_text: str, job_description: str) -> str:
        """Create the AI analysis prompt."""
        return f"""
Return JSON using exactly these keys:
score, job_match, summary, found_sections, missing_sections,
technical_skills, soft_skills, strengths, suggestions, ats_tips,
matched_keywords, missing_keywords.

Rules:
- score and job_match must be integers from 0 to 100.
- All list fields must be arrays of short strings.
- If the file is random text and not a resume, give a low score and explain it.
- Do not invent experience, skills, contact info, or education.

Resume text:
{resume_text[:7000]}

Target job description:
{job_description[:2000]}
""".strip()

    @staticmethod
    def _extract_json(content: str) -> dict[str, Any]:
        """Extract and parse JSON from an AI response."""
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("AI response did not contain JSON.")

        return json.loads(match.group(0))

    @staticmethod
    def _build_analysis(
        data: dict[str, Any],
        resume_text: str,
    ) -> ResumeAnalysis:
        """Convert AI JSON into the app's analysis dataclass."""
        word_count = len(re.findall(r"[a-zA-Z+#]+", resume_text))

        return ResumeAnalysis(
            score=AIResumeAnalyzer._clamp_score(data.get("score")),
            job_match=AIResumeAnalyzer._clamp_score(data.get("job_match")),
            word_count=word_count,
            found_sections=AIResumeAnalyzer._clean_list(
                data.get("found_sections")
            ),
            missing_sections=AIResumeAnalyzer._clean_list(
                data.get("missing_sections")
            ),
            technical_skills=AIResumeAnalyzer._clean_list(
                data.get("technical_skills")
            ),
            soft_skills=AIResumeAnalyzer._clean_list(data.get("soft_skills")),
            strengths=AIResumeAnalyzer._clean_list(data.get("strengths")),
            suggestions=AIResumeAnalyzer._clean_list(data.get("suggestions")),
            ats_tips=AIResumeAnalyzer._clean_list(data.get("ats_tips")),
            matched_keywords=AIResumeAnalyzer._clean_list(
                data.get("matched_keywords")
            ),
            missing_keywords=AIResumeAnalyzer._clean_list(
                data.get("missing_keywords")
            ),
            summary=str(data.get("summary", "AI analysis completed.")),
            source="AI analysis",
        )

    @staticmethod
    def _clamp_score(value: Any) -> int:
        """Convert a value to a 0-100 integer."""
        try:
            score = int(value)
        except (TypeError, ValueError):
            return 0

        return max(0, min(score, 100))

    @staticmethod
    def _clean_list(value: Any) -> list[str]:
        """Convert a JSON value into a safe list of short strings."""
        if not isinstance(value, list):
            return []

        return [str(item).strip()[:120] for item in value if str(item).strip()]

    @staticmethod
    def _with_source(
        analysis: ResumeAnalysis,
        source: str,
    ) -> ResumeAnalysis:
        """Return an existing analysis with a different source label."""
        return ResumeAnalysis(
            score=analysis.score,
            job_match=analysis.job_match,
            word_count=analysis.word_count,
            found_sections=analysis.found_sections,
            missing_sections=analysis.missing_sections,
            technical_skills=analysis.technical_skills,
            soft_skills=analysis.soft_skills,
            strengths=analysis.strengths,
            suggestions=analysis.suggestions,
            ats_tips=analysis.ats_tips,
            matched_keywords=analysis.matched_keywords,
            missing_keywords=analysis.missing_keywords,
            summary=analysis.summary,
            source=source,
        )
