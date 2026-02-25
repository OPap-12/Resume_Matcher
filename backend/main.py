"""
Resume Matcher API - FastAPI application.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models.db import SessionLocal, ResumeReview
from routes.resume import router as resume_router
from services.embeddings_service import get_embeddings_service

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
emb_service = get_embeddings_service()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if emb_service:
        logger.info("Initializing vector embeddings (FAISS)...")
        db = SessionLocal()
        try:
            reviews = db.query(ResumeReview).all()
            count = 0
            for r in reviews:
                if hasattr(r, "raw_text") and r.raw_text:
                    emb_service.add_resume(r.id, r.raw_text)
                    count += 1
            logger.info(f"Loaded {count} resumes into FAISS index.")
        except Exception as e:
            logger.error(f"Error loading FAISS: {e}")
        finally:
            db.close()
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}."},
    )

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from routes.auth import router as auth_router

app.include_router(auth_router)
app.include_router(resume_router)

@app.get("/")
def home():
    return {"message": "Resume Matcher API is Running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
