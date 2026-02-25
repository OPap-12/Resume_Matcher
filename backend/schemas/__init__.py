"""Pydantic request/response schemas."""
from .resume import (
    ResumeReviewResponse,
    ResumeMatchRequest,
    ResumeMatchResponse,
    StructuredResume,
)
from .common import ErrorResponse

__all__ = [
    "ResumeReviewResponse",
    "ResumeMatchRequest",
    "ResumeMatchResponse",
    "StructuredResume",
    "ErrorResponse",
]
