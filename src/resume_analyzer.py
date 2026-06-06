"""Resume analysis models and rule-based fallback logic."""

from __future__ import annotations

import re
from dataclasses import dataclass


TECHNICAL_SKILLS = {
    "agile",
    "algorithms",
    "api",
    "aws",
    "python",
    "c",
    "c++",
    "ci/cd",
    "cloud",
    "data structures",
    "database",
    "deployment",
    "debugging",
    "java",
    "javascript",
    "html",
    "css",
    "flask",
    "django",
    "gcp",
    "sql",
    "mysql",
    "git",
    "linux",
    "docker",
    "machine learning",
    "data analysis",
    "oop",
    "pandas",
    "numpy",
    "rest api",
    "testing",
    "unit testing",
    "web development",
    "typescript",
    "react",
    "node.js",
    "mongodb",
    "redis",
    "kubernetes",
    "terraform",
    "fastapi",
    "spring boot",
    "postgresql",
    "graphql",
    "bash",
    "pytorch",
    "tensorflow",
    "excel",
    "figma",
    "opencv",
}

SOFT_SKILLS = {
    "communication",
    "teamwork",
    "leadership",
    "problem solving",
    "collaboration",
    "presentation",
    "time management",
    "critical thinking",
    "adaptability",
    "attention to detail",
    "project management",
    "mentoring",
    "creativity",
}

SECTION_KEYWORDS = {
    "education": ("education", "university", "college", "degree"),
    "experience": ("experience", "internship", "work", "employment"),
    "projects": ("projects", "project"),
    "skills": ("skills", "technologies", "tools"),
    "contact": ("email", "phone", "github", "linkedin"),
}

KEYWORD_ALIASES = {
    "api": ("api", "apis"),
    "aws": ("aws", "amazon web services"),
    "ci/cd": ("ci/cd", "continuous integration", "continuous deployment"),
    "cloud": ("cloud", "cloud platform", "cloud platforms"),
    "communication": ("communication", "communicate", "explain clearly"),
    "css": ("css", "stylesheet", "stylesheets"),
    "data structures": ("data structures", "data structure"),
    "database": ("database", "databases", "db", "mysql", "postgresql", "sql"),
    "deployment": ("deployment", "deploy", "deployed", "production"),
    "docker": ("docker", "container", "containers"),
    "flask": ("flask",),
    "gcp": ("gcp", "google cloud"),
    "git": ("git", "github", "version control"),
    "html": ("html",),
    "javascript": ("javascript", "js"),
    "linux": ("linux", "unix"),
    "oop": ("oop", "object oriented", "object-oriented"),
    "problem solving": ("problem solving", "problem-solving"),
    "python": ("python",),
    "rest api": ("rest api", "rest apis", "restful", "restful api"),
    "sql": ("sql", "mysql", "postgresql", "sqlite"),
    "teamwork": ("teamwork", "team work", "collaboration", "collaborate"),
    "testing": ("testing", "test", "tests", "tested"),
    "unit testing": ("unit testing", "unit tests", "unittest", "pytest"),
    "web development": ("web application", "web applications", "web app"),
    "typescript": ("typescript", "ts"),
    "react": ("react", "react.js", "reactjs"),
    "node.js": ("node.js", "nodejs", "node"),
    "mongodb": ("mongodb", "mongo"),
    "redis": ("redis",),
    "kubernetes": ("kubernetes", "k8s"),
    "terraform": ("terraform",),
    "fastapi": ("fastapi", "fast api"),
    "spring boot": ("spring boot", "springboot"),
    "postgresql": ("postgresql", "postgres", "postgre sql"),
    "graphql": ("graphql", "graph ql"),
    "bash": ("bash", "shell scripting", "shell script"),
    "pytorch": ("pytorch", "torch"),
    "tensorflow": ("tensorflow", "tf"),
    "excel": ("excel", "microsoft excel", "spreadsheets"),
    "figma": ("figma",),
    "opencv": ("opencv", "open cv"),
    "critical thinking": ("critical thinking", "analytical thinking"),
    "adaptability": ("adaptability", "adaptable"),
    "attention to detail": ("attention to detail", "detail-oriented"),
    "project management": ("project management", "project planning"),
    "mentoring": ("mentoring", "mentor", "mentored"),
    "creativity": ("creativity", "creative"),
}

