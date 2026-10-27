from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.grading import grade_for, risk_for

router = APIRouter(prefix="/students", tags=["Students"])


def to_out(s: models.Student) -> schemas.StudentOut:
    return schemas.StudentOut(
        id=s.id, name=s.name, email=s.email, course=s.course,
        marks=s.marks, attendance=s.attendance, skills=s.skills or "",
        grade=grade_for(s.marks), risk=risk_for(s.marks, s.attendance),
    )


def get_or_404(db: Session, student_id: int) -> models.Student:
    s = db.get(models.Student, student_id)
    if not s:
        raise HTTPException(404, "Student not found")
    return s


@router.post("/", response_model=schemas.StudentOut, status_code=201)
def create_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    if db.query(models.Student).filter_by(email=data.email).first():
        raise HTTPException(400, "Email already registered")
    s = models.Student(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return to_out(s)


@router.get("/", response_model=List[schemas.StudentOut])
def list_students(course: str = None, risk: str = None,
                  db: Session = Depends(get_db)):
    """Optional filters: ?course=Python  &  ?risk=High"""
    q = db.query(models.Student)
    if course:
        q = q.filter(models.Student.course.ilike(f"%{course}%"))
    out = [to_out(s) for s in q.all()]
    if risk:
        out = [o for o in out if o.risk.lower() == risk.lower()]
    return out


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return to_out(get_or_404(db, student_id))


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, data: schemas.StudentUpdate,
                   db: Session = Depends(get_db)):
    s = get_or_404(db, student_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return to_out(s)


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    s = get_or_404(db, student_id)
    db.delete(s)
    db.commit()
    return {"status": "success", "message": f"Student {student_id} deleted"}


@router.post("/seed/demo", tags=["Demo"])
def seed_demo_data(db: Session = Depends(get_db)):
    """Loads 8 sample students so you can test instantly."""
    demo = [
        ("Aarav Sharma", "aarav@demo.com", "Python", 92, 96, "Python, SQL, FastAPI"),
        ("Diya Verma", "diya@demo.com", "Python", 78, 88, "Python, Pandas"),
        ("Rohan Gupta", "rohan@demo.com", "Data Science", 55, 70, "Excel, Basic Python"),
        ("Sneha Singh", "sneha@demo.com", "Data Science", 84, 91, "ML, Statistics, Python"),
        ("Kabir Khan", "kabir@demo.com", "Web Dev", 35, 52, "HTML"),
        ("Isha Patel", "isha@demo.com", "Web Dev", 67, 79, "HTML, CSS, JavaScript"),
        ("Vivaan Mishra", "vivaan@demo.com", "AI & ML", 88, 94, "ML, Deep Learning, Ollama"),
        ("Anaya Joshi", "anaya@demo.com", "AI & ML", 48, 66, "Python"),
    ]
    added = 0
    for n, e, c, m, a, sk in demo:
        if not db.query(models.Student).filter_by(email=e).first():
            db.add(models.Student(name=n, email=e, course=c, marks=m,
                                  attendance=a, skills=sk))
            added += 1
    db.commit()
    return {"status": "success", "added": added}
