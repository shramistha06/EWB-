from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services.grading import grade_for, risk_for

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    if not students:
        return {"total_students": 0, "message": "No data. Call POST /students/seed/demo"}

    avg_marks = sum(s.marks for s in students) / len(students)
    avg_att = sum(s.attendance for s in students) / len(students)
    topper = max(students, key=lambda s: s.marks)

    by_course = {}
    for s in students:
        by_course.setdefault(s.course, []).append(s.marks)

    return {
        "total_students": len(students),
        "average_marks": round(avg_marks, 1),
        "average_attendance": round(avg_att, 1),
        "topper": {"name": topper.name, "marks": topper.marks, "course": topper.course},
        "grade_distribution": dict(Counter(grade_for(s.marks) for s in students)),
        "risk_distribution": dict(Counter(risk_for(s.marks, s.attendance) for s in students)),
        "course_averages": {c: round(sum(v) / len(v), 1) for c, v in by_course.items()},
        "at_risk_students": [
            {"id": s.id, "name": s.name, "marks": s.marks, "attendance": s.attendance}
            for s in students if risk_for(s.marks, s.attendance) == "High"
        ],
    }


@router.get("/leaderboard")
def leaderboard(top: int = 5, db: Session = Depends(get_db)):
    students = db.query(models.Student).order_by(models.Student.marks.desc()).limit(top).all()
    return [{"rank": i + 1, "name": s.name, "course": s.course, "marks": s.marks}
            for i, s in enumerate(students)]
