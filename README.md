# Resume Matcher

AI-powered resume review and job description matching. Upload your resume, get instant feedback, and compare it against job postings with match scores, skill gap analysis, and improvement suggestions.

## Features

- **Resume Review** – AI analysis (strengths, weaknesses, suggestions)
- **Job Matching** – Upload resume + job description → match score (0–100), skill gaps, improvement tips
- **Structured Parsing** – Extracts skills, education, experience from resumes
- **Scoring Algorithm** – Hybrid keyword + AI scoring
- **Save History** – Past reviews and match results stored in PostgreSQL
- **Dashboard** – Tabbed UI for Review vs Match modes
- **Proper Architecture** – Config, models, services, routes separation
- **Deployment Ready** – Docker Compose for local/production

## Tech Stack

- **Backend:** FastAPI, Groq (Llama 3.3 70B), SQLAlchemy, PostgreSQL
- **Frontend:** React 19, Vite, Tailwind CSS
- **Future:** Vector embeddings (FAISS), Auth (JWT), pgvector

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- [Groq API key](https://console.groq.com)

### 1. Backend

```bash
cd backend
cp ../.env.example .env
# Edit .env and add your GROQ_API_KEY and DATABASE_URL

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### 3. Docker (full stack)

```bash
# Create .env with GROQ_API_KEY
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint        | Description                    |
|--------|-----------------|--------------------------------|
| POST   | /review-resume  | Upload PDF, get AI review      |
| POST   | /match-resume   | Upload PDF + job desc, get match |
| GET    | /history        | List past reviews              |
| GET    | /match-history  | List past match results        |

## Project Structure

```
├── backend/
│   ├── config.py          # Settings from env
│   ├── main.py            # FastAPI app
│   ├── models/            # DB models
│   ├── routes/            # API routes
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic (parser, AI, matching)
├── frontend/
│   └── src/
│       ├── App.jsx        # Main UI
│       └── lib/api.js     # API client
└── docker-compose.yml
```

## Roadmap

- [x] Proper architecture
- [x] Job matching + scoring
- [x] Skill gap analysis
- [x] Improvement suggestions
- [x] Save history / dashboard
- [x] Docker deployment
- [ ] Vector embeddings (FAISS / pgvector)
- [ ] Auth system (JWT)
- [ ] Public deployment (e.g. Railway, Render)

## License

MIT
