"""Resume and job matching API routes."""
import io

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Request

from sqlalchemy.orm import Session

from models.db import get_db, ResumeReview, JobMatch, User
from services.auth_service import get_current_user
from services.parser import PdfParser
from services.ai_service import AIService
from services.matching_service import MatchingService
from services.embeddings_service import get_embeddings_service
from config import get_settings

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["resume"])
parser = PdfParser()
ai_service = AIService()
matching_service = MatchingService()
emb_service = get_embeddings_service()


def validate_file(file: UploadFile, max_size: int):
    """Validate uploaded file."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")
    # Size will be checked after read


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/review-resume")
@limiter.limit("5/minute")
async def review_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload resume, get AI review (strengths, weaknesses, suggestions)."""
    settings = get_settings()
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(400, f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // 1_000_000}MB")
    validate_file(file, settings.MAX_UPLOAD_SIZE)

    text = parser.extract_text(content)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from PDF")

    try:
        analysis = ai_service.review_resume(text)
        parsed = ai_service.parse_resume(text)
    except Exception as e:
        raise HTTPException(503, f"AI service error: {str(e)}")

    entry = ResumeReview(
        filename=file.filename,
        analysis=analysis,
        parsed_resume=parsed,
        raw_text=text[:5000],
        user_id=current_user.id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    if emb_service:
        try:
            emb_service.add_resume(entry.id, entry.raw_text)
        except Exception:
            pass

    return {
        "id": entry.id,
        "filename": file.filename,
        "analysis": analysis,
        "parsed_resume": parsed,
    }


@router.post("/match-resume")
@limiter.limit("5/minute")
async def match_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload resume + job description, get match score, skill gaps, improvement suggestions.
    Send job_description as form field: job_description=<text>
    """
    settings = get_settings()
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(400, f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // 1_000_000}MB")
    validate_file(file, settings.MAX_UPLOAD_SIZE)

    if not job_description or not job_description.strip():
        raise HTTPException(400, "job_description is required")

    text = parser.extract_text(content)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from PDF")

    try:
        parsed = ai_service.parse_resume(text)
        match_result = ai_service.match_and_analyze(text, parsed, job_description)
    except Exception as e:
        raise HTTPException(503, f"AI service error: {str(e)}")

    job_kw = matching_service.extract_keywords(job_description)
    resume_kw = matching_service.extract_keywords(text)
    for s in parsed.get("skills", []) or []:
        resume_kw.update(s.lower().split())
    kw_score = matching_service.keyword_score(job_kw, resume_kw)
    ai_score = match_result["match_score"]
    final_score = matching_service.compute_hybrid_score(kw_score, ai_score)

    entry = JobMatch(
        filename=file.filename,
        job_description=job_description[:5000],
        match_score=round(final_score, 1),
        skill_gaps=match_result["skill_gaps"],
        improvement_suggestions=match_result["improvement_suggestions"],
        parsed_resume=parsed,
        user_id=current_user.id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "id": entry.id,
        "filename": file.filename,
        "match_score": entry.match_score,
        "skill_gaps": entry.skill_gaps,
        "improvement_suggestions": entry.improvement_suggestions,
        "parsed_resume": parsed,
    }


@router.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all past resume reviews for the user."""
    reviews = db.query(ResumeReview).filter(ResumeReview.user_id == current_user.id).order_by(ResumeReview.timestamp.desc()).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "analysis": r.analysis,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in reviews
    ]


@router.get("/match-history")
def get_match_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all past job match results for the user."""
    matches = db.query(JobMatch).filter(JobMatch.user_id == current_user.id).order_by(JobMatch.timestamp.desc()).all()
    return [
        {
            "id": m.id,
            "filename": m.filename,
            "match_score": m.match_score,
            "skill_gaps": m.skill_gaps,
            "improvement_suggestions": m.improvement_suggestions,
            "parsed_resume": m.parsed_resume,
            "job_description": m.job_description[:200] + "..." if m.job_description and len(m.job_description) > 200 else m.job_description,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
        }
        for m in matches
    ]

@router.get("/search-resumes")
def search_resumes(query: str, top_k: int = 5, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Search resumes by semantic similarity using FAISS."""
    if not emb_service:
        raise HTTPException(status_code=501, detail="Semantic search is disabled. Set ENABLE_EMBEDDINGS=true.")
    
    try:
        results = emb_service.search(query, top_k=top_k * 3) # over-fetch to account for post-filtering
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching vector DB: {str(e)}")
        
    if not results:
        return []
        
    resume_ids = [r["id"] for r in results]
    reviews = db.query(ResumeReview).filter(
        ResumeReview.id.in_(resume_ids),
        ResumeReview.user_id == current_user.id
    ).all()
    
    review_map = {r.id: r for r in reviews}
    
    response = []
    for r in results:
        rev = review_map.get(r["id"])
        if rev:
            response.append({
                "id": rev.id,
                "filename": rev.filename,
                "score": round(r["score"], 4),
                "parsed_resume": rev.parsed_resume,
                "timestamp": rev.timestamp.isoformat() if rev.timestamp else None,
            })
            
    return response
