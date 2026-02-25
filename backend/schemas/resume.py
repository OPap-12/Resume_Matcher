"""Resume-related schemas."""
from pydantic import BaseModel


class StructuredResume(BaseModel):
    """Parsed resume structure."""

    skills: list[str] = []
    education: list[str] = []
    experience: list[str] = []
    summary: str = ""


class ResumeAnalysis(BaseModel):
    """AI analysis output."""

    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []


class ResumeReviewResponse(BaseModel):
    """Response for resume review endpoint."""

    id: int
    filename: str
    analysis: dict
    parsed_resume: dict | None = None


class ResumeMatchRequest(BaseModel):
    """Request body for job matching (job description as text)."""

    job_description: str


class ResumeMatchResponse(BaseModel):
    """Response for resume-job match endpoint."""

    id: int
    filename: str
    match_score: float
    skill_gaps: list[str]
    improvement_suggestions: list[str]
    parsed_resume: dict | None
    analysis: dict | None = None  # strengths, weaknesses from review
