from pydantic import BaseModel, Field


class ResumeGenerateRequest(BaseModel):
    free_text: str = Field(min_length=20, description="Raw user background and experience.")


class ResumeGenerateResponse(BaseModel):
    generated_resume: str


class JobMatchRequest(BaseModel):
    resume_text: str = Field(min_length=20)
    job_description: str = Field(min_length=20)


class JobMatchResponse(BaseModel):
    similarity_score: float
    tailored_resume: str
    explanation: str
