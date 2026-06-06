from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.mongodb import close_mongo_connection, get_database
from app.routes.ai import router as ai_router
from app.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Open DB on startup by touching the database handle.
    get_database()
    yield
    # Close MongoDB client cleanly on shutdown.
    await close_mongo_connection()


app = FastAPI(
    title="Smart Resume Builder API",
    description="FastAPI backend with MongoDB and Groq AI integrations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(ai_router)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.is_dir():
    app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"message": "Smart Resume Builder API is running."}
