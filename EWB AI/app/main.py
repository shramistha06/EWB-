from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database import Base, engine
from .routes import students, analytics, ai

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EduMentor AI",
    description="Student performance tracker with analytics and an offline "
                "AI mentor powered by Ollama + LangChain.",
    version="2.0",
)

app.include_router(students.router)
app.include_router(analytics.router)
app.include_router(ai.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")
