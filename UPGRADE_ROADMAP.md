# Upgrade Roadmap – Resume Matcher

## Completed in This Upgrade

### 1. Proper Architecture
- **config/** – Environment-based settings (`config.py`)
- **models/** – SQLAlchemy models (`ResumeReview`, `JobMatch`)
- **schemas/** – Pydantic request/response models
- **services/** – Business logic: `PdfParser`, `AIService`, `MatchingService`
- **routes/** – API endpoints in separate modules

### 2. Resume + Job Description Matching
- New endpoint: `POST /match-resume` (file + `job_description` form field)
- Returns: match score, skill gaps, improvement suggestions

### 3. Scoring Algorithm
- **Keyword overlap** – Extracts terms from job and resume
- **AI-based score** – Groq LLM evaluates fit
- **Hybrid score** – 30% keywords + 70% AI (configurable)

### 4. Skill Gap Analysis
- LLM extracts skills the job needs but the resume lacks
- Shown in UI with “Skill Gaps” section

### 5. Improvement Suggestions
- Kept for resume review (strengths, weaknesses, suggestions)
- Added for job match (actionable improvements for the target role)

### 6. Dashboard
- Tabbed UI: **Review** vs **Match Job**
- Sidebar with separate history for each mode
- Match score badge (color-coded: green/amber/red)

### 7. Save History
- **Review history** – Past resume reviews
- **Match history** – Past job matches (score, skill gaps, suggestions)
- Stored in PostgreSQL

### 8. Deployment Setup
- `docker-compose.yml` – Backend, frontend, PostgreSQL
- `backend/Dockerfile` – Python/FastAPI
- `frontend/Dockerfile` – Vite build + nginx
- `.env.example` – Required environment variables

---

## Next Steps (Future Phases)

### Phase 3: Vector Embeddings
- Add `sentence-transformers` and `faiss-cpu` to `requirements.txt`
- Set `ENABLE_EMBEDDINGS=true` in env
- Implement semantic search for “find resumes similar to this job”
- Optionally: pgvector for PostgreSQL-based embeddings

### Phase 4: Auth System
- User model and registration
- JWT auth with access/refresh tokens
- Protect routes; associate reviews/matches with users
- Dependencies: `python-jose`, `passlib`, `bcrypt`

### Phase 5: Public Deployment
- Railway / Render / Fly.io for backend + frontend
- Managed PostgreSQL or Supabase
- Set `CORS_ORIGINS` and `DATABASE_URL` for production
- Use HTTPS and strong `SECRET_KEY`

---

## How to Run

**Development:**
```bash
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend (proxies to backend)
cd frontend && npm run dev
```

**Docker:**
```bash
# Ensure .env has GROQ_API_KEY
docker-compose up --build
```
