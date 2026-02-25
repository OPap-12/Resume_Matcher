"""AI-powered services using Groq LLM."""
import json

from groq import Groq

from config import get_settings


class AIService:
    """Handles all Groq AI calls."""

    def __init__(self):
        settings = get_settings()
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def review_resume(self, resume_text: str) -> dict:
        """Get strengths, weaknesses, suggestions for a resume."""
        chat = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional resume reviewer. Output your analysis strictly in JSON format. "
                        "The JSON should have three keys: 'strengths', 'weaknesses', and 'suggestions'. "
                        "Each key should contain a list of 3 clear, actionable strings."
                    )
                },
                {"role": "user", "content": resume_text},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        return json.loads(chat.choices[0].message.content)

    def parse_resume(self, resume_text: str) -> dict:
        """Extract structured data (skills, education, experience) from resume."""
        chat = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract structured data from the resume. Output strictly in JSON format. "
                        "Keys: 'skills' (list of technical/soft skills), 'education' (list of degrees/certifications), "
                        "'experience' (list of job titles or roles), 'summary' (1-2 sentence professional summary). "
                        "Use empty lists/string if not found. Be concise."
                    )
                },
                {"role": "user", "content": resume_text},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        data = json.loads(chat.choices[0].message.content)
        return {
            "skills": data.get("skills", []) or [],
            "education": data.get("education", []) or [],
            "experience": data.get("experience", []) or [],
            "summary": data.get("summary", "") or "",
        }

    def match_and_analyze(
        self, resume_text: str, parsed_resume: dict, job_description: str
    ) -> dict:
        """
        Compare resume to job description. Returns:
        - match_score (0-100)
        - skill_gaps (missing skills)
        - improvement_suggestions
        """
        skills_str = ", ".join(parsed_resume.get("skills", []) or [])
        prompt = f"""
Resume text (excerpt):
{resume_text[:2000]}

Extracted skills from resume: {skills_str}

Job Description:
{job_description[:2000]}

Analyze the resume against the job description. Output strictly in JSON with:
- "match_score": number 0-100 (how well does the resume match the job)
- "skill_gaps": list of 3-5 key skills/qualifications the job requires but the resume lacks
- "improvement_suggestions": list of 3-5 actionable suggestions to improve the resume for this job
"""
        chat = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume-job matcher. Output only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        result = json.loads(chat.choices[0].message.content)
        return {
            "match_score": float(result.get("match_score", 0)),
            "skill_gaps": result.get("skill_gaps", []) or [],
            "improvement_suggestions": result.get("improvement_suggestions", []) or [],
        }
