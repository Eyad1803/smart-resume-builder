from fastapi import APIRouter

from app.models.ai import (
    JobMatchRequest,
    JobMatchResponse,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])
ai_service = AIService()


@router.post("/generate-resume", response_model=ResumeGenerateResponse)
async def generate_resume(payload: ResumeGenerateRequest) -> ResumeGenerateResponse:
    generated_resume = ai_service.generate_resume_from_text(payload.free_text)
    return ResumeGenerateResponse(generated_resume=generated_resume)


@router.post("/match-job", response_model=JobMatchResponse)
async def match_job(payload: JobMatchRequest) -> JobMatchResponse:
    return ai_service.match_job(payload)
