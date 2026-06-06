import json
import re

from fastapi import HTTPException, status
from groq import Groq

from app.database.mongodb import get_settings
from app.models.ai import JobMatchRequest, JobMatchResponse
from app.security.input_guard import BLOCK_MESSAGE, InputGuardError, validate_ai_input


class AIService:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)
        self.model_name = "llama-3.1-8b-instant"

    @staticmethod
    def _guard_ai_input(text: str) -> str:
        try:
            return validate_ai_input(text)
        except InputGuardError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=BLOCK_MESSAGE,
            ) from exc

    def generate_resume_from_text(self, free_text: str) -> str:
        safe_text = self._guard_ai_input(free_text)
        # Prompt the model to output a clean, professional resume format.
        prompt = (
            "You are an expert resume writer. Transform the following free text into a "
            "professional ATS-friendly resume in markdown format with sections: "
            "Summary, Skills, Experience, Projects, Education.\n\n"
            f"Input:\n{safe_text}"
        )
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return completion.choices[0].message.content or ""

    def match_job(self, payload: JobMatchRequest) -> JobMatchResponse:
        safe_resume = self._guard_ai_input(payload.resume_text)
        safe_job_description = self._guard_ai_input(payload.job_description)
        # Ask the model for structured JSON so scoring can be parsed reliably.
        prompt = (
            "You are a resume-job matching expert. Compare the resume with the job description.\n"
            "Return ONLY valid JSON with keys: similarity_score (0-100 number), tailored_resume "
            "(string), explanation (string). Do not include markdown fences.\n\n"
            f"Resume:\n{safe_resume}\n\nJob Description:\n{safe_job_description}"
        )

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = completion.choices[0].message.content or ""
        cleaned_content = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned_content)
            score = float(parsed.get("similarity_score", 0))
            score = max(0.0, min(score, 100.0))
            tailored_resume = str(parsed.get("tailored_resume", "")).strip()
            explanation = str(parsed.get("explanation", "")).strip()
        except (json.JSONDecodeError, ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI response parsing failed. Try again.",
            ) from None

        return JobMatchResponse(
            similarity_score=score,
            tailored_resume=tailored_resume,
            explanation=explanation,
        )
