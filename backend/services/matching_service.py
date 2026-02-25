"""Resume-job matching logic (keyword + AI hybrid)."""
import re


class MatchingService:
    """Computes match score and skill gaps."""

    @staticmethod
    def extract_keywords(text: str) -> set[str]:
        """Extract potential skill/keyword tokens from text."""
        text = text.lower()
        # Remove common noise, keep words 2+ chars
        words = re.findall(r"\b[a-z0-9+.#-]{2,}\b", text)
        return set(words)

    @staticmethod
    def keyword_score(job_keywords: set[str], resume_keywords: set[str]) -> float:
        """Compute overlap score 0-100 based on keyword overlap."""
        if not job_keywords:
            return 0.0
        overlap = len(job_keywords & resume_keywords) / len(job_keywords)
        return min(100, overlap * 100 * 1.2)  # Slight boost

    @staticmethod
    def compute_hybrid_score(
        keyword_score_val: float, ai_score: float, ai_weight: float = 0.7
    ) -> float:
        """Blend keyword score with AI score."""
        return keyword_score_val * (1 - ai_weight) + ai_score * ai_weight