COMPILED_PATTERNS = {
    keyword: re.compile(
        "|".join(
            rf"(?<![a-zA-Z0-9]){re.escape(alias)}(?![a-zA-Z0-9])"
            for alias in KEYWORD_ALIASES.get(keyword, (keyword,))
        ),
        re.IGNORECASE,
    )
    for keyword in TECHNICAL_SKILLS | SOFT_SKILLS
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
    job_match: int
    word_count: int
    found_sections: list[str]
    missing_sections: list[str]
    technical_skills: list[str]
    soft_skills: list[str]
    strengths: list[str]
    suggestions: list[str]
    ats_tips: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    summary: str
    source: str = "Rule-based fallback"


class ResumeAnalyzer:
    """Analyze resume text and return practical improvement feedback."""

    def analyze(
        self,
        text: str,
        job_description: str = "",
    ) -> ResumeAnalysis:
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
        matched_keywords, missing_keywords = self._compare_job_keywords(
            normalized_text,
            self._normalize(job_description),
        )
        suggestions = self._build_suggestions(
            normalized_text,
            word_count,
            missing_sections,
            technical_skills,
            soft_skills,
            missing_keywords,
        )
        strengths = self._build_strengths(
            word_count,
            found_sections,
            technical_skills,
            soft_skills,
            matched_keywords,
        )
        score = self._calculate_score(
            normalized_text,
            word_count,
            found_sections,
            technical_skills,
            soft_skills,
        )
        job_match = self._calculate_job_match(
            normalized_text,
            self._normalize(job_description),
            score,
        )
        summary = self._build_summary(
            score,
            technical_skills,
            missing_sections,
        )

        return ResumeAnalysis(
            score=score,
            job_match=job_match,
            word_count=word_count,
            found_sections=found_sections,
            missing_sections=missing_sections,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            strengths=strengths,
            suggestions=suggestions,
            ats_tips=self._build_ats_tips(
                normalized_text,
                word_count,
                missing_sections,
                technical_skills,
                missing_keywords,
            ),
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
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
            if ResumeAnalyzer._contains_keyword(text, term):
                matches.append(term)
        return sorted(matches)

    @staticmethod
    def _contains_keyword(text: str, keyword: str) -> bool:
        """Return True when text contains a keyword or known alias."""
        pattern = COMPILED_PATTERNS.get(keyword)
        if pattern is None:
            pattern = re.compile(
                rf"(?<![a-zA-Z0-9]){re.escape(keyword)}(?![a-zA-Z0-9])",
                re.IGNORECASE,
            )

        return bool(pattern.search(text))

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
        score = 0
        score += min(len(found_sections) * 8, 32)
        score += min(len(technical_skills) * 5, 25)
        score += min(len(soft_skills) * 3, 12)

        if self._has_email(text):
            score += 8
        if self._has_phone(text):
            score += 5
        if 150 <= word_count <= 700:
            score += 8
        if self._has_action_verbs(text):
            score += 10
        if self._has_measurable_impact(text):
            score += 8

        return min(score, 100)

    def _calculate_job_match(
        self,
        resume_text: str,
        job_description: str,
        resume_score: int,
    ) -> int:
        """Calculate how closely a resume matches the target job."""
        if not job_description:
            return resume_score

        total_weight = 0
        matched_weight = 0
        for keyword in TECHNICAL_SKILLS | SOFT_SKILLS:
            pattern = COMPILED_PATTERNS[keyword]
            weight = len(pattern.findall(job_description))
            if weight == 0:
                continue

            total_weight += weight
            if pattern.search(resume_text):
                matched_weight += weight

        if total_weight == 0:
            return resume_score

        keyword_score = (matched_weight / total_weight) * 100
        return round((keyword_score * 0.7) + (resume_score * 0.3))

    def _build_suggestions(
        self,
        text: str,
        word_count: int,
        missing_sections: list[str],
        technical_skills: list[str],
        soft_skills: list[str],
        missing_keywords: list[str],
    ) -> list[str]:
        """Create concrete suggestions based on missing resume signals."""
        suggestions = []

        if missing_sections:
            missing = ", ".join(missing_sections)
            suggestions.append(
                f"Strengthen your resume content with these sections: {missing}."
            )
        if not self._has_email(text):
            suggestions.append("Add recruiter contact details near your name.")
        if not self._has_phone(text):
            suggestions.append("Include a phone number for interview follow-up.")
        if len(technical_skills) < 4:
            suggestions.append(
                "Show more role-related technologies through projects."
            )
        if missing_keywords:
            keywords = ", ".join(missing_keywords[:4])
            suggestions.append(
                f"Add evidence for job requirements such as {keywords}."
            )
        if not soft_skills:
            suggestions.append(
                "Describe teamwork or communication with a concrete example."
            )
        if word_count < 120:
            suggestions.append(
                "Add more project detail, responsibilities, and outcomes."
            )
        elif word_count > 800:
            suggestions.append(
                "Shorten older or less relevant details to improve focus."
            )
        if not self._has_action_verbs(text):
            suggestions.append(
                "Rewrite bullets with stronger action verbs and ownership."
            )
        if not self._has_measurable_impact(text):
            suggestions.append(
                "Add measurable impact, such as users, time saved, or accuracy."
            )

        if not suggestions:
            suggestions.append(
                "Great foundation. Add one tailored achievement for this role."
            )

        return suggestions

    @staticmethod
    def _build_strengths(
        word_count: int,
        found_sections: list[str],
        technical_skills: list[str],
        soft_skills: list[str],
        matched_keywords: list[str],
    ) -> list[str]:
        """Create short strength labels for the results UI."""
        strengths = []

        if found_sections:
            strengths.append(f"{len(found_sections)} key sections found")
        if technical_skills:
            strengths.extend(technical_skills[:3])
        if soft_skills:
            strengths.extend(soft_skills[:2])
        if matched_keywords:
            strengths.append(f"{len(matched_keywords)} job keywords matched")
        if word_count >= 120:
            strengths.append("Detailed resume content")

        return strengths or ["Readable text extracted"]

    @classmethod
    def _build_ats_tips(
        cls,
        text: str,
        word_count: int,
        missing_sections: list[str],
        technical_skills: list[str],
        missing_keywords: list[str],
    ) -> list[str]:
        """Return ATS tips customized to the resume structure."""
        tips = []

        if missing_sections:
            missing = ", ".join(missing_sections[:3])
            tips.append(f"Use exact section labels for: {missing}.")
        if not cls._has_email(text):
            tips.append("Keep email as selectable text, not inside an image.")
        if not cls._has_phone(text):
            tips.append("Place phone number in a plain-text contact line.")
        if len(technical_skills) < 3:
            tips.append("Create a Skills heading so tools are easy to parse.")
        if missing_keywords:
            keywords = ", ".join(missing_keywords[:3])
            tips.append(f"Mirror exact ATS keywords where truthful: {keywords}.")
        if word_count < 80:
            tips.append("Very short resumes may be parsed as incomplete.")
        elif word_count > 800:
            tips.append("Long resumes may dilute keyword relevance in ATS.")

        tips.append("Avoid tables, columns, icons, and text inside images.")

        return tips[:5]

    @staticmethod
    def _compare_job_keywords(
        resume_text: str,
        job_description: str,
    ) -> tuple[list[str], list[str]]:
        """Compare resume terms against the target job description."""
        if not job_description:
            return [], []

        possible_keywords = TECHNICAL_SKILLS | SOFT_SKILLS
        job_keywords = sorted(
            term
            for term in possible_keywords
            if ResumeAnalyzer._contains_keyword(job_description, term)
        )
        matched = [
            term
            for term in job_keywords
            if ResumeAnalyzer._contains_keyword(resume_text, term)
        ]
        missing = [term for term in job_keywords if term not in matched]

        return matched, missing

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

    @staticmethod
    def _has_measurable_impact(text: str) -> bool:
        """Return True when text includes quantified achievements."""
        pattern = (
            r"(?<![a-zA-Z0-9])\d+(?:\.\d+)?\s*"
            r"(?:%|users|members|projects|hours|seconds|ms|x|times faster)"
            r"(?![a-zA-Z0-9])"
        )
        return bool(re.search(pattern, text, re.IGNORECASE))
