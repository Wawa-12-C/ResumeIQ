"""Rule-based resume analysis logic.

The analyzer is intentionally deterministic so it can run in class demos
without requiring an external AI service or API key.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


TECHNICAL_SKILLS = {
    "python",
    "c",
    "c++",
    "java",
    "javascript",
    "html",
    "css",
    "flask",
    "django",
    "sql",
    "mysql",
    "git",
    "linux",
    "docker",
    "machine learning",
    "data analysis",
    "pandas",
    "numpy",
    "api",
}

SOFT_SKILLS = {
    "communication",
    "teamwork",
    "leadership",
    "problem solving",
    "collaboration",
    "presentation",
    "time management",
}

SECTION_KEYWORDS = {
    "education": ("education", "university", "college", "degree"),
    "experience": ("experience", "internship", "work", "employment"),
    "projects": ("projects", "project"),
    "skills": ("skills", "technologies", "tools"),
    "contact": ("email", "phone", "github", "linkedin"),
}

ACTION_VERBS = {
    "built",
    "created",
    "designed",
    "developed",
    "implemented",
    "improved",
    "led",
    "managed",
    "optimized",
    "tested",
}


@dataclass(frozen=True)
class ResumeAnalysis:
    """Structured result returned by the analyzer."""

    score: int
    word_count: int
    found_sections: list[str]
    missing_sections: list[str]
    technical_skills: list[str]
    soft_skills: list[str]
    suggestions: list[str]
    summary: str


class ResumeAnalyzer:
    """Analyze resume text and return practical improvement feedback."""

    def analyze(self, text: str) -> ResumeAnalysis:
        """Analyze resume text."""
        normalized_text = self._normalize(text)
        if not normalized_text:
            raise ValueError(
                "The uploaded file does not contain readable text."
            )

        words = re.findall(r"[a-zA-Z+#]+", normalized_text)
        word_count = len(words)
        found_sections, missing_sections = self._find_sections(normalized_text)
        technical_skills = self._find_terms(normalized_text, TECHNICAL_SKILLS)
        soft_skills = self._find_terms(normalized_text, SOFT_SKILLS)
        suggestions = self._build_suggestions(
            normalized_text,
            word_count,
            missing_sections,
            technical_skills,
            soft_skills,
        )
        score = self._calculate_score(
            normalized_text,
            word_count,
            found_sections,
            technical_skills,
            soft_skills,
        )
        summary = self._build_summary(
            score,
            technical_skills,
            missing_sections,
        )

        return ResumeAnalysis(
            score=score,
            word_count=word_count,
            found_sections=found_sections,
            missing_sections=missing_sections,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            suggestions=suggestions,
            summary=summary,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """Convert text to a compact lowercase representation."""
        return " ".join(text.lower().split())

    @staticmethod
    def _find_terms(text: str, terms: set[str]) -> list[str]:
        """Return matching terms sorted alphabetically."""
        matches = []
        for term in terms:
            pattern = rf"(?<![a-zA-Z]){re.escape(term)}(?![a-zA-Z])"
            if re.search(pattern, text):
                matches.append(term)
        return sorted(matches)

    @staticmethod
    def _find_sections(text: str) -> tuple[list[str], list[str]]:
        """Detect expected resume sections."""
        found = []
        missing = []

        for section, keywords in SECTION_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                found.append(section.title())
            else:
                missing.append(section.title())

        return found, missing

    def _calculate_score(
        self,
        text: str,
        word_count: int,
        found_sections: list[str],
        technical_skills: list[str],
        soft_skills: list[str],
    ) -> int:
        """Calculate a resume quality score from 0 to 100."""
        score = 20
        score += min(len(found_sections) * 10, 40)
        score += min(len(technical_skills) * 4, 24)
        score += min(len(soft_skills) * 3, 9)

        if self._has_email(text):
            score += 5
        if self._has_phone(text):
            score += 5
        if 120 <= word_count <= 800:
            score += 8
        if self._has_action_verbs(text):
            score += 9

        return min(score, 100)

    def _build_suggestions(
        self,
        text: str,
        word_count: int,
        missing_sections: list[str],
        technical_skills: list[str],
        soft_skills: list[str],
    ) -> list[str]:
        """Create concrete suggestions based on missing resume signals."""
        suggestions = []

        if missing_sections:
            missing = ", ".join(missing_sections)
            suggestions.append(f"Add or clarify these sections: {missing}.")
        if not self._has_email(text):
            suggestions.append("Add a professional email address.")
        if not self._has_phone(text):
            suggestions.append("Add a phone number for recruiter contact.")
        if len(technical_skills) < 4:
            suggestions.append(
                "List more role-related technical skills, tools, or languages."
            )
        if not soft_skills:
            suggestions.append(
                "Mention teamwork, communication, or leadership with evidence."
            )
        if word_count < 120:
            suggestions.append(
                "Add more detail about projects and achievements."
            )
        elif word_count > 800:
            suggestions.append(
                "Shorten the resume so the key points are easier to scan."
            )
        if not self._has_action_verbs(text):
            suggestions.append(
                "Start achievement bullets with action verbs like built or "
                "improved."
            )
        impact_pattern = r"\d+%|\d+\s*(users|members|seconds|hours|projects)"
        if not re.search(impact_pattern, text):
            suggestions.append(
                "Use numbers to show impact, such as users or results."
            )

        if not suggestions:
            suggestions.append(
                "Great foundation. Tailor keywords to each job posting."
            )

        return suggestions

    @staticmethod
    def _build_summary(
        score: int,
        technical_skills: list[str],
        missing_sections: list[str],
    ) -> str:
        """Build a short human-readable summary."""
        if score >= 80:
            quality = "strong"
        elif score >= 60:
            quality = "developing"
        else:
            quality = "early-stage"

        skill_text = (
            ", ".join(technical_skills[:5])
            or "few clear technical skills"
        )
        if missing_sections:
            missing_text = f" Missing: {', '.join(missing_sections)}."
        else:
            missing_text = " Core sections are present."

        return f"This is a {quality} resume with {skill_text}.{missing_text}"

    @staticmethod
    def _has_email(text: str) -> bool:
        """Return True when text contains an email-like contact."""
        return bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))

    @staticmethod
    def _has_phone(text: str) -> bool:
        """Return True when text contains a phone-like contact."""
        return bool(re.search(r"(\+?\d[\d\s().-]{7,}\d)", text))

    @staticmethod
    def _has_action_verbs(text: str) -> bool:
        """Return True when the resume uses action-oriented verbs."""
        return any(verb in text for verb in ACTION_VERBS)
