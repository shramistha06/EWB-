from typing import Optional
from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str
    email: str
    course: str
    marks: float = Field(0.0, ge=0, le=100)
    attendance: float = Field(0.0, ge=0, le=100)
    skills: str = ""


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    course: Optional[str] = None
    marks: Optional[float] = Field(None, ge=0, le=100)
    attendance: Optional[float] = Field(None, ge=0, le=100)
    skills: Optional[str] = None


class StudentOut(StudentCreate):
    id: int
    grade: str = ""
    risk: str = ""

    class Config:
        from_attributes = True


class AskBody(BaseModel):
    question: str
