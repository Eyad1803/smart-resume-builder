# Smart Resume Builder Backend

FastAPI backend for authentication, AI resume generation, and job matching with MongoDB + Groq.

## Setup

1. Create virtual environment and activate it.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` in the project root and fill in values.
4. Start MongoDB (if not already running):
   - `net start MongoDB`
   - or `docker run -d --name mongodb -p 27017:27017 mongo:latest`
5. Run the API server on port **8002**:
   - `uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload`

## Frontend Demo

The single-page demo UI is served by FastAPI at:

**http://127.0.0.1:8002/ui/**

Open that URL in your browser after starting the server.

### Frontend sections

- **Register** — create an account (`email`, `password`, `full_name`)
- **Login** — sign in and store `access_token` in `localStorage`
- **Resume Generator** — submit free text and view `generated_resume`
- **Job Match** — compare resume vs job description, view `similarity_score` and `explanation`

### Full demo flow

1. Open **http://127.0.0.1:8002/ui/**
2. Go to **Register** and create a test account
3. Confirm the success message and JWT stored in browser storage
4. Go to **Login** and sign in with the same credentials
5. Open **Resume Generator**, paste career notes (20+ characters), click **Generate resume**
6. Open **Job Match**, paste a job description, click **Analyze match**
7. Review the similarity score and explanation

API documentation: **http://127.0.0.1:8002/docs**

## API Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /ai/generate-resume`
- `POST /ai/match-job`

## Frontend files

- `frontend/index.html` — SPA shell and layout
- `frontend/css/styles.css` — presentation styles
- `frontend/js/app.js` — forms, API calls, and navigation

## Lab 7 - DevSecOps / GitHub Actions

This project uses GitHub Actions for automated security checks and AI-assisted PR review.

### Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Security Pipeline | `.github/workflows/security_pipeline.yml` | Push/PR to `main` | Runs `pytest test_security_injection.py -v` |
| AI PR Review | `.github/workflows/ai_pr_review.yml` | PR opened/updated | Posts Gemini AI security review as a PR comment |

### Configure `GEMINI_API_KEY`

The AI PR review workflow requires a Gemini API key stored as a GitHub repository secret (never committed to the repo):

1. Open your GitHub repository
2. Go to **Settings → Secrets and variables → Actions → Repository secrets**
3. Click **New repository secret**
4. Name: `GEMINI_API_KEY`
5. Value: your Gemini API key from Google AI Studio

`GITHUB_TOKEN` is provided automatically by GitHub Actions for posting PR comments.

### What fails a PR

- **Security Pipeline** — any failing test in `test_security_injection.py` (e.g., removed input validation)
- **AI PR Review** — if `review.md` contains `VULNERABILITY_FOUND` (e.g., hardcoded secrets or bypassed Filter-Verify pipeline)

Safe PRs receive a comment starting with `SAFE_CODE`.
