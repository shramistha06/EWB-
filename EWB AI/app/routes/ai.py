from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import llm
from .students import get_or_404

router = APIRouter(prefix="/ai", tags=["Local AI (Ollama)"])


@router.post("/ask")
def ask_ai(body: schemas.AskBody, db: Session = Depends(get_db)):
    """Ask anything about your students in plain English."""
    students = db.query(models.Student).all()
    return {"status": "success", "answer": llm.ask(students, body.question)}


@router.get("/mentor-report/{student_id}")
def mentor_report(student_id: int, db: Session = Depends(get_db)):
    """AI-written personal report + 7-day action plan for one student."""
    student = get_or_404(db, student_id)
    all_students = db.query(models.Student).all()
    class_avg = sum(s.marks for s in all_students) / len(all_students)
    return {
        "status": "success",
        "student": student.name,
        "report": llm.mentor_report(student, class_avg),
    }
